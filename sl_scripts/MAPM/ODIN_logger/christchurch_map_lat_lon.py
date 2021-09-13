"""Author: Shaun Lowis, Date: 02/07/2019, For Bodeker Scientific.
   Adding the lat and lon plotpoints from the instruments.csv file
   over a map of Christchurch"""

import os

conda_file_dir = "/home/shaun/miniconda3/envs/bs-36/"
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

from mpl_toolkits.basemap import Basemap
from bs.core import env
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def dataframe():
    """reads the instruments.csv file and makes a pandas dataframe"""
    filename = env.scratch("Shaun", "ODIN_logger", "instruments.csv")
    df = pd.read_csv(filename, parse_dates=['time', 'last_backup'], date_parser=pd.core.tools.datetimes.to_datetime)
    return df


def lats_dataframe(df):
    """creates a dataframe using all the lats values from the instruments file"""
    lats = df["lat"].values
    lats[lats == 0] = np.nan
    lat_grid = np.linspace(np.nanmin(lats), np.nanmax(lats), 200)
    return lat_grid


def lons_dataframe(df):
    """creates a dataframe using all the lons values from the instruments file"""
    lons = df["lon"].values
    lons[lons == 0] = np.nan
    lon_grid = np.linspace(np.nanmin(lons), np.nanmax(lons), 200)
    return lon_grid


def nanmin(df, lat_or_lon):
    """finds the nanmin val of either a lat or lon by a dataframe input, and a string for lat or lon"""
    val = df[lat_or_lon].values
    minout = np.nanmin(val)
    return minout


def nanmax(df, lat_or_lon):
    """finds the nanmax val of either a lat or lon by a dataframe input, and a string for lat or lon"""
    val = df[lat_or_lon].values
    maxout = np.nanmax(val)
    return maxout


def data_finder(filepath):
    """extracts the data values from an ODIN file and appends them to a data list."""
    dataout = []
    with open(filepath) as file:
        file.readline()
        for line in file:
            line = line.split(";")
            dataout.append(line[2])
    return dataout


def input_asker(filenum):
    """gets the filename or desired input from the user"""
    if filenum == 1:
        filename = input("Enter the folder name: ")
        return filename
    elif filenum == 2:
        filename = input("Enter the Odin datafile name: ")
        return filename


def main():
    """the main function"""
    df = dataframe()
    lats = lats_dataframe(df)
    lons = lons_dataframe(df)
    min_lon = nanmin(df, "lon")
    min_lat = nanmin(df, "lat")
    max_lon = nanmax(df, "lon")
    max_lat = nanmax(df, "lat")
    data = data_finder(env.scratch("Shaun", "ODIN_logger", "processed", input_asker(1), input_asker(2)))
    b_map = Basemap(llcrnrlon=min_lon, llcrnrlat=min_lat, urcrnrlon=max_lon, urcrnrlat=max_lat, epsg=4269)
    b_map.arcgisimage(service='ESRI_Imagery_World_2D', xpixels=2000, verbose=True)
    b_map.scatter(lons, lats, latlon=True, c=data, s=700, cmap="" )
    plt.show()

# make an x and y plot using all of the times and 3rd values from the ODIN files


main()
