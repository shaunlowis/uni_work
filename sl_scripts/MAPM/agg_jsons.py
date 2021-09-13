import json
import glob
from pathlib import Path
import os


def agg_jsons(fp, outpath, dtype='AWS'):
    agg_dict = {}

    if dtype == 'AWS':
        for path in fp:
            with open(Path(path), 'r') as data:
                data = json.load(data)
                
                for key, value in data.items():
                    if "dict" not in str(type(value)):
                        if key not in agg_dict.keys():
                            agg_dict[key] = value
                        else:
                            agg_dict[key] += value
                    else:
                        if key not in agg_dict.keys():
                            agg_dict[key] = value
                        else:
                            for subkey, subval in value.items():
                                if 'dict' not in str(type(subval)):
                                    if subkey not in agg_dict[key].keys():
                                        agg_dict[key][subkey] = subval
                                    else:
                                        agg_dict[key][subkey] += subval
                                else:
                                    for s_subkey, s_subval in subval.items():
                                        agg_dict[key][subkey][s_subkey] += s_subval

    else:
        for path in fp:
            with open(Path(path), 'r') as data:
                data = json.load(data)
                
                for key, value in data.items():
                    if "dict" not in str(type(value)):
                        if key not in agg_dict.keys():
                            agg_dict[key] = value
                        else:
                            agg_dict[key] += value
                    else:
                        if key not in agg_dict.keys():
                            agg_dict[key] = value
                        else:
                            for subkey, subval in value.items():
                                agg_dict[key][subkey] += subval

    if not os.path.exists(outpath):
        with open(outpath, 'w') as json_file:
            json.dump(agg_dict, json_file)
    else:
        response = input('File already exists at target location, overwrite? [Y/N]')
        if response == 'Y':
            with open(outpath, 'w') as json_file:
                json.dump(agg_dict, json_file)
        else:
            pass


fp_aws = glob.glob(r'/mnt/storage/Scratch/Shaun/ethan_task/jsons/AWS/*.json')
fp_aws_WOW = glob.glob(r'/mnt/storage/Scratch/Shaun/ethan_task/jsons/AWS_WOW/*.json')
fp_ODIN = glob.glob(r'/mnt/storage/Scratch/Shaun/ethan_task/jsons/ODIN_jsons/*.json')
fp_642 = glob.glob(r'/mnt/storage/Scratch/Shaun/ethan_task/jsons/ES642/*.json')

fp_AWS_WOW = []
print('here')

outpath_aws_WOW = r'/mnt/storage/Scratch/Shaun/ethan_task/agg_jsons/AWS_WOW/aws_WOW_merged.json'
outpath_aws_non_WOW = r'/mnt/storage/Scratch/Shaun/ethan_task/agg_jsons/AWS/aws_merged.json'
outpath_odin = r'/mnt/storage/Scratch/Shaun/ethan_task/agg_jsons/ODIN_jsons/odin_merged.json'
outpath_642 = r'/mnt/storage/Scratch/Shaun/ethan_task/agg_jsons/ES642/ES642_merged.json'


agg_jsons(fp_aws_WOW, outpath_aws_WOW, 'AWS')
# agg_jsons(fp_other, outpath_other, 'ODIN/642')



