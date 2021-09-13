#%%

import matplotlib as mpl
from matplotlib import pyplot as plt
import xarray as xr
from os.path import join
import numpy as np
#import xesmf as xe
from scipy.interpolate import RegularGridInterpolator
from pathlib import Path


#%%
INPUT_FOLDER = Path('/mnt/temp/sync_to_data/global_DEM/esa_lcm/')

#%%

with xr.open_dataset(INPUT_FOLDER / 'ESACCI-LC-L4-LCCS-Map-300m-P1Y-2015-v2.0.7b.nc') as ds:
    data = ds['lccs_class'].values
    lats_in = ds['lat'].values
    lons_in = ds['lon'].values



#%%
lats = np.arange(-90, 90+1e-6, 0.25/64)
lons = np.arange(-180, 180, 0.25/64)

data_out = np.zeros((len(lats), len(lons)))

# data_out = xr.Dataset({'lat': (['lat'], lats), 'lon': (['lon'], lons),})
#d_out = np.array([lats, lons])

#%%

x_chunks = 8
y_chunks = 8

n_x = len(lons) // x_chunks
n_y = len(lats) // y_chunks

n_x_in = len(lons_in) // x_chunks
n_y_in = len(lats_in) // y_chunks


#%%
my_interp = RegularGridInterpolator((-lats_in, lons_in), data, bounds_error=False)


#%%
#data_out = my_interp((-lats.reshape(-1), lons.reshape(-1))
#dat_in = np.array([xx, yy]).T

#%%
for x in range(0, x_chunks):
    for y in range(0, y_chunks):

        y_1 =  y*n_y
        y_2 = (y+1)*n_y
        x_1 = x*n_x
        x_2 = (x+1)*n_x 

        if y == y_chunks - 1:
            y_2 = len(lats)
        
        if x == x_chunks - 1:
            x_2 = len(lons)

        # Trying to add chunked data out as z dimension to meshgrid, indexing ij
        # Also try indexing xy next
        xx, yy = np.meshgrid(lons[x_1:x_2], lats[y_1:y_2])
        out_grid = np.array([xx.reshape(-1), yy.reshape(-1)]).T
        temp_data = my_interp(out_grid).reshape(xx.shape)
        data_out[y_1:y_2, x_1:x_2] = temp_data
        print(x,y)
    #     break
    # break
#%%
out_ds = xr.Dataset({'lat': (['lat'], lats), 'lon': (['lon'], lons,), 
                    'lcc' : (['lat', 'lon'], data_out)})

#%%
out_ds.to_netcdf(r'/mnt/temp/sync_to_data/global_DEM/regrid.nc')
#%%
        # out_grid = np.array([xx, yy]).T
        # temp_data = my_interp(out_grid)

        # data_out[y_1:y_2, x_1:x_2] = temp_data.T
        # print(x,y)

# #%%
# d_out[y_1:y_2, x_1:x_2] = temp_data.T
#%%
plt.figure(figsize=(20, 18))
plt.pcolormesh(data_out)
plt.savefig('regrid.png')
plt.close()
# my_interp = RegularGridInterpolator((-lats_in, lons_in), data)
# #%%
# xx, yy = np.meshgrid(lons, -lats)
# out_grid = np.array([xx, yy])
# #%%
# out_grid.shape
# #%%
# my_interp(np.array([-lats, lons]))


# #%%
# def regrid(ds_in, ds_out,  **kwargs):
#     """Regridding function that should be scalable for higher resolution data.

#     Args:
#         ds (xarray dataset): Target xarray dataset to be regridded.
#         lat (np array): New longitude grid that the target ds should be in.
#         lon (np array): New lat grid that the target ds should be in.
#         data (xarray dataarray): xarray dataset variable to be targeted in the regridding.
#     **kwargs:
#         Any valid argument to xe.Regridder(), expects method, i.e. one of: 
#         ['bilinear', 'conservative', 'nearest_s2d', 'nearest_d2s', 'patch']
#     """
#     regridder = xe.Regridder(ds, ds_out, **kwargs)
#     return regridder

# #%%
# for x in range(0, x_chunks):
#     for y in range(0, y_chunks):
#         if y == y_chunks - 1:
#             lat_c = lats[y*n_y:]
#         else:
#             lat_c = lats[y*n_y:(y+1)*n_y]
        
#         if x == x_chunks - 1:
#             lon_c = lons[x*n_x_in:]
#         else:
#             lon_c = lons[x*n_x_in:(x+1)*n_x_in]

#         in_lon = lons[x*n_x:(x+1)*n_x]

#         y_in_1 =  y*n_y_in - 10
#         y_in_2 = (y+1)*n_y_in + 10
#         x_in_1 = x*n_x_in - 10
#         x_in_2 = (x+1)*n_x_in + 10

#         x_in_1 = max(x_in_1, 0)
#         x_in_2 = min(x_in_2, len(lons_in))
#         y_in_1 = max(y_in_1, 0)
#         y_in_2 = min(y_in_2, len(lats_in))

#         # n_y_in = int(n_y_in)
#         # n_x_in = int(n_x_in)

#         #ds['lccs_class'][x*n_x_in:(x+1)*n_x_in, y*n_y_in:(y+1)*n_y_in],
        
#         # regridder = xe.Regridder({'lat' : lats_in[y_in_1:y_in_2], 'lon' : in_lon[x_in_1:x_in_2]}, 
#         #                         {'lat' : lat_c, 'lon' : lon_c}, 'nearest_s2d')
        
#         # #data_out.values[y*n_y:(y+1)*n_y, x*n_x:(x+1)*n_x] = regridder(ds['lccs_class'][x*n_x_in:(x+1)*n_x_in, y*n_y_in:(y+1)*n_y_in])
#         # print(f'Completed section {x+y}')
#         break
#     break
# #%%
# y_in_1
# #data_out.to_netcdf(r'/mnt/temp/sync_to_data/global_DEM/esa_lcm/regridded.nc')
# # %%
# data.shape
# # %%
# ds_out = xr.Dataset({'lat': (['lat'], lats), 'lon': (['lon'], lons)})
# regridder = xe.Regridder({'lat' : lats_in, 'lon' : lons_in}, ds_out, method='nearest_s2d')
# # %%

# %%
