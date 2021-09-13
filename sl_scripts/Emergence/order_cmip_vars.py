""" Quick and dirty script to read through a textfile of CMIP6 variables and sort them in descending order
    based off of how many files each variable has. 'file' should be a text file containing the unsorted variables.
    Written by Shaun Lowis, for Bodeker Scientific.
"""

import pandas as pd
import numpy as np
from os.path import join
import re

base = r'/mnt/storage/Scratch/Shaun/cmip6'
# Replace second of file and outfile with the names of the input and desired output
file = join(base, 'variant_label.txt')
outfile = join(base, 'sorted_variant_label.txt')

tempdict = {}
with open(file, 'r') as f:
    matchstring = r'\(\s*\+?(-?\d+)\s*\)'
    matches = re.findall(matchstring, f.read())
    lines = f.readlines()

with open(file, 'r') as f:
    lines = [line.rstrip() for line in f]
    for i, match in enumerate(matches):
        tempdict[match] = lines[i]

templist = tempdict.keys()

intlist = sorted([int(key) for key in templist])

outlist = []

for key in intlist:
    outlist.append(tempdict[str(key)])

with open(outfile, 'w') as f:
    for line in reversed(outlist):
        f.write(line + '\n')
