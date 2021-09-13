import os
import random as rand
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import netCDF4 as nc

STATUS = 'Corrected'

def plot_sats(in_dir, out_dir):
    """ Creating a combined plot of all satellites in in_dir, for each 5 degree latitude band between -90 and 90,
        and for both O3_nd and O3_vmr datatypes, at a random level. Outputted files are saved in out_dir.
    """

    sat_dir = in_dir
    # List of satellite directories
    sats = [name for name in os.listdir(sat_dir) if os.path.isdir(os.path.join(sat_dir, name))]
    print(f'List of satellites: {sats}')
    lat_bands = np.arange(-90, 95, 5)
    #lat_bands = np.arange(-30, 30, 5)
    level = rand.randint(10, 50)  # 0, 69
    #level = 20
    print('Plotting level ', level)
    # Colors to be used for the visualisation
    colors = ['#ff3333', '#ffcc33', '#99ff33', '#33ff66', '#33ffff', '#3366ff', '#9933ff', '#ff33cc', '#0000ff']

    # Plot both data types:
    for d_type in ['O3_nd', 'O3_vmr']:
        try:
            for n, band in enumerate(lat_bands):
                print(f'Plotting for band: {band} to {lat_bands[n + 1]}')

                for i, sat in enumerate(sats):
                    print(f'Plotting {sat}')
                    gph_dir = os.path.join(sat_dir, sat, 'gph')
                    # Get all the datafiles for plotting
                    files = [name for name in os.listdir(gph_dir) if os.path.isfile(os.path.join(gph_dir, name))]

                    if STATUS is 'Corrected':
                        new_files = []
                        for file in files:
                            if 'lvl_'+str(level) in file:
                                new_files.append(file)
                        files = new_files

                    for file in files:
                        file = os.path.join(gph_dir, file)
                        data = nc.Dataset(file)
                        if data.dimensions['time'].size == 1:
                            data.close()
                            continue
                        data.close()
                        data = xr.open_dataset(file)

                        # Slice the data from the current level
                        if STATUS is 'Corrected':
                            lats = data['latitude'][:].values
                        else:
                            lats = data['latitude'][:, level].values
                        no_nan_lats = lats[~np.isnan(lats)]

                        # Slice the data from the current latitude band
                        idxs = np.where((no_nan_lats >= band) & (no_nan_lats < lat_bands[n + 1]))

                        # Scale the data and filter out any NaN values
                        if d_type == 'O3_nd':
                            if STATUS is 'Corrected':
                                y1vals = data[d_type].values[:, 0]
                                y1vals = y1vals[idxs[0]]
                            else:
                                y1vals = data[d_type].values
                                y1vals = y1vals[idxs[0], level]
                            y1vals = y1vals * 1e-12
                            data_mask = ~np.isnan(y1vals)
                            y1vals = y1vals[data_mask]
                        else:
                            if STATUS is 'Corrected':
                                y1vals = data[d_type].values[:, 0]
                                y1vals = y1vals[idxs[0]]
                            else:
                                y1vals = data[d_type].values
                                y1vals = y1vals[idxs[0], level]
                            y1vals = y1vals * 1e6
                            data_mask = ~np.isnan(y1vals)
                            y1vals = y1vals[data_mask]

                        if sat == "SONDE":
                            xvals = data['time'].values
                            if STATUS is 'Corrected':
                                xvals = xvals[idxs[0]]
                            else:
                                xvals = xvals[idxs[0], level]
                            xvals = xvals[data_mask]
                        else:
                            xvals = data['time'].values
                            xvals = xvals[idxs[0]]
                            xvals = xvals[data_mask]

                        # Add the data in a colour for each satellite to the combined plot
                        plt.rcParams["figure.figsize"] = (20, 6)
                        plt.scatter(xvals, y1vals, s=2, c=colors[i])
                        plt.title(f'Level {level} between latitude {band}$^\circ$ and {lat_bands[n + 1]}$^\circ$, {d_type}')
                        plt.xlabel('Time')

                        if d_type == 'O3_nd':
                            plt.ylabel(r'Ozone number density x$10^{12}$')
                        else:
                            plt.ylabel(r'Ozone volume mixing ratios x$10^-6$')

                        plt.tight_layout()
                        data.close()

                artists = []

                for j, color in enumerate(colors):
                    artists.append(mpatches.Patch(color=color, label=sats[j]))

                plt.legend(handles=artists)
                outpath = os.path.join(out_dir, f'level{level}_{n}')
                plt.savefig(outpath)

        except IndexError:
            continue

def main():
    if STATUS == 'Corrected':
        in_dir = r'/mnt/temp/BDBP/version_2.1/Data/Corrected/'
        out_dir = r'/mnt/temp/BDBP/plots/corrected/'
    else:
        in_dir = r'/mnt/temp/BDBP/version_2.1/Data/Prepared/Data/'
        out_dir = r'/mnt/temp/BDBP/plots/prepared/'
    plot_sats(in_dir, out_dir)


if __name__ == '__main__':
    main()
