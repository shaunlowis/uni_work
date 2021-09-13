import xarray as xr
from dask.distributed import Client, LocalCluster
import os


def main():
    """ Script for splitting up large PALM files into separate z slices and/or individual variables.
        This is to make the files more managable and hopefully get VAPOR to work properly.
        This script uses dask in order to do operations on the large datafiles.
    """
    # Network directories for PALM outputs
    data_dir = r'/run/user/1000/gvfs/smb-share:server=remus.local,share=temp/' \
               r'Projects/Small Contracts/PALM_wind/JOBS/sky_tower_V2/OUTPUT'
    out_dir = r'/run/user/1000/gvfs/smb-share:server=remus.local,share=temp/' \
              r'Projects/Small Contracts/PALM_wind/JOBS/sky_tower_V2/OUTPUT/levels'
    data_file = r'sky_tower_V2_3d.001.nc'

    # Reading in data using dask
    in_data = os.path.join(data_dir, data_file)
    cluster = LocalCluster()
    client = Client(cluster)
    data = xr.open_dataset(in_data)

    new_data = xr.Dataset()
    local_out_dir = r'/home/shaun/Documents/work_dir/greg_project/data_visualisation/Auckland_out'

    # List of other variables that the PALM data has:

    #     new_data['E_UTM'] = data['E_UTM']
    #     new_data['N_UTM'] = data['N_UTM']
    #     new_data['Eu_UTM'] = data['Eu_UTM']
    #     new_data['Nu_UTM'] = data['Nu_UTM']
    #     new_data['Ev_UTM'] = data['Ev_UTM']
    #     new_data['lon'] = data['lon']
    #     new_data['lat'] = data['lat']
    #     new_data['lonu'] = data['lonu']
    #     new_data['latu'] = data['latu']
    #     new_data['lonv'] = data['lonv']
    #     new_data['latv'] = data['latv']
    #     new_data['crs'] = data['crs']
    #
    #     new_data['zu_3d'].attrs['axis'] = "Z"
    #     new_data['x'].attrs['axis'] = "X"
    #     new_data['zw_3d'].attrs['axis'] = "Z"
    #     new_data['xu'].attrs['axis'] = "X"
    #     new_data['y'].attrs['axis'] = "Y"
    #     new_data['yv'].attrs['axis'] = "Y"
    #     new_data['x'].attrs['axis'] = "X"
    #     new_data['x'].attrs['axis'] = "X"

    # Iterating through the z values of the datafile. For some reason VAPOR crashes if the NetCDF file only has 1
    # z value. As such choose a nxt value of >1.
    # Output variable initialised here.
    out_data = ''
    for i in range(40, (len(data['zu_3d'] - 1))):
        new_file = f'z{i}_u_data.nc'
        out_data = os.path.join(out_dir, new_file)
        nxt = i + 10
        new_data['u'] = data['u'][:, i:nxt, :, :]
        # new_data['v'] = data['v'][:, i:nxt, :, :]
        # new_data['w'] = data['w'][:, i:nxt, :, :]
        # new_data['ti'] = data['ti'][:, i:nxt, :, :]
        try:
            new_data.to_netcdf(out_data)
        except RuntimeError:
            print(f'The weird HDF error occurred for level {i}, try rerunning the script or something.')
        print(f'Generated {new_file}, {i}/{len(data["zu_3d"])}')

    new_data.to_netcdf(out_data)


if __name__ == '__main__':
    main()
