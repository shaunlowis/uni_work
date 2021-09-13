from pathlib import Path
import xarray as xr
import glob
from os.path import join

fp_642 = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Deployment/Raw/NetCDF/*.nc')]
fp_642_uncert = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Deployment/Raw_with_uncert/*.nc')]

fp_aws = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/AWS*/Deployment/Raw/NetCDF/*.nc')]

base_out = r'/mnt/storage/Scratch/Shaun/ethan_task/fixed_inlets'

fp_odins = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Deployment/Raw/NetCDF/*.nc')]
odin_col1 = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Colocation_1/Raw/NetCDF/*.nc')]
odin_col2 = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/Colocation_2/Raw/NetCDF/*.nc')]

all_odins = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ODIN/**/*.nc', recursive=True)]
all_642 = [Path(fp) for fp in glob.glob(r'/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/**/*.nc', recursive=True)]

def fix_vars(fp, dtype):
    """ Go through either AWS, ES642 or ODIN 

    Args:
        fp (list of Path objects): directory.
        dtype (): [description]

    Raises:
        ValueError: [description]
    """
    for f in fp:
        with xr.open_dataset(f) as ds:
            try:
                attrs = ds['inlet_height'].attrs
                if ds['inlet_height'] > 10:
                    ds['inlet_height'] = ds['inlet_height'] / 1000
                ds['inlet_height'].attrs = attrs
            except KeyError:
                print(f'File {f} did not contain inlet_height key.')

            try:
                ds['altitude'].attrs['long_name'] = 'Geometric height above GRS1980 Geoid'
            except KeyError:
                print(f'File {f} did not contain altitude key.')

            if dtype not in ["AWS", "ES642", "ODIN", "ES642_uncert"]:
                raise ValueError('Incorrect data type! Must be one of ["AWS", "ES642", "ODIN"]')
            ds.to_netcdf(join(base_out, dtype, f.name))
            print(f'Outputted {f.name} to {base_out}')


fix_vars(all_642, 'ES642')