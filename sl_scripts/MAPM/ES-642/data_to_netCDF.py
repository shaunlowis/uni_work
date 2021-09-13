""" Script to change the ES_642.csv data files to netCDF4 format
    The function "load_es642_data" was provided by Leroy Bird, and has been adapted for this script.
    Author: Shaun Lowis, for Bodeker Scientific
"""

import glob
import netCDF4
import pandas as pd
from os.path import join
from netCDF4 import Dataset


def load_es642_data(input_folder, serials, sep):
    """
    Loads ES_642 data frames into
    :param input_folder:
    :param serials: List of the serial numbers - these should match the file names without the .txt
    :param sep: the input file separator
    :return:
    """
    df_dict = {}

    for ser in serials:
        all_files = sorted(glob.glob(join(input_folder, ser + '*.txt')))

        if len(all_files) > 0:
            df_all = None
            for target_file in all_files:
                if ser[0:3] == 'DM_':
                    df_p = pd.read_csv(target_file, sep=sep, parse_dates=['Date_Time'], skiprows=6,
                                       names=['Date_Time', 'PM2.5', 'Flow', 'Temp'])
                else:
                    assert ser[0:3] == 'DMM'
                    df_p = pd.read_csv(target_file, sep=sep, parse_dates=['Date_Time'], skiprows=6,
                                       names=['Date_Time', 'PM2.5', 'Flow', 'WindDir', 'WindSpeed', 'Temp'])

                if df_all is None:
                    df_all = df_p
                else:
                    df_all.append(df_p, ignore_index=True)

            df_dict[ser] = df_all
        else:
            print('Could not find: ', ser)

    return df_dict


def gen_netcdf(data, dataset, time, latitude, longitude, serial):
    """ Generates a netCDF file template that can be added to, for the ES_642 instruments.
    :param data: This corresponds to the pandas dataframe of the CSV file.
    :param dataset: The converted netCDF object of the above data.
    :param time: Parameter defined in "df_dict_to_netcdf" function
    :param latitude: Parameter defined in "df_dict_to_netcdf" function
    :param longitude: Parameter defined in "df_dict_to_netcdf" function
    :param serial: The serial number of the ES_642 instrument used to iterate through the dictionary.
    :return: The variables for the target netCDF file. Note there is no .close() argument, this is to
             allow the user to add more variables and dimensions as under the "else:" branch in "df_dict_to_netcdf".
    """

    # Creating the dimensions of the netCDF file
    dataset.createDimension('Time', len(time))
    dataset.createDimension('Latitude', len(latitude))
    dataset.createDimension('Longitude', len(longitude))

    # Creating/declaring the variables of the netCDF file
    timevar64 = dataset.createVariable(varname='Time', dimensions=('Time',),
                                       datatype='float64')
    pm_v = dataset.createVariable('PM2.5', "f4", ("Time",))
    flow_v = dataset.createVariable('Flow', "f4", ("Time",))
    temp_v = dataset.createVariable('Temp', "f4", ("Time",))
    lat_v = dataset.createVariable('Latitude', "f4", ("Latitude",))
    lon_v = dataset.createVariable('Longitude', "f4", ("Longitude",))

    # Values for initialasing time
    calendar = 'gregorian'
    units = 'seconds since 2000-01-01 00:00'

    # Adding data values to the created variables
    timevar64[:] = netCDF4.date2num(time, units=units, calendar=calendar)
    pm_v[:] = data["PM2.5"].values
    flow_v[:] = data["Flow"].values
    temp_v[:] = data["Temp"].values
    lat_v[:] = latitude
    lon_v[:] = longitude

    # Attributes for variables and dimensions
    # Global
    dataset.serial = serial
    dataset.institution = "Bodeker Scientific"
    dataset.project = "{} ES_642 operating from June to August 2019 during " \
                      "the MAPM Campaign (Mapping Air Pollution Emmisions) by Bodeker Scientific".format(serial)
    dataset.source = "Met One Instruments, Inc. model ES_642"
    dataset.weight = "2.7 kg (6 lbs)"
    dataset.unit_dimensions_with_inlet = "48.3cm high, 17.8cm wide, 10.8cm deep."
    dataset.unit_dimensions_without_inlet = "25.4cm high, 17.8cm wide, 10.8cm deep."
    dataset.calibration = "Automatic Zero Calibration every hour or as programmed from 1 to 999 minutes."
    dataset.measurement_range = "0 to 100 mg/m^3 (0 to 100,000 microg/m^3 )"
    dataset.measurement_sensitivity = ".001 mg/m^3 ."

    # Temperature
    temp_v.standard_name = "Temperature"
    temp_v.long_name = "Temperature within ES_642 unit"
    temp_v.unit = "C"
    temp_v.unit_long = "Celsius"
    temp_v.source = "ES_642, Ambient Temperature Sensor Range -30 to +50°C"

    # Time
    timevar64.standard_name = "Time"
    timevar64.units = units
    timevar64.source = "ES_642 sensor"
    timevar64.long_name = units
    timevar64.calendar = calendar

    # Flow
    flow_v.standard_name = "Flow Rate"
    flow_v.source = "Brushless Diaphragm (20,000 hour)."
    flow_v.unit = "lpm"
    flow_v.units_long = "2.0 liters/minute ± 0.1 lpm"
    flow_v.long_name = "Volumetric flow rate"

    # PM2.5
    pm_v.standard_name = "PM2.5"
    pm_v.source = "Particulate concentration by forward light scatter laser Nephelometer."
    pm_v.unit = "10^-6 g/m^3"
    pm_v.units_long = "2.5 micron particulate matter concentration"
    pm_v.long_name = "Instantaneous mass concentration of PM2.5 ambient aerosol particles in air"

    # Latitude
    lat_v.standard_name = "Latitude"
    lat_v.units = "Degrees North"

    # Longitude
    lon_v.standard_name = "Longitude"
    lon_v.units = "Degrees East"


