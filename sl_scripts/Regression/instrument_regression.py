"""
+ ========================================================================================== +
+    Author: Johnny (Shaun) Lowis, for Bodeker Scientific.                                   +
+    Using a multivariate linear regression model to error correct ODIN's and ES642's        +
+    using the Woolston TEOM as a training set.                                              +
+ ========================================================================================== +

"""

import netCDF4 as nc
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from sklearn import metrics
from users.sl_scripts.MAPM.TEOM.plot_hourly_means import plot_data


class MAPMregression:
    """ Class for performing multivariate, linear regression analysis on NetCDF files;
        particularly ODIN and ES642 data, for the MAPM campaign. Trains regression on
        hourly averaged data, using vars in ES642/ODIN for X_train and PM2.5 in TEOM for
        y_train. The data is shaped and alignment of timesteps checked.
    """

    def __init__(self, X_train_fp, y_train_fp, X_variables, plot_minute=False, plot_hours=False,
                 plot_all=False, error_out=False, residuals=False, plot_pm_comparison=False, scale_model=False):
        """ Initialise class attributes:
        :param X_train_fp: Filepath, to ES642/Odin hourly averaged datafile.
        :param y_train_fp: Filepath, to TEOM.
        :param X_variables: List, of variable names in hourly averaged and minute interval devices.
                                              -kwargs**-
        :param plot_minute: Boolean, to plot minute interval linearly regressed y_pred vs TEOM PM2.5.
        :param plot_hours: Boolean, plot hourly averaged 'training' data.
        :param plot_all: Boolean, plot all informatics data.
        :param residuals: Boolean, plot of difference between PM2.5 in training data and regressed PM2.5.
        :param plot_pm_comparison: Boolean, plot of ES642pm on x-axis vs TEOMpm on y-axis.
        :param scale_model: Boolean, whether or not SciKit Learn's StandardScaler normalisation is applied.
        :param error_out: Boolean, for if error between measured and regressed y_pred should be printed."""

        self.X_train_fp = X_train_fp
        self.y_train_fp = y_train_fp
        self.X_variables = X_variables
        self.plot_minute = plot_minute
        self.plot_hours = plot_hours
        self.plot_all = plot_all
        self.error_out = error_out
        self.residuals = residuals
        self.plot_pm_comparison = plot_pm_comparison
        self.scale_model = scale_model
        self._scale_data()

    def __str__(self):
        return str(f'#=================Evaluating instrument {self.name}=================#\n')

    def _process_data(self):
        """ Reads TEOM and hourly averaged instrument data. Checks if timesteps align via np.intersect1d.
            The TEOM pm2.5 and hourly instruments' input variables are then shaped to ensure their intersecting
            times align. The hourly instrument's datavalues are also transposed and returned."""

        with nc.Dataset(self.y_train_fp) as data_TEOM:
            # Converting from integers to datetime.datetime objects.
            teom_time = nc.num2date(data_TEOM.variables["time"][:],
                                    data_TEOM.variables['time'].units)
            teom_pm = data_TEOM.variables['pm2.5'][:]

        with nc.Dataset(self.X_train_fp) as data_642:
            ES642_time = nc.num2date(data_642.variables["time"][:], data_642.variables['time'].units)

            # Check where intersecting timevalues are, thereby accounting for jumps in time.
            time_values, teom_idxs, es642_idxs = np.intersect1d(teom_time, ES642_time, return_indices=True)

            assert time_values.shape != (0,), "No overlapping values between x_train and y_train data. " \
                                              "Regression calculation is not possible."

            # process_vars function retrieves the keys stated in  self.X_train_variables and self.X_test_variables.
            ES642_vars = process_vars(self.X_variables, data_642)

            # Retrieve instrument's name
            try:
                self.name = data_642.sensor_name
            except AttributeError:
                try:
                    self.name = data_642.device_name
                except AttributeError:
                    self.name = data_642.previous_filename
                    self.name = self.name.split('/')
                    self.name = self.name[-1][:11]

        shifted_ES642_vars = []

        # Shaping hourly_averaged instrument's data using time alignment. Time alignment meaning to find common times
        # between TEOM and hourly averaged instrument and using these values. This results in shape consistency in the
        # training data and correct comparison between datavalues between instruments.
        for var in ES642_vars:
            shifted_var = var[es642_idxs]
            shifted_ES642_vars.append(shifted_var)

        # Shaping TEOM data using time alignment.
        shifted_teom_time = teom_time[teom_idxs]
        shifted_teom_pm = teom_pm[teom_idxs]

        # Converting hourly averaged instrument data to Pandas DataFrame and transposing.
        shifted_ES642_vars_df = pd.DataFrame(shifted_ES642_vars)
        transposed_ES642_vars_df = shifted_ES642_vars_df.transpose()

        # Converting TEOM data to DataFrame. This is because SciKitLearn's StandardScaler expects a DataFrame input.
        shifted_teom_pm_df = pd.DataFrame(shifted_teom_pm)

        return shifted_teom_time, transposed_ES642_vars_df, shifted_teom_pm_df

    def _scale_data(self):
        """ Scale data using SciKitLearn's StandardScaler object. The data is fitted, then transformed.
            X_train, y_train and x_scaler are returned as these are needed in self._evaluate()
            Contains analytics and error analysis plots."""

        # Call to self._process_data() to gain timeshifted data.
        shifted_teom_time, transposed_ES642_vars_df, shifted_teom_pm_df = self._process_data()

        # Normalising data. This is because machine learning algorithms perform better on data distributed
        # between a range of 0,1.
        if self.scale_model is True:
            # apply_scaler(data, scale=False, descale=False, scaler=None)
            X_train, self.x_scaler = apply_scaler(transposed_ES642_vars_df, scale=True)
        else:
            X_train = transposed_ES642_vars_df

        # self.y_scaler and self.regressor are class attributes because; self.y_scaler is needed for data delineation,
        # self.regressor is needed to be called later in minute interval data after training on hourly averaged data.
        if self.scale_model is True:
            y_train, self.y_scaler = apply_scaler(shifted_teom_pm_df, scale=True)
        else:
            y_train = shifted_teom_pm_df

        # The regress() function is documented below.
        self.regressor = LinearRegression()
        self.regressor.fit(X_train, y_train)
        y_pred = self.regressor.predict(X_train)

        if self.scale_model is True:
            y_pred_trans = apply_scaler(y_pred, descale=True, scaler=self.y_scaler)
        else:
            y_pred_trans = shifted_teom_pm_df

        # Declare values of coefficients and intercepts, for later access.
        self.coefficients = self.regressor.coef_
        self.intercept = self.regressor.intercept_

        # def plot_data(teom_time, teom_pm, ES642_time, ES642_pm):
        if self.plot_all or self.plot_hours is True:
            plot_data(shifted_teom_time, shifted_teom_pm_df, shifted_teom_time, y_pred_trans, self.name)
            print('Plotted hourly data.')

        # Performance analysis of the fit of the outputted data.
        if self.error_out is True:
            print('Hourly Mean Absolute Error:', metrics.mean_absolute_error(y_train, y_pred))
            print('Hourly Mean Squared Error:', metrics.mean_squared_error(y_train, y_pred))
            print('Hourly Root Mean Squared Error:', np.sqrt(metrics.mean_squared_error(y_train, y_pred)))

        if self.residuals is True:
            residual = shifted_teom_pm_df - y_pred_trans
            for i, var in enumerate(self.X_variables):
                plot_residuals(transposed_ES642_vars_df[i], residual, var, self.name)

        if self.plot_pm_comparison is True:
            plot_pm_comparison(transposed_ES642_vars_df[0], y_pred_trans, shifted_teom_pm_df, self.name)

    def regression_info(self):
        """ Prints the coefficients of the regression equation, along with the intercept and input variables."""
        for i, variable in enumerate(zip(self.coefficients, self.X_variables)):
            print(f'Instrument {str(self.name)}\'s {str(self.X_variables[i])} has a coefficient'
                  f' of {float(self.coefficients[i]):.4f}')
        print(f"The hourly averaged regression intercept is: {self.intercept}\n")

    def evaluate(self, X_test_fp, lasso=False, y_pred_in=None):
        """ Takes in scaled training data and LinearRegression object from hourly averaged runcase in self._scale_data
            and applies the same scaling to the minute interval data. The hourly trained regression model is then
            run on the minute interval data."""

        # Retrieving minute interval data values, converting to a Pandas DataFrame and transposing.
        with nc.Dataset(X_test_fp) as data_X_test:
            X_test_vars = np.array(process_vars(self.X_variables, data_X_test)).T
            data_X_time = nc.num2date(data_X_test.variables["time"][:], data_X_test.variables['time'].units)

        # Create a mask to identify Nan values and remove them.
        nan_mask = np.any(np.isnan(X_test_vars), axis=1)
        X_test_vars_not_nan = X_test_vars[~nan_mask, :]
        # 'Fake' array of NaN values where datavalues exist in X_test_vars.
        result = np.full(nan_mask.shape, np.nan)

        # Perform transformation and regression prediction on removed NaN dataset.
        if self.scale_model is True:
            X_test = self.x_scaler.transform(X_test_vars_not_nan)
        else:
            X_test = X_test_vars_not_nan

        if lasso is False:
            y_pred = self.regressor.predict(X_test)
        else:
            y_pred = y_pred_in

        # Replace the removed NaN values
        result[~nan_mask] = y_pred.reshape(-1)

        # Reverse the transformation on the datavalues, i.e. denormalise the data.
        if self.scale_model is True:
            trans_result = self.y_scaler.inverse_transform(result)
        else:
            trans_result = result

        if self.plot_all or self.plot_minute:
            plot_data(data_X_time, X_test_vars.T[0], data_X_time, trans_result, self.name)

        return trans_result


