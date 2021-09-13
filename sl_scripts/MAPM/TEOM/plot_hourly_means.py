""" Author: Johnny (Shaun) Lowis, for Bodeker Scientific.
    Plotting TEOM hourly mean data vs time, with the goal of data comparisons between instruments.
"""

import netCDF4 as nc
from matplotlib.font_manager import FontProperties
from matplotlib import pyplot as plt
# from users.mc_scripts.MAPM.gen_device_means import collect_hour_mean_filenames
import datetime


def read_data(filepath_teom, filepath_642):
    with nc.Dataset(filepath_teom, mode='r') as data_teom:
        teom_time = nc.num2date(data_teom.variables["time"][:],
                                data_teom.variables['time'].units) - datetime.timedelta(hours=1)
        teom_pm = data_teom.variables["pm2.5"][:]

    with nc.Dataset(filepath_642, mode='r') as data_642:
        ES642_time = nc.num2date(data_642.variables["time"][:], data_642.variables['time'].units)
        ES642_pm = data_642.variables["pm2.5"]

    return teom_time, teom_pm, ES642_time, ES642_pm


def plot_data(teom_time, teom_pm, ES642_time, ES642_pm, instrument_name):

    font = FontProperties()
    font.set_size(12)
    fig, axs = plt.subplots(1, figsize=(12, 8))

    teom_line = axs.plot(teom_time, teom_pm, color='red')
    ES642_line = axs.plot(ES642_time, ES642_pm, color='blue')
    plt.title(f'Woolston TEOM vs {instrument_name}: pm2.5 vs. time', fontsize=14)
    plt.xlabel('Time (YYYY-MM-DD)', fontproperties=font)
    plt.ylabel('pm2.5 ($\mu$g/m$^{3}$)', fontproperties=font)
    labels = ['Woolston TEOM line', f'{instrument_name} line']
    plt.legend((teom_line, ES642_line), labels=labels, fontsize=12)
    fig.tight_layout()

    plt.show()


def plot_teom_vs_642s(teom_time, teom_pm, ES642_fps):
    font = FontProperties()
    font.set_size(12)

    for i, ES642_fp in enumerate(ES642_fps):
        with nc.Dataset(ES642_fp) as data_642:
            fig, axs = plt.subplots(1, figsize=(12, 8))
            teom_line = axs.plot(teom_time, teom_pm, color='red')
            keys = ['pm2.5', 'air_pressure', 'air_temperature', 'relative_humidity']
            ES642_time = nc.num2date(data_642.variables["time"][:], data_642.variables['time'].units)
            ES642_line = axs.plot(ES642_time, data_642.variables[keys[0]][:], color='blue')
            plt.title(f'Colocation 1; Woolston TEOM vs ES-642_{data_642.sensor_name}: '
                      f'{data_642.variables[keys[0]].name} vs. time', fontsize=14)
            plt.xlabel('Time (YYYY-MM-DD)', fontproperties=font)
            plt.ylabel(f'{data_642.variables[keys[0]].name} ($\mu$g/m$^{3}$)', fontproperties=font)
            labels = ['Woolston TEOM line', f'ES642_{data_642.sensor_name} line']
            plt.legend((teom_line, ES642_line), labels=labels, fontsize=12)
            fig.tight_layout()
        plt.show()


def main():
    # filepath_teom = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/TEOM/Colocation_1/Raw/NetCDF"
    # colocation1_teom = filepath_teom + "/" + r"TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc"
    # filepath_642 = r"/mnt/temp/Projects/MAPM/Data_Permanent/MAPM_campaign/ES642/Colocation_1/Averaged/NetCDF"
    # colocation1_642 = filepath_642 + "/" + r"ES-642_DM2_Christchurch2019_Colocation_1_averaged.nc"
    # teom_time, teom_pm, ES642_time, ES642_pm = read_data(colocation1_teom, colocation1_642)
    # # plot_data(teom_time, teom_pm, ES642_time, ES642_pm)
    # fp642 = collect_hour_mean_filenames()
    # plot_teom_vs_642s(teom_time, teom_pm, fp642)

    es642_local_fp = r'/home/slowis/Documents/wrkdir/es_colo1/NetCDF/ES' \
                     r'-642_DM1_Christchurch2019_Colocation_1_averaged.nc '
    teom_local_fp = r'/home/slowis/Documents/wrkdir/woolston/TEOM_Woolston_Christchurch2019_Colocation_1_raw.nc'

    teom_time, teom_pm, ES642_time, ES642_pm = read_data(teom_local_fp, es642_local_fp)
    plot_teom_vs_642s(teom_time, teom_pm, es642_local_fp)


if __name__ == '__main__':
    main()
