""" Script for producing comparison plots of two FLEXPART-WRF model runs.
    the Confluence writeup is here:
    https://confluence.bodekerscientific.com/display/MAPM/Comparison+plotter+of+FLEXPART-WRF+runs
    written by Shaun Lowis for the MAPM project, Bodeker Scientific.
"""

import os
import numpy as np
import netCDF4 as nc
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize


def plot_out(reference_netCDF, comparison_netCDF, outdir_loc, dates_file, ref_header_fp, comp_header_fp,
             plot_all_parcels=False):
    """ Script to generate plots of comparison and reference netCDFs from FLEXPART output/ dir.
        Before the script can run, error checks are performed on the inputted files. See the docstring for the
        error_check function for more information.
    :param reference_netCDF: The NetCDF file to be plotted on the left hand side of the comparison plots.
    :param comparison_netCDF: The NetCDF file to be plotted on the right hand side of the comparison plots.
    :param outdir_loc: Location where comparison plots will be stored.
    :param dates_file: txt file of dates of the FLEXPART timesteps.
    :param ref_header_fp: Filepath to the reference header NetCDF file, containing information on the latitude,
                          longitude and number of releases.
    :param comp_header_fp: Filepath to the reference header NetCDF file, containing information on the latitude,
                           longitude and number of releases.
                                                    -**kwargs-
    :param plot_all_parcels: Here the user can dictate whether they want to plot all of the releases in the
                             FLEXPART-WRF output, or just parcel 0 by default.
    :return: A directory for every level, and n number of plots inside the directory, where n = number of timesteps.
    """
    # Perform error check before the functions can be compared:
    # error_check(reference_data, ref_dates, ref_header, comparison_data, comp_dates, comp_header)
    error_check(reference_netCDF, dates_file, ref_header_fp, comparison_netCDF, dates_file, comp_header_fp)
    # Change current working directory to the output directory location, 'outdir_loc':
    os.chdir(outdir_loc)
    # Check and print the current working directory:
    cwd = os.getcwd()
    print(f'Directory for outputted files: {cwd}\n')
    # Opening the reference NetCDF dataset using NetCDF4:
    with nc.Dataset(reference_netCDF, 'r') as ref:
        # Loading the time values from the date file as a numpy array:
        times = np.loadtxt(dates_file)
        # Iterating from 0 to the length of the bottom_top attribute:

        for i in range(0, ref.__getattribute__('BOTTOM-TOP_GRID_DIMENSION')):
            # Creating an output directory for each level, here the levels should be the same in the reference
            # and comparison header files, so I have used the reference header arbitrarily:
            header_dataset = nc.Dataset(ref_header_fp)
            height = header_dataset.variables['ZTOP'][i]
            level = os.path.join(outdir_loc, str(height))

            if not os.path.exists(level):
                os.mkdir(level)

            # Iterating through each time value and plotting x = 'west_east' and y = 'south_north'
            # at that time value and saving the figure.

            for n, time in enumerate(times):
                time_str = str(time)
                formatted_time = time_str[0:4] + '-' + time_str[4:6] + '-' + time_str[6:8] + '-' + time_str[8:10] \
                                               + '-' + time_str[10:12]

                savedir = os.path.join(str(level), str(formatted_time) + '.png')

                # Set plot_all_parcels to True when calling the function if desired:
                if plot_all_parcels:
                    for j in range(0, len(ref.variables['CONC'][0, 0, 0, :, 0, 0, 0])):
                        plot_parcels(reference_netCDF, comparison_netCDF, i, n, j, i, formatted_time,
                                     savedir, ref_header_fp, comp_header_fp)
                else:
                    release_num = 0
                    plot_parcels(reference_netCDF, comparison_netCDF, i, n, release_num, i, formatted_time,
                                 savedir, ref_header_fp, comp_header_fp)

    print('Finished generating plots\n')


