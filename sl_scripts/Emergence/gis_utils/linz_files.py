import os
import pyproj
import shapefile
import geopy

from os.path import join
from pyproj import CRS
from pyproj import Transformer
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from shapely.geometry import Point

import shapely.speedups
shapely.speedups.enable()

import subprocess as sub
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx

from shapely.ops import transform

# Useful guide on working with .shp files:
# https://towardsdatascience.com/mapping-with-matplotlib-pandas-geopandas-and-basemap-in-python-d11b57ab5dac
# Online course on using .shp files and geospatial data analysis with python:
# https://www.earthdatascience.org/workshops/gis-open-source-python/intro-vector-data-python/

# Command for outputting changed projection .shp file; 'ogr2ogr -t_srs EPSG:4326 destination.shp source.shp'

def shape_location_finder(in_dir, out_dir, data, plot_data=False, save_data=False):
    """ Converts LINZ data to coordinates, then finds the location of each house in the dataset and adds it to a .csv file.
        :param in_dir: Input directory where shapefiles are stored.
        :param out_dir: Where the .csv and, if savedir=True, a plot of the data will be stored.
        :param data: The filename of the .shp file.
                                                        -kwargs**-
        :param plot_data: Whether to plot the shapefile with a contextily basemap.
        :param save_data: Whether to save the plot to out_dir. """
    # Using os.path.join for windows and linux compatibility
    data_in = join(in_dir, data)

    # Reading and plotting the data using geopandas:
    data = gpd.read_file(data_in)
    print('Data loaded')

    # Using the data.to_crs(4326) command converts the data from the NZGD2000 projection to latitudes and longitudes.
    polygons = data['geometry']
    centroid_coords = polygons.centroid
    centroid_coords = centroid_coords.to_crs(4326)
    print('Converted to EPSG:4326, calculated centroids')

    locations = {}
    # Initialising a geolocator object in order to find the locations of houses
    email = 'shaun@bodekerscientific.com'
    geolocator = Nominatim(user_agent=email, timeout=100)
    print('Finding locations of houses.')

    # Iterating through all the point objects we converted to coordinates above and finding their locations
    for n in range(0, len(centroid_coords)):
        coords = f'{centroid_coords[n].y}, {centroid_coords[n].x}'
        location = geolocator.reverse(coords)
        locations[coords] = location
        print(location)

    # Saving this data to a .csv file
    print(f'Saving data to {out_dir}')
    df = pd.DataFrame.from_dict(locations, orient="index")
    df.to_csv(join(out_dir, 'locations.csv'), index=0)
    print('Data saved.')

    # Adding a basemap background for the data to give a better idea of where the dataset is, using contextily module:

    if plot_data:
        fig, ax = plt.subplots(figsize=(12, 8))
        centroid_coords.plot(ax=ax, markersize=0.005)
        ax = plt.gca()
        ctx.add_basemap(ax=ax, crs='EPSG:4326', source=ctx.providers.CartoDB.VoyagerNoLabels, cmap='plasma')
        plt.axis('equal')
        plt.title('Centre of LINZ catalogued buildings in New-Zealand')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.tight_layout()
        plt.show()

        if save_data:
            fig, ax = plt.subplots(figsize=(12, 8))
            centroid_coords.plot(ax=ax, markersize=0.005)
            ax = plt.gca()
            ctx.add_basemap(ax=ax, crs='EPSG:4326', source=ctx.providers.CartoDB.VoyagerNoLabels, cmap='plasma')
            lims = plt.axis('equal')
            plt.title('Centre of LINZ catalogued buildings in New-Zealand')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.tight_layout()
            plt.savefig(save_data)
        else:
            pass
    else:
        pass

def locs_from_shp(in_dir, data, out_dir):
    """" Takes in a shapefile, finds the centroids of the shapes, saves it as a .shp file containing only coords and shapes.
         Useful for avoiding opening large shapefiles that have useless data in them."""

    data_in = join(in_dir, data)
    data = gpd.read_file(data_in)
    polygons = data['geometry']
    centroid_coords = polygons.centroid
    centroid_coords = centroid_coords.to_crs(4326)

    df = gpd.GeoDataFrame()
    lats = centroid_coords.y
    lons = centroid_coords.x
    df['coords'] = lats.astype(str) + ', ' + lons.astype(str)
    df['geometry'] = polygons

    print('Loaded df...')

    df.to_file(out_dir)
    print(f'Finished writing to shapefile at {out_dir}')

def coords_from_address(address, locs_shp):
    """ Input address, find coordinates in lat lon grid (EPSG:4326)"""
    email = 'shaun@bodekerscientific.com'
    locator = Nominatim(user_agent=email, timeout=100)
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    location = geocode(address)
    loc = f"{location.raw['lat']}, {location.raw['lon']}"

    point = Point(float(location.raw['lat']), float(location.raw['lon']))

    wgs84_pt = point

    wgs84 = pyproj.CRS('EPSG:4326')
    utm = pyproj.CRS('NZGD2000')

    data = gpd.read_file(locs_shp)

    project = pyproj.Transformer.from_crs(wgs84, utm, always_xy=True).transform
    utm_point = transform(wgs84_pt, data)

    out = []

    for poly in data.geometry:
        if point.within(poly):
            out.append(poly)
    
    print(out)

def main():
    in_path = r'/mnt/temp/sync_to_data/LINZ/nz-building-outlines'
    # out_path = r'/home/shaun/Documents/work_dir/LINZ/locations'
    shapefile_data = r'nz-building-outlines-1.shp'
    # shapefile_data2 = r'nz-building-outlines-2.shp'

    shape = join(in_path, shapefile_data)
    new_shp = r'/home/shaun/Documents/work_dir/climate_sigma/locations.shp'

    # Run below to find locations of all houses in shapefile:
    # shape_location_finder(in_path, out_path, shapefile_data)
    # Run below to plot and view the data:
    # shape_location_finder(in_path, out_path, shapefile_data, plot_data=True)
    # Run below to plot and save the plot of the data:
    # shape_location_finder(in_path, out_path, shapefile_data, plot_data=True, save_data=True)

    # Testing new function:
    
    out_dir = r'/home/shaun/Documents/work_dir/climate_sigma/locations.shp'
    # locs_from_shp(in_path, shapefile_data, out_dir)

    coords_from_address('42 Russell street Alexandra', shape)

if __name__ == "__main__":
    main()

# Here you can add additional arguments, described in the docs: https://geopandas.org/reference.html#geopandas.GeoSeries.plot

# The attributes of the LINZ .shp file:
# building_i, name, use, suburb_loc, town_city, territoria, capture_me, capture_so, capture__1, capture__2, capture__3, capture__4, last_modif, geometry
