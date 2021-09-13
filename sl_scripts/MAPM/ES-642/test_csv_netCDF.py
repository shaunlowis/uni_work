""" Test file for checking continuity of data files.
"""
from users.mc_scripts.MAPM.ES_642.retrieve_ES_642 import filenames_as_list
from users.lb_scripts.csv_to_netCDF import CSVToNC

import pandas as pd
import netCDF4 as nc
import numpy as np

DEFINITIONS_FILE = '/mnt/storage/Scratch/Shaun/MAPM/ES642/ECAN_642_definitons.tsv'
INPUT_FILES = r"/mnt/storage/Scratch/Shaun/MAPM/ES642/dat_files_info/valid_files.txt"
OUTPUT_DIR = r"/mnt/storage/Scratch/Shaun/MAPM/ES642/dat_netCDFs/{}.nc"


def val_files(fp_v):
    """
    :param fp_v:
    :return:
    """
    outlist = []
    with open(fp_v, 'r') as fpv:
        for file in fpv:
            outlist.append(file)
    return outlist


def main():
    dat_files = filenames_as_list()
    definition_df = pd.read_csv(DEFINITIONS_FILE, sep='\t')

    init = CSVToNC()

    for file in dat_files:
        file = file.strip()
        init = init.from_csv(file, find_dates=False, names=["unix_timestamp", "PM2.5 conc", "flow",
                                                            "temp", "rh", "press", "PM2.5 conc 1 hr average",
                                                            "instrument status code", "PM2.5 sensor no of readings",
                                                            "serial number", "wind direction", "wind speed",
                                                            "wind sensor no of readings", "checksum"])
        init['unix_timestamp'].values = nc.num2date(init['unix_timestamp'].values, 'seconds since 1970-01-01 00:00:0')
        init = init.set_attributes(definition_df=definition_df)
        fname = dat_files[97:]
        init.to_netcdf(OUTPUT_DIR.format(fname))
        print(f"file {fname} created")


main()
