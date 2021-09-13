import os
import cdsapi

from os.path import join
from pathlib import Path


def download(fp, dtype, var, year):
    c = cdsapi.Client()

    if dtype == 'netcdf':
            savedir = join(fp, f'{year}.nc')
            if os.path.exists(fp):
                pass
            else:
                Path(fp).mkdir(parents=True, exist_ok=True)

    elif dtype == 'grib':
        savedir = join(fp, f'{year}.grib')
        if os.path.exists(fp):
            pass
        else:
            Path(fp).mkdir(parents=True, exist_ok=True)

    c.retrieve(
        'reanalysis-era5-pressure-levels-monthly-means',
        {
            'product_type': 'monthly_averaged_reanalysis',
            'variable': str(var),
            'pressure_level': [
                '1', '2', '3',
                '5', '7', '10',
                '20', '30', '50',
                '70', '100', '125',
                '150', '175', '200',
                '225', '250', '300',
                '350', '400', '450',
                '500', '550', '600',
                '650', '700', '750',
                '775', '800', '825',
                '850', '875', '900',
                '925', '950', '975',
                '1000',
            ],
            'year': str(year),
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'time': '00:00',
            'format': str(dtype),
        }, savedir)


def main():
    TYPE = 'grib'
    BASE_DIR = r'/mnt/temp/sync_to_data/ERA5/global_monthly_means/reanalysis'
    vars = ['Divergence', 'Geopotential',  'Divergence', 'Fraction of cloud cover',
            'Geopotential', 'Ozone mass mixing ratio', 'Potential vorticity',
            'Relative humidity', 'Specific cloud ice water content', 'Specific cloud liquid water content',
            'Specific humidity', 'Specific rain water content', 'Specific snow water content', 'Temperature',
            'U-component of wind', 'V-component of wind', 'Vertical velocity', 'Vorticity (relative)']
    for var in vars:
        for year in range(1979, 2021):
            download(join(BASE_DIR, var), TYPE, var, year)

main()