import rasterio
import rasterio

import numpy as np
import rioxarray as rxr
import numpy as np
import subprocess as sub

from matplotlib import pyplot as plt

from os.path import join

from pyproj import Transformer
from pyproj import Proj, transform

from rasterio.plot import show
from affine import Affine

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# reprojecting using GDAL:
# gdalwarp -t_srs "+proj=longlat +datum=WGS84 +no_defs" DSM_BQ31_2013_1000_2138.tif regridedd_DSM.tif


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx], idx

def load_transform_raster(fname):
    """
        Opens a raster file and converts the projection in WGS64 (lat/lon) projection.
        From https://gis.stackexchange.com/questions/129847/
        obtain-coordinates-and-corresponding-pixel-values-from-geotiff-using-python-gdal
    :param fname:
    :return:
    """
    # Read raster
    with rasterio.open(fname) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        data = r.read()  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(data.shape[2]), np.arange(data.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(rc2en, otypes=[np.float, np.float])(rows, cols)

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong', datum='WGS84')
    lons, lats = transform(p1, p2, eastings, northings)
    return data[0], lats, lons

def regrid(filepath, filename):
    """ Runs a gdal translate command to convert the tiff file to standard lat long projection.
        Full example command is: gdalwarp -t_srs "+proj=longlat +datum=WGS84 +no_defs" DSM_BQ31_2013_1000_2138.tif regridedd_DSM.tif """
    file_in = join(filepath, filename)
    file_out = join(filepath, 'regridded.tif')

    s = sub.getstatusoutput(f'gdalwarp -t_srs "+proj=longlat +datum=WGS84 +no_defs" {file_in} {file_out}')
    print(s)

def get_coords(address):
    """ Finds the lat lon of a house."""
    email = 'shaun@bodekerscientific.com'
    locator = Nominatim(user_agent=email, timeout=100)
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    location = geocode(address)
    house_coords = (float(location.raw['lat']), float(location.raw['lon']))
    return house_coords

def plot_data(dsm_file, rgr_dsm_file, dem_file, rgr_dem_file, outdir, location, plot_location=False, plot_2d_diff=False, plot_3d_diff=False):
    """ Opens and plots the input geotiff data, expects a DSM and a DEM file.
        :param dsm_file: path to the DSM.tif file
        :param rgr_dsm_file: path to the DSM file regridded using regrid()
        :param dem_file: path to the DEM.tif file
        :param rgr_dem_file: path to the DEM file regridded using regrid()
        :param outdir: directory that files will be saved in.
        :param plot_location: Make a comparison plot of where the input address is in both DSM and DEM files.
        :param plot_2d_diff: Subtracts the DEM from the DSM (DSM-DEM) and plots the resulting height in a 2d contour plot.
        :param plot_3d_diff: Same as 2d, but a 3d plot. """

    dsm = rxr.open_rasterio(dsm_file)
    # dsm.head

    dem = rxr.open_rasterio(dem_file)
    # dem.head

    # Load tif files
    rgr_dem = rxr.open_rasterio(rgr_dem_file)
    dem = rasterio.open(rgr_dem_file)

    rgr_dsm = rxr.open_rasterio(rgr_dsm_file)
    dsm = rasterio.open(rgr_dsm_file)

    # Location plot
    if plot_location:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18,10))
        fig.suptitle('Rendering of DSM and DEM geotiff files.', fontsize=18)

        dem_im = show(dem, ax=ax1, cmap='bone')
        ax1.set_title('DEM', fontsize=16)
        ax1.ticklabel_format(useOffset=False, style='plain')
        ax1.scatter(location[1], location[0], c='red', marker='x')
        ax1.set_ylabel('Latitudes', fontsize=16)
        ax1.set_xlabel('Longitudes', fontsize=16)

        dsm_im = show(dsm, ax=ax2, cmap='bone')
        ax2.set_title('DSM', fontsize=16)
        ax2.ticklabel_format(useOffset=False, style='plain')
        ax2.scatter(location[1], location[0], c='red', marker='x')
        ax2.set_xlabel('Longitudes', fontsize=16)

        plt.tight_layout()

        plt.savefig(join(outdir, 'location_plot.jpeg'), dpi=350)

    # Use Leroy's script to rasterize DEM, DSM files.
    dem_heights, dem_lats, dem_lons = load_transform_raster(rgr_dem_file)
    dsm_heights, dsm_lats, dsm_lons = load_transform_raster(rgr_dsm_file)

    # Code to find and compare the heights of a point in the DSM and DEM:
    # Use find_nearest since the precise datapoint may not be in dataset.
    dem_lat_val, dem_lat_idx = find_nearest(dem_lats[0,:], location[1])
    dem_lon_val, dem_lon_idx = find_nearest(dem_lons[:,0], location[0])

    # Find height at point in DEM:
    dem_bld_height = dem_heights[dem_lon_idx, dem_lat_idx]

    dsm_lat_val, dsm_lat_idx = find_nearest(dsm_lats[0,:], location[1])
    dsm_lon_val, dsm_lon_idx = find_nearest(dsm_lons[:,0], location[0])

    # Find height at point in DSM:
    dsm_bld_height = dsm_heights[dsm_lon_idx, dsm_lat_idx]

    dsm_heights[dsm_lon_idx, dsm_lat_idx] - dem_heights[dem_lon_idx, dem_lat_idx]

    print(f'The height of the building in the DEM is: {dem_bld_height:.2f}\n',
          f'In the DSM it is: {dsm_bld_height:.2f}\n',
          f'And the difference is: {(dsm_heights[dsm_lon_idx, dsm_lat_idx] - dem_heights[dem_lon_idx, dem_lat_idx]):.2f}')


    # 3d plotting code:

    # Calculate difference between DSM and DEM.
    heights = dsm_heights - dem_heights

    # Drop all heights above 200m
    thresh_idxs = heights > 200
    heights[thresh_idxs] = 0

    if plot_3d_diff:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.gca(projection='3d')
        surf = ax.plot_surface(dsm_lats, dsm_lons, heights, cmap='viridis',
                            linewidth=0, antialiased=False)

        plt.title('Difference between DSM and DEM (DSM-DEM)', fontsize=18)
        plt.xlabel('Latitudes', fontsize=14, labelpad=12)
        plt.ylabel('Longitudes', fontsize=14, labelpad=12)
        ax.set_zlabel('Height [m]', fontsize=14, labelpad=10)
        ax.ticklabel_format(useOffset=False, style='plain')

        plt.savefig(join(outdir, '3dvisualisation.jpeg'), dpi=350)

    #2d plotting code:
    if plot_2d_diff:
        fig, ax = plt.subplots(1, figsize=(10,12))

        plt.contourf(dsm_lats, dsm_lons, heights, cmap='viridis')
        plt.margins(0.5)
        plt.title('Difference between DSM and DEM (DSM-DEM)', fontsize=18)
        plt.xlabel('Latitudes', fontsize=14, labelpad=12)
        plt.ylabel('Longitudes', fontsize=14, labelpad=12)
        plt.colorbar()
        ax.ticklabel_format(useOffset=False, style='plain')

        plt.tight_layout()
        plt.savefig(join(outdir, '2d_diff_visualisation.jpeg'), dpi=350)


