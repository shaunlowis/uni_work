from pathlib import Path
import glob
import subprocess

# Run on either of these for merging std and mean respectively.
std_tifs = [fp for fp in glob.glob(r'/mnt/temp/sync_to_data/global_DEM/dem7arcsec/std/**/*.tif', recursive=True)]
mean_tifs = [fp for fp in glob.glob(r'/mnt/temp/sync_to_data/global_DEM/dem7arcsec/mean/**/*.tif', recursive=True)]
out_std = r'/mnt/temp/sync_to_data/global_DEM/dem7arcsec/std/merged.tif' 
out_mean = r'/mnt/temp/sync_to_data/global_DEM/dem7arcsec/mean/merged.tif' 

merge_command = "gdal_merge.py "  +  "-o " + out_std

for tif in std_tifs:
    merge_command += " " + tif 

out = subprocess.call(merge_command, shell=True)
print(out)