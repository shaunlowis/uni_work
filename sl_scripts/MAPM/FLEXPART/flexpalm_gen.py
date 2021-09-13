"""Script for automatically producing a flexpalm.input file from a directory of PALM output files.
    The script checks for continuity in timesteps between files and has catches and exceptions for
    unexpected filetypes. The file is saved in the 'outdir' location.
    The Confluence writeup is here:
    https://confluence.bodekerscientific.com/pages/viewpage.action?pageId=42468426
    Written by Johnny (Shaun) Lowis, for Bodeker Scientific.
"""

import netCDF4 as nc
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import datetime as dt


def make_flexpalm_gen(outdir, static_input_path, PALM_output_path):
    """ Script for automatically generating the flexpalm.input file.
        I have purposefully written the lines out as much as possible in order to increase the legibility of the script.
        This helps with debugging and visualising what the actual text file produced will look like.
        :param outdir: The output directory where the flexpalm.input file will be written to.
        :param static_input_path: The path to the static input file.
        :param PALM_output_path: The path to the PALM model run's outputs, this should point to a directory.
    """
    # Declaring the name of the file to be written:
    flexpalm_file = outdir + 'flexpalm.input'

    # Writing the header lines and creating the flexpalm.input file.
    # As in the docstring, this format was done intentionally to increase legibility, albeit less 'pythonic'.
    with open(flexpalm_file, 'w') as output_file:
        line1 = '! PALM data input namelist file\n'
        line2 = '!******************************************************************************\n'
        line3 = '&palm_input_namelist\n'
        line4 = '\n'
        line5 = f"   palm_static_driver_file   = '{static_input_path}',\n"
        line6 = f"   palm_3d_data_dir          = '{PALM_output_path}',\n"
        line7 = '\n'
        output_file.write(line1 + line2 + line3 + line4 + line5 + line6 + line7)

    # List comprehension line to create a list of files inside the PAL_output directory:
    files = [f for f in listdir(PALM_output_path) if isfile(join(PALM_output_path, f))]
    dts = []
    # sort the files according to their times
    for i, file in enumerate(files):
        name = os.path.splitext(file)[0]
        hour = int((name.split('_')[5]).split('h')[0])
        min = int((name.split('_')[6]).split('m')[0])
        if hour == 24:
            dts.append(dt.datetime(2000, 1, 2, 0, min))
        else:
            dts.append(dt.datetime(2000, 1, 1, hour, min))

    # now sort the datetime array and get the files in the right order
    files = np.asarray(files)
    files = files[np.argsort(dts)]
    # Here the start and end times of the PALM output files are retrieved and appended to a list for sorting:
    formatted_files = []
    output_file = open(flexpalm_file, 'a')
    for i, file in enumerate(files):
        with nc.Dataset(PALM_output_path + file) as data:
            try:
                if data.variables['time'][0] != np.min(data.variables['time']):
                    raise RuntimeError('ERROR: The lowest time value is not at the start of the file!')
                if data.variables['time'][-1] != np.max(data.variables['time']):
                    raise RuntimeError('ERROR: The highest time value is not at the end of the file!')

                # get the first time step from the second file
                maxval = len(files)

                start_time = np.min(data.variables['time'][:])
                end_time = np.max(data.variables['time'][:])

                if i != maxval - 1:
                    data_next = nc.Dataset(PALM_output_path + files[i+1])
                    next_time = np.min(data_next.variables['time'][:])
                    rounded_next_time = np.floor(float(next_time))
                else:
                    rounded_next_time = np.floor(float(end_time))

                ## Note that PALM's time steps come in seconds but have some sort of decimal places, e.g. hour 3 of a PALM run is
                ## time step 10800.XXX where the XXX varies from run to run for some reasons that are not clear to me (Stefanie).
                ## So here we will take the rounded numbers, i.e. hour 3  starts at 10800.00 and after 9 minutes we will be at 11340.00.
                ## So we will ignore the XXX as this is not important for the generation of this file.

                rounded_start_time = np.floor(float(start_time))
                rounded_end_time = np.floor(float(end_time))

                calculated_end_time = rounded_end_time + 60

                if (len(data.variables['time']) != 10) and not('24h_0m' in file):
                    raise RuntimeError(f'ERROR: file {file} does not have 10 time steps as required!')

                if rounded_end_time > calculated_end_time:
                    raise RuntimeError(f'ERROR: file {file} something went wrong your end_time is incorrect!')

                if i != maxval - 1:
                    # since PALM is very annoying how it handles the times, the time steps can be out by some part of a second
                    if (calculated_end_time - rounded_next_time) > 2:
                        raise RuntimeError(f'ERROR: file {file} something went wrong!')

                available_PALM_string = f"   palm_3d_data_mapping({i + 1})   = {float(rounded_start_time)}, {float(rounded_next_time)},'{file}',\n"
                output_file.write(available_PALM_string)
                    #formatted_files.append(str(np.floor(float(start_time))) + ':' + str(file) + ':' +
                    #                       str(np.floor(float(end_time + 60))))

            # This exception catches all of the static files and other files that don't have a time variable,
            # to let the script skip incorrect datafiles.
            except KeyError:
                print(f'WARNING, file {file} has no "time" variable!')

    # Adding the footer to the flexpalm.input file:
    with open(flexpalm_file, 'a') as output_file:
        output_file.write('\n' + '/ ! end of namelist')

    print(f'Finished writing the flexpalm.input file, output directory is: {flexpalm_file}')

    output_file.close()

    # Sorting the start_times list. If this doesn't work, I will write a manual sorting algorithm.
    #sorted_times = sorted(formatted_files)

    # for i, file in enumerate(formatted_files):
    #     # Here I check that the start time of the next datafile is the same as the end time of the current
    #     # datafile:
    #     maxval = len(formatted_files)
    #
    #     if i != maxval - 1:
    #         fp_next_file = PALM_output_path + formatted_files[i + 1].split(':')[1]
    #         data = nc.Dataset(PALM_output_path + file.split(':')[1])
    #         current_file_end_time = np.floor(float(data.variables['time'][-1])) + 60
    #         next_file_start_time = np.floor(float(nc.Dataset(fp_next_file).variables['time'][0]))
    #
    #         if (current_file_end_time - next_file_start_time) > 1:
    #             raise RuntimeError(f'ERROR: discontinuity in timesteps between files {files[i]} and '
    #                                f'{files[i + 1]}!')
    #
    # # Iterating through the sorted list. The list contains elements in the format [start time]:[filename]:[end time]
    # # Hence, when splitting the element, the start time, end time and filename is retrieved without having to
    # # reopen the individual NetCDF PALM output files. These are then appended to the flexpalm.input file:
    # for count, file in enumerate(formatted_files):
    #     filename = file.split(':')[1]
    #     start = file.split(':')[0]
    #     end = file.split(':')[2]
    #     with open(flexpalm_file, 'a') as output_file:
    #         available_PALM_string = f"   palm_3d_data_mapping({count + 1})   = {float(start)}, {float(end)},'{filename}',\n"
    #         output_file.write(available_PALM_string)




# Declare the appropriate variables here:

# Outdir is where you want the file to be written
outdir = r'/home/stefanie/wrk_dir/flexpart_palm/testcases_master_v4/testcase_09/'
# Static input path and name
static_input_file = r'/mnt/temp/Projects/MAPM/Data_Delete/PALM/MAPM_runs/new_wrf/06_21/Input/chch_full_06-21_static_N02'
# NOTE: THIS NEEDS TO BE THE DIRECTORY OF THE PALM OUTPUTS:
day06_21 = r'/mnt/temp/Projects/MAPM/Data_Delete/PALM/MAPM_runs/new_wrf/06_21/'

# Call the function:
make_flexpalm_gen(outdir, static_input_file, day06_21)
