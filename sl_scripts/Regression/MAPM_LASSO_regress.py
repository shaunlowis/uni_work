"""
+ ===================================================================================== +
+    Author: Johnny (Shaun) Lowis, for Bodeker Scientific.                              +
+    Using a LASSO regression model to error correct ODIN's and ES642's                 +
+    using the Woolston TEOM as a training set, comparing this to Linear Regression     +
+    as used in instrument_regression.py, to avoid negative outputs from model.         +
+ ===================================================================================== +

"""

import numpy as np
import netCDF4 as nc
from sklearn import metrics
from sklearn.linear_model import Lasso
from users.sl_scripts.Regression.instrument_regression import MAPMregression
from users.sl_scripts.Regression.instrument_regression import process_vars
from users.sl_scripts.MAPM.TEOM.plot_hourly_means import plot_data
from users.sl_scripts.Regression.instrument_regression import apply_scaler


class MAPMLASSO(MAPMregression):
    """ Child class of MAPMregression, using Lasso regression in stead of Linear regression."""

    def __init__(self, X_train_fp, y_train_fp, X_variables, **kwargs):
        """ Inheriting attributes and methods of MAPMregression class"""
        super().__init__(X_train_fp, y_train_fp, X_variables, **kwargs)

    def _scale_data(self):
        shifted_teom_time, transposed_ES642_vars_df, shifted_teom_pm_df = self._process_data()

        if self.scale_model is True:
            # apply_scaler(data, scale=False, descale=False, scaler=None)
            X_train, self.x_scaler = apply_scaler(transposed_ES642_vars_df, scale=True)
        else:
            X_train = transposed_ES642_vars_df

        nan_mask = np.any(np.isnan(X_train), axis=1)
        X_test_vars_not_nan = X_train[~nan_mask, :]
        result = np.full(nan_mask.shape, np.nan)
        self.model_lasso = Lasso(alpha=0.001, fit_intercept=False, positive=True)
        self.model_lasso.fit(X_test_vars_not_nan, shifted_teom_pm_df)
        y_pred = self.model_lasso.predict(X_test_vars_not_nan)
        result[~nan_mask] = y_pred.reshape(-1)

        self.coefficients = self.model_lasso.coef_
        self.intercept = self.model_lasso.intercept_

        if self.error_out:
            self.error_metrics = {
                # Hourly Mean Absolute
                'hr_mean_abs': metrics.mean_absolute_error(shifted_teom_pm_df, y_pred),
                # Hourly Mean Square
                'hr_mean_sq': metrics.mean_squared_error(shifted_teom_pm_df, y_pred),
                # Hourly Mean Square Root
                'hr_mean_sq_root': np.sqrt(metrics.mean_squared_error(shifted_teom_pm_df, y_pred)),
                # Explained Variation Score (best score is 1)
                'exp_var_score': metrics.explained_variance_score(shifted_teom_pm_df, y_pred),
                # Max Residual
                'max_res': metrics.max_error(shifted_teom_pm_df, y_pred),
            }

        if self.plot_all or self.plot_hours is True:
            plot_data(shifted_teom_time, shifted_teom_pm_df, shifted_teom_time, result, self.name)
            print('Plotted hourly data.')

    def eval_lasso(self, X_test_fp):
        with nc.Dataset(X_test_fp) as data_X_test:
            X_test_vars = np.array(process_vars(self.X_variables, data_X_test)).T

        nan_mask = np.any(np.isnan(X_test_vars), axis=1)
        X_test_vars_not_nan = X_test_vars[~nan_mask, :]
        y_pred = self.model_lasso.predict(X_test_vars_not_nan)
        result = self.evaluate(X_test_fp, lasso=True, y_pred_in=y_pred)

        return result


def main():
    print(__doc__)
    # fp_TEOM = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/TEOM/Colocation_1/Raw/NetCDF" \
    #           r"/TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc"

    # ----------------------------------- EXAMPLE USING ES642 ---------------------------------------------------- #
    # fp_642_colocation = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Colocation_1/Averaged/NetCDF/ES" \
    #                     r"-642_DM1_Christchurch2019_Colocation_1_averaged.nc"
    # ES642_deployment = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Deployment/Raw/NetCDF/" \
    #                    r"ES-642_DM1_Christchurch2019_Deployment_raw.nc"
    # ES642_keys = ['pm2.5', 'air_pressure', 'air_temperature', 'relative_humidity', 'pm2.5 ** 2', 'air_pressure **2']
    # Lasso_ES642 = MAPMLASSO(fp_642_colocation, fp_TEOM, ES642_keys, plot_minute=False, plot_hours=True, scale_model=True)
    # print(Lasso_ES642)
    # Lasso_ES642.eval_lasso(ES642_deployment)
    # Lasso_ES642.regression_info()

    # ----------------------------------- EXAMPLE USING LOCAL DIR ------------------------------------------------ #
    local_dir = r'/home/slowis/Documents/wrkdir/'
    local_642_colocation = local_dir + r'ES-642_DM1_Christchurch2019_Colocation_1_averaged.nc'
    local_642_deployment = local_dir + r'ES-642_DM1_Christchurch2019_Deployment_raw.nc'
    local_TEOM = local_dir + r'TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc'
    local_ES642_keys = ['pm2.5', 'air_pressure', 'air_temperature', 'relative_humidity']
    Lasso_ES642 = MAPMLASSO(local_642_colocation, local_TEOM, local_ES642_keys, plot_minute=False, plot_hours=True,
                            scale_model=True)
    print(Lasso_ES642)
    Lasso_ES642.eval_lasso(local_642_deployment)
    Lasso_ES642.regression_info()

    # ----------------------------------- EXAMPLE USING ODIN ----------------------------------------------------- #
    # fp_ODIN_colocation = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Colocation_1/Averaged/NetCDF/" \
    #                      r"ODIN_SD0006_Christchurch2019_Colocation1_averaged.nc"
    # fp_ODIN_deployment = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Deployment/Raw/NetCDF/" \
    #                      r"ODIN_SD0006_Christchurch2019_Deployment_raw.nc"
    # ODIN_keys = ['PM2.5', 'PM1', 'PM10', 'temperature', 'Relative humidity']
    # Lasso_ODIN = MAPMLASSO(fp_ODIN_colocation, fp_TEOM, ODIN_keys)
    # print(Lasso_ODIN)
    # Lasso_ODIN.eval_lasso(fp_ODIN_deployment)
    # Lasso_ODIN.regression_info()


if __name__ == '__main__':
    main()
