""" Takes in files over min length value, checks and flags calibration times.
    Written by Johnny (Shaun) Lowis for Bodeker Scientific.
"""
import glob
import os
import csv
import pandas as pd


FILE_PATH_LOCATION = '/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES_642/Raspberry Pis'
MINI_LINES_IN_FILE = 12 * 60


def err_find(files_list):
    """ Finds and flags error lines
    :param files_list: list of files to iterate through
    :return: error lines.
    """
    errlist = []

    for fp in files_list:
        with open(fp, 'r') as f:
            for i, line in enumerate(f):
                if line[9:30] == "0,0.0,0.0,0.0,0.0,0.0":
                    err = "Error at line {}, {}\n".format(str(i), str(line))
                    errlist.append(err)

    if len(errlist) != 0:
        print("The following lines had errors: \n")
        for err in errlist:
            print(err)


def time_jump(files_list):
    """ Finds and flags any time jumps inside files.
    :param files_list: list of ES_642 data files
    :return: jumps in time
    """
    err_textfiles = r"/home/slowis/Documents/err_data"
    jumps = []
    invalid_lines = []

    for fp in files_list:
        with open(fp, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if i < len(lines):
                    curr = lines[i].split(",")[0]
                    prev = lines[i - 1].split(",")[0]
                    try:
                        if int(curr) - int(prev) != 60:
                            jump_str = "Jump in line {} in file {}\n"
                            frmt_jump = jump_str.format(i, fp)
                            jumps.append(frmt_jump)
                    except ValueError:
                        err_string = "Error in line {} in file {}\n"
                        frmt_str = err_string.format(i, fp)
                        invalid_lines.append(frmt_str)

    if len(jumps) != 0:
        print("WARNING TIME JUMPS PRESENT! SEE 'time_jumps.txt'\n")
        fname = "time_jumps.txt"
        fdir = err_textfiles + "/" + fname
        with open(fdir, 'w') as f:
            for jump in jumps:
                f.write(jump)
    else:
        print("No time jumps inside input files.")

    if len(invalid_lines) != 0:
        print("WARNING INVALID LINES PRESENT! SEE 'line_errors.txt'\n")
        fname = "line_errors.txt"
        fdir = err_textfiles + "/" + fname
        with open(fdir, 'w') as f:
            for inval in invalid_lines:
                f.write(inval)

    else:
        print("No invalid lines in files.")


def get_local_dirs():
    dirs = [name for name in os.listdir(FILE_PATH_LOCATION) if os.path.isdir(os.path.join(FILE_PATH_LOCATION, name))]
    return [os.path.join(FILE_PATH_LOCATION, name) for name in dirs]


# valid files have at least 12 hours of data contained.
def find_valid_files():
    local_dirs = get_local_dirs()

    valid_files = []
    for local_dir in local_dirs:
        device_files = glob.glob(f"{local_dir}/*.dat")

        for file_loc in device_files:
            with open(file_loc, 'r') as f:
                local_ref = os.path.join(*file_loc.split('/')[-2:])
                if len(f.readlines()) >= MINI_LINES_IN_FILE:
                    valid_files.append(file_loc)
                    print(f"Added file: {local_ref}")

    print("done..")
    return valid_files


def add_header(fp_data, fp_header):
    """
    :param fp_data:
    :param fp_header:
    :return:
    """
    with open(fp_data, 'w', newline='') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerow(["Date", "temperature 1", "Temperature 2"])

        with open(fp_header, 'r', newline='') as incsv:
            reader = csv.reader(incsv)
            writer.writerows(row + [0.0] for row in reader)


def main():
    # fp_data = r"/home/slowis/Documents/test/es642/dmm_control0028.csv"
    # fp_header = r""

    # df = pd.read_csv(fp_data, header=None)

    files_list = find_valid_files()

    # err_find(files_list)
    time_jump(files_list)


main()
