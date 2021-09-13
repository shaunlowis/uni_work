"""
   Script for processing the pm values to be averages, and scaling the time values accordingly.
   Author: Shaun Lowis, for Bodeker Scientific
"""

import netCDF4 as nc
import numpy as np


def avg_netcdf(input_file, avg_hours=1):

    with nc.Dataset(input_file) as nc_ds:
        pm = nc_ds['PM2.5'][:]
        times = nc.num2date(nc_ds['Time'][:], units=nc_ds['Time'].units).astype('datetime64[s]')

    min_date = np.min(times)
    max_date = np.max(times)

    hourly_dts = np.arange(min_date, max_date + np.timedelta64(2*avg_hours, 'h'), np.timedelta64(avg_hours, 'h'))
    hourly_mean = []
    final_dts = []

    for n, curr_dt in enumerate(hourly_dts[0:-1]):
        next_dt = hourly_dts[n + 1]
        mask = (times >= curr_dt) & (times < next_dt)

        if mask.sum() > avg_hours*60*0.5:
            mean = np.nanmean(pm[mask])
        else:
            mean = np.nan

        hourly_mean.append(mean)
        final_dts.append(curr_dt)

    hr_mean = np.array(hourly_mean)
    fin_dts = np.array(final_dts)

    return hr_mean, fin_dts


def load_netcdf(input_path, output_path, hourly_mean, final_dts):
    """

    :param input_path: path to input netCDF file
    :param output_path: path to output destination
    :param hourly_mean: var input
    :param final_dts: var input
    :return: creates new netCDF file
    """
    tempin = nc.Dataset(input_path, 'r')
    tempout = nc.Dataset(output_path, 'w')

    tempout.createDimension('Time', len(hourly_mean))
    tempout.createDimension('Latitude', 1)
    tempout.createDimension('Longitude', 1)

    time_v = tempout.createVariable(varname='Time', dimensions=('Time',),
                                    datatype='float64')
    pm_v = tempout.createVariable('PM2.5', "f4", ("Time",))
    lat_v = tempout.createVariable('Latitude', "f4", ("Latitude",))
    lon_v = tempout.createVariable('Longitude', "f4", ("Longitude",))

    calendar = 'gregorian'
    units = 'seconds since 2000-01-01 00:00'

    final_dts = final_dts.astype('O')
    time_v[:] = nc.date2num(final_dts, units=units, calendar=calendar)
    time_v.units = units
    pm_v[:] = hourly_mean
    lat_v[:] = tempin['Latitude'][:]
    lon_v[:] = tempin['Longitude'][:]

    pm_v.units = "micrograms per metre cubed"

    tempin.close()
    tempout.close()


def main():

    serials = ["DM_01", "DM_02", "DM_03", "DM_04", "DM_05", "DM_06", "DM_07", "DM_08", "DM_09",
               "DMM_02", "DMM_03", "DMM_04", "DMM_05", "DMM_06"]
    for serial in serials:
        input_path = r"/home/shaun/Documents/ES-642_updated/Raw/{}_raw.nc".format(serial)
        output_path = r"/home/shaun/Documents/ES-642_updated/Raw_Averaged/{}_raw_mean.nc".format(serial)
        hourly_mean, final_dts = avg_netcdf(input_path)
        load_netcdf(input_path, output_path, hourly_mean, final_dts)

    output_dest = r"/home/shaun/Documents/ES-642_updated/Raw_Averaged/"
    print("Done with conversion, target directory is: {}".format(output_dest))


main()