def main():
    """ Examples below on how to set up and run the code;"""
    # Run #1;
    # DSM_file = r'DSM_BQ31_2013_1000_2138.tif'
    # DSM_path = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DSM'
    # dsm_file = join(DSM_path, DSM_file)

    # DEM_file = r'DEM_BQ31_2013_1000_2138.tif'
    # DEM_path = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DEM'
    # dem_file = join(DEM_path, DEM_file)

    # house_coords = (-41.29111111, 174.79166667)

    # outdir = r'/home/shaun/Documents/work_dir/climate_sigma/plots/test'

    # rgr_dsm_file = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DSM/regridded_DSM.tif'
    # rgr_dem_file = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DEM/regridded_DEM.tif'

    # plot_data(dsm_file, rgr_dsm_file, dem_file, rgr_dem_file, outdir, house_coords, plot_location=True, plot_2d_diff=True, plot_3d_diff=True)

    # Run #2;
    DEM_path = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DEM/2/'
    DEM_file = r'DEM_BQ31_2013_1000_2239.tif'
    dem_file = join(DEM_path, DEM_file)

    DSM_path = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DSM/2/'
    DSM_file = r'DSM_BQ31_2013_1000_2239.tif'
    dsm_file = join(DSM_path, DSM_file)

    house_coords = get_coords('46 Rakau Road, Hataitai')
    
    outdir = r'/home/shaun/Documents/work_dir/climate_sigma/plots/test2'

    # filepath = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DEM/2'
    # filename = r'DEM_BQ31_2013_1000_2239.tif'
    # regrid(filepath, filename)

    rgr_dsm_file = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DSM/2/regridded.tif'
    rgr_dem_file = r'/home/shaun/Documents/work_dir/climate_sigma/land_data/working_dir/DEM/2/regridded.tif'

    plot_data(dsm_file, rgr_dsm_file, dem_file, rgr_dem_file, outdir, house_coords, plot_location=True, plot_2d_diff=True, plot_3d_diff=True)

main()