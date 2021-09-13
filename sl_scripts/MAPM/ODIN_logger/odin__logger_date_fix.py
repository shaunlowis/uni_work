""" Written by Shaun Lowis, date: 01/07/2019
    takes the foldername of the incorrect Odin file's folder as the first input, then the filename
    as the second input. The program outputs the corrected file with an amended month + 2, dates - 2.
    If other dates are desired, this can be changed in lines 22 and 23.
    """

from bs.core import env
import glob


def main():
    """function for fixing the Odin logger dates being incorrect"""
    foldername_input = input("Enter the logger folder name here: ")
    filename_input = input("Enter .txt log name: ")
    filepath = env.scratch("Shaun", "ODIN_logger", "processed", foldername_input, filename_input)
    output_filename = env.scratch("Shaun", "ODIN_logger", "processed", foldername_input, filename_input)
    new_lines = []
    with open(filepath) as file:
        file.readline()
        for line in file:
            line = line.split(";")
            line[15] = line[15].split("-")
            monthnum = line[15][1]
            if monthnum == "04":
                monthnum = int(line[15][1])
                monthnum += 2
                line[15][1] = str(monthnum).zfill(2)
                daynum = int(line[15][2])
                daynum -= 2
                line[15][2] = str(daynum).zfill(2)
                fixed_line = "-".join(line[15])
                line[15] = fixed_line
                lineout = ";".join(line)
                new_lines.append(lineout)
    with open(output_filename, "w") as output_file:
        for line in new_lines:
            output_file.write(line)


main()
