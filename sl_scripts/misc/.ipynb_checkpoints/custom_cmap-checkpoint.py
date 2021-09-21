""" Author: Johnny (Shaun) Lowis, for Bodeker Scientific.
    Script for creating new colormaps using dynamic ranges and color options.
    "reverse_colormap" was taken from: https://stackoverflow.com/questions/3279560/reverse-colormap-in-matplotlib
    All credit to "Mattijn" for this function.
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import palettable
import colorcet as cc


def linear_segmented(seq, mapname):
    """Return a LinearSegmentedColormap
    seq: a sequence of floats and RGB-tuples. The floats should be increasing
    and in the interval (0,1).
    """
    seq = [(None,) * 3, 0.0] + list(seq) + [1.0, (None,) * 3]
    cdict = {'red': [], 'green': [], 'blue': []}

    for i, item in enumerate(seq):
        if isinstance(item, float):
            r1, g1, b1 = seq[i - 1]
            r2, g2, b2 = seq[i + 1]
            cdict['red'].append([item, r1, r2])
            cdict['green'].append([item, g1, g2])
            cdict['blue'].append([item, b1, b2])

    return mcolors.LinearSegmentedColormap(mapname, cdict)


def new_diverge(cmap_name, low, high):
    """ Uses the linear_segmented function, with three input colours
    to create a diverging colormap with white in the middle.
    """
    low = mcolors.ColorConverter().to_rgb(low)
    high = mcolors.ColorConverter().to_rgb(high)
    white = mcolors.ColorConverter().to_rgb('white')
    return linear_segmented([low, white, 0.5, white, high], cmap_name)


def color_range(list_vals, list_colors, cmapname, cust_range=None):
    """ Creates a custom color range for the colormap object, at specified
    input values as given by the user. The inputs of this function should be:
    :param list_vals: The complete range of the dataset, should be in form: [lower_bound, middle, upper_bound]
                      (where the bounds refer to the lower and upper extremes of the datarange.)
    :param list_colors: A list object of input colours in string format: ['blue', 'white', 'red']
    :param cmapname: The name of the new colormap to be created.
    :param cust_range: The custom input range that the user wants the cmap to correspond to. Should be a list:
                       For the custom range list: [x1, x2, x3, x4, x5]
                       This is for divergent plot use.
                       x1 = lower limit of mapped data, i.e. "data floor".
                       x2 = lower colour limit.
                       x3 = upper colour limit.
                       x4 = intensity of the middle value.
                       x5 = upper limit of mapped data, i.e. "data ceiling".

    The relationship between the input values of cust_range and the outputted colormap appears to show that x2
    is related to the intensity of the 'lower value colour', x3 the 'upper value colour' and x4 the middle value
    as per a diverging colormap. x1 and x5 seem to act in the same way as the vmin and vmax arguments of a
    matplotlib colormap/pcolormesh/scatter object's kwargs. All of these values indicate their intensity to
    correspond to their values/range of the datavalues.

    """
    norm = plt.Normalize(min(list_vals), max(list_vals))
    tuples = list(zip(map(norm, list_vals), list_colors))
    cmap = mcolors.LinearSegmentedColormap.from_list("", tuples)

    if cust_range is not None:
        colors = cmap(plt.Normalize(min(cust_range), max(cust_range))(np.array(cust_range)))
        norm = plt.Normalize(min(cust_range), max(cust_range))
        tuples = list(zip(map(norm, list_vals), colors))
        cmap = mcolors.LinearSegmentedColormap.from_list("", tuples)

    cmap.name = cmapname

    return cmap


def plot_examples(cms):
    """ Plots an input list of colormaps against eachother for comparison.
    :param cms: A list of matplotlib colormap objects, can include any recognised colormap: ['viridis', 'jet']
    """
    np.random.seed(19680801)
    data = np.random.randn(30, 30)

    fig, axs = plt.subplots(1, len(cms), figsize=(6 + (len(cms)*1.5), 3 + (len(cms)/3)))

    for i, [ax, cmap] in enumerate(zip(axs, cms)):
        psm = ax.pcolormesh(data, cmap=cmap, rasterized=True)
        ax.set_title(f'Colormap plot {i}')

        try:
            ax.set_title(cmap.name)
        except AttributeError:
            ax.set_title(cmap)

        ticks = np.linspace(0, 9, 9)

        cbar = fig.colorbar(psm, ax=ax)
        cbar.ax.set_yticklabels(ticks)
        fig.tight_layout()

    plt.show()


def lin_to_diverge(cmap1, cmap2, cmapname):

    try:
        name = cmapname.name
    except AttributeError:
        name = cmapname

    in1 = plt.cm.get_cmap(cmap1)(np.linspace(0, 1, 129))
    in2 = plt.cm.get_cmap(cmap2)(np.linspace(0, 1, 129))

    combine = np.vstack((in1, in2))
    outmap = mcolors.LinearSegmentedColormap.from_list(name, combine)
    return outmap


def reverse_colourmap(cmap, name = 'my_cmap_r'):
    """
    In:
    cmap, name
    Out:
    my_cmap_r

    Explanation:
    t[0] goes from 0 to 1
    row i:   x  y0  y1 -> t[0] t[1] t[2]
                   /
                  /
    row i+1: x  y0  y1 -> t[n] t[1] t[2]

    so the inverse should do the same:
    row i+1: x  y1  y0 -> 1-t[0] t[2] t[1]
                   /
                  /
    row i:   x  y1  y0 -> 1-t[n] t[2] t[1]
    """
    reverse = []
    k = []

    for key in cmap._segmentdata:
        k.append(key)
        channel = cmap._segmentdata[key]
        data = []

        for t in channel:
            data.append((1-t[0],t[2],t[1]))
        reverse.append(sorted(data))

    LinearL = dict(zip(k,reverse))
    my_cmap_r = mpl.colors.LinearSegmentedColormap(name, LinearL)
    return my_cmap_r


def main():
    """ Some example code below for how to initialise and call above functions:
    """
    cvals = [-12., 0, 12]
    colors = ["red", "white", "blue"]

    cust_range1 = [-12, 0, 10, 0, 12]
    another_one = color_range(cvals, colors, 'No custom range')
    and_another_one = color_range(cvals, colors, cust_range1, cust_range1)
    plot_examples([another_one, and_another_one, 'viridis'])

    ice_20 = palettable.cmocean.sequential.get_map('Ice_20')
    oslo = palettable.scientific.sequential.get_map('Oslo_20')
    Blues7_7 = palettable.lightbartlein.sequential.get_map('Blues7_7')
    blues7_7_r = reverse_colourmap(Blues7_7.mpl_colormap)

    merge1 = lin_to_diverge(blues7_7_r, 'hot_r', 'blues7_7')
    merge2 = lin_to_diverge(ice_20.mpl_colormap, 'hot_r', ice_20.name)
    merge3 = lin_to_diverge(oslo.mpl_colormap, 'hot_r', oslo.mpl_colormap.name)
    plot_examples([merge1, merge2, merge3])


if __name__ == '__main__':
    main()