def apply_scaler(data, scale=False, descale=False, scaler=None):
    """ Initialises a SciKit Learn StandardScaler to normalise data with. This function can also descale data
        if a StandardScaler object is passed. When scaling is performed, the scaler and scaled data is returned.
        If a scaler is passed and scale is True, the input data will be scaled using the inputted scaler and returned.
        :param data: Input data to be scaled
        :param scale: Boolean, if True data is scaled.
        :param descale: Boolean, if True, data is descaled.
        :param scaler: Boolean, if data is descaled, this StandardScaler object should be passed in."""

    if scale is True:
        data_scaler = preprocessing.StandardScaler()
        data_scaler.fit(data)
        return data_scaler.transform(data), data_scaler

    elif scale is True and scaler:
        scaler.fit(data)
        return scaler.transform(data)

    if descale is True:
        return scaler.inverse_transform(data)


def process_vars(vars_in, data):
    """ Reads the list of variable keys. If any of the keys contain '**' characters, the datavalue within is
        squared and appended to the list of instrument datavalues."""

    outlist = []

    for key in vars_in:
        if "**" in key.strip():
            key = key[:key.index("**")].strip()
            ES642_var = data.variables[key][:].filled(np.nan)
            outlist.append(ES642_var ** 2)
        else:
            ES642_var = data.variables[key][:].filled(np.nan)
            outlist.append(ES642_var)

    return outlist


