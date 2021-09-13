""" Generating emissions map for Stefanie from
    ECAN census data"""

import cartopy
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties

CENSUS_FILEPATH = r'/home/shaun/Documents/work_dir/bottom_up/census_data/MB_plus_census_wood.xlsx'
OUTPUT_DIR = r'/home/slowis/Documents/wrkdir/stefanie_emissions_map/output'
GRID = r'/home/slowis/Documents/wrkdir/stefanie_emissions_map/input/chch_mapm_01_static.nc'


def map_gen(dataset, output_path, readme=False):
    """ Takes in given dataset in pandas dataframe format,
        returns cartographic projection of input dataset.
    :param output_path: Directory to where emissions map and README are saved.
    :param readme: Whether or not to produce a README.txt file with metadata of the emissions map.
    :param dataset: Input data for projecting.
    :return: Outputted map plot.
    """

    # Define font for continuity in plot.
    font = FontProperties()
    font.set_size(14)

    # Retrieve data from ECAN files' pandas DataFrame.
    lons = dataset["Centroid Long"]
    lats = dataset["Centroid Lat"]
    areas = dataset["AREA_M2"]
    pm = dataset["Emissions (grams Pm2.5) per night"] / areas

    # with nc.Dataset(GRID) as grid_data:
    #     lats = grid_data['lat'][:]
    #     lons = grid_data['lon'][:]

    # Used to find the corners of the map projection
    minlon = np.min(lons) - 0.01
    maxlon = np.max(lons) + 0.01
    minlat = np.min(lats) - 0.01
    maxlat = np.max(lats) + 0.01

    # Define map's orientation and initiate figure instance.
    extent = [minlon, maxlon, minlat, maxlat]
    central_lon = np.mean(extent[:2])
    plt.figure(figsize=(12, 9), dpi=400)

    # Add Cartopy GeoSubplot objects, as well as geographical features and axes labels.
    ax = plt.axes(projection=ccrs.PlateCarree(central_lon))
    ax.set_extent(extent)
    ax.add_feature(cartopy.feature.OCEAN)
    ax.add_feature(cartopy.feature.LAND, edgecolor='black')
    ax.add_feature(cartopy.feature.LAKES, edgecolor='black')
    ax.add_feature(cartopy.feature.COASTLINE)
    ax.gridlines(draw_labels=True)
    ax.text(-0.13, 0.55, 'Latitude', va='bottom', ha='center',
            rotation='vertical', rotation_mode='anchor',
            transform=ax.transAxes, fontsize=14)
    ax.text(0.5, -0.12, 'Longitude', va='bottom', ha='center',
            rotation='horizontal', rotation_mode='anchor',
            transform=ax.transAxes, fontsize=14)

    plt.show()
    print('Finished generating emissions map.')

    # plt.savefig(OUTPUT_DIR, 'emissions_map.png')
    plt.show()

    # Generation of README.txt file with metadata, further details will be added as script develops.
    if readme:
        template = 'Metadata for emissions map produced by Bodeker Scientific, for inquiries contact:\n' \
                   'shaun@bodekerscientific.com\n' \
                   'The produced image is an emissions map of the Christchurch area, produced from ECAN\n' \
                   'census data. The x-axis is Longitude, the y-axis is Latitude. Each dot represents one\n' \
                   'household woodburner. The individual woodburner emissions from the ECAN data were divided\n' \
                   'by the areas of the households they were in. This produced emissions of units g/m^2.\n' \
                   'The emissions were recorded as PM2.5 per night by ECAN. The exact definition of a night\'s\n' \
                   'time period is yet to be clarified at this stage. The coastline can be seen in the top right\n' \
                   'corner.\n' \
                   f'The grid file is located at {GRID}\n' \
                   f'The census file is located at {CENSUS_FILEPATH}\n' \

        with open(output_path + '/' + 'README.txt', 'w') as fpf:
            fpf.write(template)

        print('Finished generating README.txt file.')


def main():
    # Read ECAN census data into Pandas DataFrame:
    dataset = pd.read_excel(CENSUS_FILEPATH)
    map_gen(dataset, OUTPUT_DIR)


if __name__ == '__main__':
    main()