def plot_parcels(reference_data, comparison_data, bottom_top_count, times_count, release_count,
                 level, time, savedir, reference_header, comparison_header):
    """ Takes in the header file, the merged file and creates a comparison plot. For now, since no
            comparison exists, the merged file has just been used for both plots. This is easy changed
            when another FLEXPART-WRF run is done.

        :param reference_data: NetCDF file containing data on the CONC variable of the FLEXPART run. This data
                               will be plotted on the left hand side of the comparison plots.
        :param comparison_data: NetCDF file containing data on the CONC variable of the FLEXPART run. This data
                                will be plotted on the right hand side of the comparison plots.
        :param bottom_top_count: Used for iteration, this is at what bottom_top value the data is being plotted at.
        :param times_count: Used for iteration, this is at what bottom_top value the data is being plotted at.
        :param release_count: Used for iteration, this is at what parcel is being plotted.
        :param level: Used for iteration, this is at what level value the data is being plotted at.
        :param time: Used for iteration, this is at what time value the data is being plotted at.
        :param savedir: Output location for plots.
        :param reference_header: The reference run's header file.
        :param comparison_header: The comparison run's header file.
        :return: A contour plot of latitude vs longitude of the concentration of a trace parcel of cesium.
        """
    # Retrieving data from the header, merged data files. The comparison dataset here is just the reference dataset
    # again, but can be replaced by another FLEXPART run once we have the necessary data.
    ref_header_dataset = nc.Dataset(reference_header)
    comp_header_dataset = nc.Dataset(comparison_header)
    reference_dataset = nc.Dataset(reference_data)
    comparison_dataset = nc.Dataset(comparison_data)

    ref_lons = ref_header_dataset["XLONG"][:]
    ref_lats = ref_header_dataset["XLAT"][:]

    comp_lons = comp_header_dataset["XLONG"][:]
    comp_lats = comp_header_dataset["XLAT"][:]

    ref_conc = reference_dataset["CONC"]
    comp_conc = comparison_dataset['CONC']

    # Here array indexing is used to find the concentration value at a specified location in the 7D array;
    # where the dimensions of the array are: record, Time, ageclass, releases, bottom_top, south_north, west_east
    ref_conc = ref_conc[times_count, 0, 0, release_count, bottom_top_count, :, :]
    comp_conc = comp_conc[times_count, 0, 0, release_count, bottom_top_count, :, :]

    # Creating a custom colormap to use for the plots:
    colours = ['white', 'blue']
    cmap = LinearSegmentedColormap.from_list("white_blue_lin_seg", colours)

    # Creating the comparison plots, here ax is the background, ax1 the left hand plot and ax2 the right hand plot.
    # Where the LHS plot = reference FLEXPART run and RHS plot = comparison FLEXPART run.
    # Here I manually declare the axes which will have the actual data:
    fig = plt.figure(figsize=(11, 9))
    ax = fig.add_subplot(111)
    ax1 = fig.add_axes([0.1, 0.111, 0.325, 0.769])
    ax2 = fig.add_axes([0.55, 0.111, 0.325, 0.769])

    # Here the two colorbar axes are defined and positioned:
    ref_cb_ax = fig.add_axes([0.45, 0.111, 0.02, 0.769])
    conc_cb_ax = fig.add_axes([0.9, 0.111, 0.02, 0.769])

    # Adding the data to the two axes:
    ax1.contourf(ref_lons, ref_lats, ref_conc.filled(0), cmap=cmap)
    ax2.contourf(comp_lons, comp_lats, comp_conc.filled(0), cmap=cmap)

    # Here I normalize the data so the colorbars are scaled correctly:
    ref_norm = Normalize(np.min(ref_conc.filled(0)), np.max(ref_conc.filled(0)))
    comp_norm = Normalize(np.min(comp_conc.filled(0)), np.max(comp_conc.filled(0)))

    # Here I am creating a pyplot ScalarMappable object for each colorbar in order to get the correct
    # scaling of the data:
    ref_im = ScalarMappable(norm=ref_norm, cmap=cmap)
    comp_im = ScalarMappable(norm=comp_norm, cmap=cmap)

    # Putting the above steps together to make the colorbars and add titles:
    ref_cbar = fig.colorbar(ref_im, cax=ref_cb_ax)
    ref_cbar.ax.set_ylabel('Reference colorbar')
    comp_cbar = fig.colorbar(comp_im, cax=conc_cb_ax)
    comp_cbar.ax.set_ylabel('Comparison colorbar')

    # Making the axes and labels of ax invisible. Having a background axis object allows for a single title,
    # x-label and y-label. Otherwise these would need to be manually placed using x and y coordinates.
    ax.spines['top'].set_color('none')
    ax.spines['bottom'].set_color('none')
    ax.spines['left'].set_color('none')
    ax.spines['right'].set_color('none')
    ax.tick_params(labelcolor='w', top=False, bottom=False, left=False, right=False)

    # Making the fonts of the subplots larger:
    ax1.tick_params('both', labelsize=12)
    ax1.tick_params('y', right=True)
    ax2.tick_params('both', labelsize=12)
    ax2.set_yticklabels([])
    ax2.tick_params('y', right=True)

    # Finding the altitude of the current height, this should be the same for both datasets, so I just use
    # the reference dataset arbitrarily:
    height = ref_header_dataset.variables['ZTOP'][level]

    # Adding labels and titles:
    ax1.set_ylabel('Latitude', fontsize=15)
    ax.set_xlabel('Longitude', fontsize=15)
    # ax.set_title(f'FLEXPART-WRF output comparison plot of parcel {release_count} at time {time}, level {level}',
    #              fontsize=18)
    ax.set_title(f'Release: {release_count}, at time: {time}, height: {height}m', fontsize=18)

    # plt.show()
    # plt.close()
    plt.savefig(savedir)
    plt.close()
    print(f'Saved plot of release: {release_count}, level: {level}, time: {time}, in subfolder: {height}')