def plot_residuals(variable, residual, varname, instrument_name):
    plt.rcParams["figure.figsize"] = (12, 8)
    plt.scatter(variable, residual, color='blue')
    plt.title(f'PM2.5 vs. variable', fontsize=14)
    plt.xlabel(f'{instrument_name}: {varname}')
    plt.ylabel(f'Residual PM2.5')
    plt.tight_layout()

    plt.show()


def plot_pm_comparison(instrument_pm_before, instrument_pm_after, TEOM_pm, instrument_name):
    plt.rcParams["figure.figsize"] = (12, 8)
    before = plt.scatter(TEOM_pm, instrument_pm_before, color='red')
    after = plt.scatter(TEOM_pm, instrument_pm_after, color='blue')
    plt.plot(TEOM_pm, TEOM_pm, color='black')
    plt.title('Comparison plot of TEOM PM2.5 vs ES642 PM2.5')
    plt.xlabel(f'{instrument_name} PM2.5')
    plt.ylabel('TEOM PM2.5')
    labels = ['PM2.5 before regression', f'PM2.5 after regression']
    plt.legend((before, after), labels=labels)
    plt.tight_layout()
    plt.show()


def main():
    print(__doc__)
    # fp_TEOM = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/TEOM/Colocation_1/Raw/NetCDF" \
    #           r"/TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc"

    # ----------------------------------- EXAMPLE USING ES642 ---------------------------------------------------- #
    # fp_642_colocation = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Colocation_1/" \
    #                     r"Averaged/NetCDF/ES-642_DM1_Christchurch2019_Colocation_1_averaged.nc"
    # fp_642_deployment = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Deployment/Raw/NetCDF/" \
    #                     r"ES-642_DM1_Christchurch2019_Deployment_raw.nc"

    # The keys should be initialised as a list, with PM2.5 being its first element.
    # ES642_keys = ['pm2.5', 'air_pressure', 'air_temperature', 'relative_humidity']
    # ES642_regress = MAPMregression(fp_642_colocation, fp_TEOM, ES642_keys,
    #                                error_out=False, plot_pm_comparison=True, residuals=False)

    # This last line returns the shaped pm. This is done by:
    # regressed_ES642_pm = ES642_regress.evaluate(fp_642_deployment, plot=False)
    # ES642_regress.evaluate(fp_642_deployment)
    # ES642_regress.regression_info()

    # ----------------------------------- EXAMPLE USING ODIN ----------------------------------------------------- #
    # fp_ODIN_colocation = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Colocation_1/Averaged/NetCDF/" \
    #                      r"ODIN_SD0006_Christchurch2019_Colocation1_averaged.nc"
    # fp_ODIN_deployment = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Deployment/Raw/NetCDF/" \
    #                      r"ODIN_SD0006_Christchurch2019_Deployment_raw.nc"
    #
    # # The keys should be initialised as a list, with PM2.5 being its first element.
    # ODIN_keys = ['PM2.5', 'PM1', 'PM10', 'temperature', 'Relative humidity']
    # ODIN_regress = MAPMregression(fp_ODIN_colocation, fp_TEOM, ODIN_keys, error_out=False, scale_model=False,
    #                               plot_hours=True, plot_minute=True)

    # This last line returns the shaped pm. This is done by:
    # regressed_ODIN_pm = ODIN_regress.evaluate(fp_ODIN_deployment, plot=False)
    # ODIN_regress.evaluate(fp_ODIN_deployment)
    # ODIN_regress.regression_info()

    # ----------------------------------- EXAMPLE USING LOCAL DIR ------------------------------------------------ #
    local_dir = r'/home/slowis/Documents/wrkdir/'
    local_642_colocation = local_dir + r'ES-642_DM1_Christchurch2019_Colocation_1_averaged.nc'
    local_642_deployment = local_dir + r'ES-642_DM1_Christchurch2019_Deployment_raw.nc'
    local_TEOM = local_dir + r'TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc'
    local_ES642_keys = ['pm2.5', 'air_pressure', 'air_temperature', 'relative_humidity']
    local_ES642_regress = MAPMregression(local_642_colocation, local_TEOM, local_ES642_keys, error_out=False,
                                         scale_model=False,
                                  plot_hours=True, plot_minute=True)
    local_ES642_regress.evaluate(local_642_deployment)

    # ----------------------------------------- NOTES ------------------------------------------------------------ #
    # 'PM2.5' should be the first variable in the key lists.
    # The key lists may contain different elements, but both should be the same length.
    # This is to avoid shape conflicts.
    # These key issues are due to a lack of uniformity between the NetCDF files for the TEOM, ODIN and ES642
    # instruments. This may be fixed at a later date.
    # The variables need to be in the same order.


if __name__ == '__main__':
    main()