def df_dict_to_netcdf(df_dict, output_fname, serial):
    """
    Converts the output dictionary from "load_es642_data" to a netCDF file
    :param df_dict: takes in the output from "load_es642_data", a pandas dataframe object.
    :param output_fname: Location for the output netCDF file.
    :param serial: Takes in which serial to be created per the dataframe output. This should be a string.
    :return: returns a netCDF file at "output_fname"
    """

    dm_01 = df_dict[serial]
    temp642 = Dataset(output_fname, 'w', format='NETCDF4')

    filepath_csv = r"/home/shaun/Documents/ES-642_updated/MAPM measurement sites - Sites.csv"

    # The headers below are the values that the user wants to keep. It is worth noting that if different variables
    # are to be implemented, the "createDimension" and "createVariable" lines would need to be updated with the
    # changed variable names.

    headers = ["Latitude", "Longitude", "ID"]
    data_csv = csv_data_scrub(filepath_csv, headers)

    time = pd.to_datetime(dm_01["Date_Time"]).astype('O')

    # Loading in data values for the variables. These would need to be changed if different variables are to be used
    latitude = data_csv[data_csv['ID'] == serial]['Latitude'].values
    longitude = data_csv[data_csv['ID'] == serial]['Longitude'].values

    if serial[0:3] == "DM_":
        # Creates variables and dimensions as per gen_netcdf function
        gen_netcdf(dm_01, temp642, time, latitude, longitude, serial)

        print("Finished construction of netCDF file for {}".format(serial))
        temp642.close()

    else:
        # Creates variables and dimensions as per gen_netcdf function
        gen_netcdf(dm_01, temp642, time, latitude, longitude, serial)

        # Adding additional variable values for the wind readings if serial starts with "DMM"
        wind_dir_v = temp642.createVariable('Wind_direction', "f4", ("Time",))
        wind_speed_v = temp642.createVariable('Wind_speed', "f4", ("Time",))

        # Adding values to the additional variables
        wind_dir_v[:] = dm_01["WindDir"].values
        wind_speed_v[:] = dm_01["WindSpeed"].values

        # Adding units to wind variables
        # Wind Direction
        wind_dir_v.standard_name = "Wind Direction"
        wind_dir_v.source = "TSP Inlet Standard, sharp-cut cyclone inlets."
        wind_dir_v.unit = "deg"
        wind_dir_v.units_long = "Degrees"

        # Wind Speed
        wind_speed_v.standard_name = "Wind Speed"
        wind_speed_v.source = "TSP Inlet Standard, sharp-cut cyclone inlets."
        wind_speed_v.unit = "ms"
        wind_speed_v.units_long = "Metres per second."

        print("Finished construction of netCDF file for {}".format(serial))
        temp642.close()


def csv_data_scrub(filepath, headers):
    """
    Loads the csv_datafile in, allows user to remove unnecessary header columns.
    :param filepath: the path to the .csv file
    :param headers: list of headers(str) to be removed
    :return: returns the data from the csv in a pandas dataframe with the headers removed.
    """
    data = pd.read_csv(filepath)
    columns = list(data.columns.values)
    for header in columns:
        if header not in headers:
            del data[header]
    return data


def main():
    """ This main function is used to iterate through a given amount of serials.
        serials correspond to the datafile names, and produces netCDF files via "df_dict_to_netcdf".
        Different files can be converted by changing the values of folder_path and serials. A function
        for generating a serial list automatically is pending.
    :return: The processed netCDF files at the given folder_path.
    """
    # The destination path for where the files will be outputted to:
    folder_path = r"/home/shaun/Documents/ES-642_updated/All/"

    # The prefixes for the ES_642 files. This can be automated at a later version.
    serials = ["DM_01", "DM_02", "DM_03", "DM_04", "DM_05", "DM_06", "DM_07", "DM_08", "DM_09",
               "DMM_02", "DMM_03", "DMM_04", "DMM_05", "DMM_06"]

    # Load a dictionary of dataframes from the datafiles
    es642_data = load_es642_data(folder_path, serials, ";")

    # Loops through the serials and processes the files individually.
    for serial in serials:
        output_fname = r"/home/shaun/Documents/ES-642_updated/Raw/{}_raw.nc".format(serial)
        df_dict_to_netcdf(es642_data, output_fname, serial)

    outfile = r"/home/shaun/Documents/ES-642_updated/Raw/"

    print("Conversion finished. \nFinished files are located at: {}".format(outfile))


main()
