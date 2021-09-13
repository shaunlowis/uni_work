import os
from osgeo import gdal
# osgeo can be installed using: conda install -c conda-forge gdal
import numpy as np
import pandas as pd
import contextily as ctx
import matplotlib.pyplot as plt


def check_asc():
    fp_dir = r'/home/shaun/Documents/work_dir/greg_project/palm/JOBS/auckland_buildings/INPUT/'
    fp_asc = r'auckland_buildings_topo'
    data = os.path.join(fp_dir, fp_asc)
    data = pd.read_csv(data)
    print(data)


check_asc()


def main():
    dir_fp = r'/home/shaun/Documents/work_dir/greg_project/palm_files/Auckland_DEM/buildings/'
    file = r'DEM_BA31_3532_2013.tif'
    fp = os.path.join(dir_fp, file)
    gdal_data = gdal.Open(fp)

    west, south, east, north = (174.391862, -37.320988, 175.135059, -36.337212)

    ghent_img, ghent_ext = ctx.bounds2img(west, south, east, north, ll=True, source=ctx.providers.CartoDB.Voyager)

    f, ax = plt.subplots(1, figsize=(9, 9))
    ax.imshow(ghent_img, extent=ghent_ext)

    gadl_band = gdal_data.GetRasterBand(1)
    nodataval = gadl_band.GetNoDataValue()

    data_array = gdal_data.ReadAsArray().astype(np.float)
    data_array = np.flipud(data_array)

    if np.any(data_array == nodataval):
        data_array[data_array == nodataval] = np.nan

    fig = plt.figure(figsize=(7, 8))
    ax = fig.add_subplot(111)
    plt.contourf(data_array, cmap="viridis", alpha=1)
    plt.title(f"Auckland DEM: {file}")
    plt.colorbar()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

#
# main()
