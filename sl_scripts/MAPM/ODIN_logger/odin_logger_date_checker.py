"""Program for finding incorrect datavalues in ODIN logger files
   Author: Shaun Lowis, Date: July 11, 2019, For Bodeker Scientific."""

import os


def main():
    """Checks the ODIN data files in a specified filepath to see if their dates are correct
    :return: incorrect datafiles' filepath
    """

    filepath = r"/mnt/shareddrive/Projects/MAPM/Data/ODIN/backup"

    for folder in os.listdir(filepath):
        if folder.startswith("ODIN-SD-2018-"):
            for file_name in os.listdir(filepath + "/" + folder):
                for data_file in os.listdir(filepath + "/" + folder + "/" + file_name):
                    if data_file == "DATA.TXT":
                        file_location = filepath + "/" + folder + "/" + file_name + "/" + data_file
                        lines = open(file_location)
                        lines = lines.readlines()
                        lines = lines[1]
                        lines = lines.split(";")
                        if lines[15] != "2000/01/01":
                            print("This/these file(s) have an error in their start date(s)")
                            print(file_location)


main()
