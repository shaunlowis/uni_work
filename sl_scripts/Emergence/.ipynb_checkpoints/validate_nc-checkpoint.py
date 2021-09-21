""" Check NetCDF file to see if it is corrupted, and a valid format.
"""
import xarray as xr
import numpy as np

class Checker:
    """ The goal is to pass in a CMIP6 dataset when calling the Checker class, to run various
        checks to verify the dataset is complete and valid. This may be expanded to check any NetCDF
        So far Shaun has thought of checking the following:
        - Whether xarray can open and read the file.
        - Whether the longitudes and latitudes contain any NaN values and are continuous.
        - Whether all the variables in the file can be accessed.
    """

    def __init__(self, filepath):
        """Upon init, call checker functions.

        Args:
            Filepath ([path or pathlike object]): Path to file in question.
        """
        self.filepath = filepath
        self._xr_check()
    
    def _core_keys(self, ds):
        """Finds time, latitude, longitude keys by testing several different common key names.

        Args:
            ds (xarray dataset): Dataset whose keys are to be found.
        """
        # Add more permutations here if found
        common_datekeys = ['XTIME', 'time', 'Time']
        common_latkeys = ['lat', 'lats', 'latitude', 'Latitude', 'Lat', 'Lats']
        common_lonkeys = ['lon', 'lons', 'longitude', 'Longitude', 'Lon', 'Lons']

        datekey = [key for key in list(ds.coords) if key in common_datekeys]
        latkey = [key for key in list(ds.coords) if key in common_latkeys]
        lonkey = [key for key in list(ds.coords) if key in common_lonkeys]

        out = {}
        out['datekey'] = datekey
        out['latkey'] = latkey
        out['lonkey'] = lonkey

        print(f'Core key names: {out}')
        return out

        
    def _xr_check(self):
        """Check if the dataset can be opened with xarray. Avoid reopening it to keep the script fast.
        """
        with xr.open_dataset(self.filepath) as ds:
            keys = list(ds.coords)

            varlist = []
            varlist = [varlist.append(ds[var]) for var in keys]
            print(f'Varlist here {varlist}')

            keydict = self._core_keys(ds)
            lats = ds.coords[keydict['latkey']].values
            lons = ds.coords[keydict['lonkey']].values
            time = ds.coords[keydict['datekey']].values

            print(f'{lats}, {lons}, {time}')
            
            assert np.all(lats[1:] >= lats[:-1], axis=1)
            assert np.all(lons[1:] >= lons[:-1], axis=1)
            assert np.all(time[1:] >= time[:-1], axis=1)


def main():
    fp = r'/home/shaun/Downloads/ta_Amon_CESM2-WACCM_ssp585_r5i1p1f1_gn_201501-206412.nc'
    Checker(fp)


if __name__ == '__main__':
    main()