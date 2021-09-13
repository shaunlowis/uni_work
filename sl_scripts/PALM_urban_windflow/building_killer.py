import os
from PIL import Image
import numpy as np


INDIR = r'/home/shaun/Documents/work_dir/greg_project/palm/JOBS/sky_tower/raw_data'
INFILE = r'DSM_BA32_3603_2013.tif'

inpath = os.path.join(INDIR, INFILE)

im = Image.open(inpath)
imarray = np.array(im)
im.show()