def error_check(reference_data, ref_dates, ref_header, comparison_data, comp_dates, comp_header):
    """ This function performs an error check on the FLEXPART-WRF outputs and determines if the can be compared
        using this visualisation script. It checks for:
        1. Check that the date files for both have the same number of dates but also the same date.
        If not, throw error and the program should stop with a message.

        2. Check that both header files (reference and comparison) have the same number of latitudes and longitudes
        and the same latitudes and longitudes. If not, throw error and the program should stop with a message.

        3. Check that both header files (reference and comparison) have the same number of altitudes and same altitudes.
        If not, throw error and the program should stop with a message.

        4. Check that the location of the releases is the same in both cases.

        :param reference_data: The reference dataset that will be plotted on the left hand side of the comparison
                               plots.
        :param ref_dates: The dates file for the reference dataset.
        :param ref_header: The header file for the reference dataset.
        :param comparison_data: The comparison dataset that will be plotted on the right hand side of the comparison
                                plots.
        :param comp_dates: The dates file for the comparison dataset.
        :param comp_header: The header file for the comparison dataset.
        """
    print('Starting error checks:\n')
    # Loading the dates files as numpy arrays:
    ref_times = np.loadtxt(ref_dates)
    comp_times = np.loadtxt(comp_dates)

    # Comparing the dates files:
    if len(ref_times) != len(comp_times):
        raise RuntimeError('WARNING: LENGTHS OF THE DATES FILES ARE NOT THE SAME, THESE OUTPUTS CANNOT BE COMPARED.')
    else:
        print('Checked lengths of dates files...')

    # Checking if all of the values inside of the date files are the same:
    if np.array_equal(ref_times, comp_times):
        print('Checked that the date values in both dates files are the same...')
    else:
        raise RuntimeError('WARNING: THE DATE VALUES IN THE DATE FILES ARE NOT THE SAME, OUTPUTS CANNOT BE COMPARED.')

    with nc.Dataset(reference_data) as ref_data:
        with nc.Dataset(comparison_data) as comp_data:
            ref_cent_lat = ref_data.__getattribute__('CEN_LAT')
            comp_cent_lat = comp_data.__getattribute__('CEN_LAT')
            ref_cent_lon = ref_data.__getattribute__('CEN_LON')
            comp_cent_lon = comp_data.__getattribute__('CEN_LON')

            if ref_cent_lat != comp_cent_lat or ref_cent_lon != comp_cent_lon:
                raise RuntimeError('WARNING: THE CENTRAL LATITUDE AND LONGITUDE VALUES ARE NOT THE SAME IN BOTH FILES')
            else:
                print('Checked that the centre latitude and longitude values of data are the same.')

    # Comparing the header files:
    with nc.Dataset(ref_header) as ref_header_data:
        with nc.Dataset(comp_header) as comp_header_data:
            # Check that the latitude and longitude variables have the same shape:
            if ref_header_data.variables['XLONG'].shape != comp_header_data.variables['XLONG'].shape:
                raise RuntimeError('WARNING: SHAPES OF THE XLONG VARIABLES ARE NOT THE SAME IN BOTH HEADERS')
            else:
                print('Checked that XLONG shapes are consistent in both header files...')

            if ref_header_data.variables['XLAT'].shape != comp_header_data.variables['XLAT'].shape:
                raise RuntimeError('WARNING: SHAPES OF THE XLAT VARIABLES ARE NOT THE SAME IN BOTH HEADERS')
            else:
                print('Checked that XLAT shapes are consistent in both header files...')

            # Check that the latitude and longitude variables have the same values:
            if np.array_equal(ref_header_data.variables['XLAT'][:], comp_header_data.variables['XLAT'][:]):
                print('Checked that XLAT values are consistent in both header files...')
            else:
                raise RuntimeError('WARNING: VALUES OF THE XLAT VARIABLES ARE NOT THE SAME IN BOTH HEADERS')

            if np.array_equal(ref_header_data.variables['XLONG'][:], comp_header_data.variables['XLONG'][:]):
                print('Checked that XLONG values are consistent in both header files...')
            else:
                raise RuntimeError('WARNING: VALUES OF THE XLONG VARIABLES ARE NOT THE SAME IN BOTH HEADERS')

            # Check that the levels are the same shape in both headers:
            if ref_header_data.variables['ZTOP'].shape != comp_header_data.variables['ZTOP'].shape:
                raise RuntimeError('WARNING: SHAPES OF THE ZTOP VARIABLES ARE NOT THE SAME IN BOTH HEADERS')
            else:
                print('Checked that ZTOP shapes are consistent in both header files...')

            # Check that the values of the levels are the same in both headers:
            if np.array_equal(ref_header_data.variables['ZTOP'][:], comp_header_data.variables['ZTOP'][:]):
                print('Checked that ZTOP values are consistent in both header files...')
            else:
                raise RuntimeError('WARNING: VALUES OF THE ZTOP VARIABLES ARE NOT THE SAME IN BOTH HEADERS')

    print('Error checks performed, no errors found!\n')


# Call to the function:
def main():
    reference_dir = r'/home/stefanie/wrk_dir/flexpart_palm/testcases_master_v4/testcase_09/flexpart_output'
    comparison_dir = r'/home/stefanie/wrk_dir/flexpart_palm/testcases_master_v4/testcase_09b/flexpart_output/'
    outdir = r'/home/stefanie/wrk_dir/flexpart_plots/'

    ref_netCDF = reference_dir + '/merged.nc'
    comp_netCDF = comparison_dir + '/merged.nc'
    ref_header = reference_dir + '/header_d01.nc'
    comp_header = comparison_dir + '/header_d01.nc'
    dates = reference_dir + '/dates'
    plot_out(ref_netCDF, comp_netCDF, outdir, dates, ref_header, comp_header)


if __name__ == '__main__':
    main()
