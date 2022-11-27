from functools import partial
from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from pathlib import Path

size=10
params = {
        'text.usetex': True,
        'font.family': "helvetica",
        'font.size': size,
        'legend.fontsize': size,
        'axes.labelsize': size,
        'axes.titlesize': size,
        'xtick.labelsize': size*0.75,
        'ytick.labelsize': size*0.75,
        'axes.titlepad': 25,
        'figure.autolayout': True,
        'figure.dpi': 100,
        'lines.markersize': 5,
        'lines.linewidth': 1
}
plt.rcParams.update(params)
px = 1/plt.rcParams['figure.dpi']  # pixel in inches

def set_size(width=483, fraction=1, subplots=(1, 1)):
    """Set figure dimensions to avoid scaling in LaTeX.

    Parameters
    ----------
    width: float or string
            Document width in points, or string of predined document type
    fraction: float, optional
            Fraction of the width which you wish the figure to occupy
    subplots: array-like, optional
            The number of rows and columns of subplots.
    Returns
    -------
    fig_dim: tuple
            Dimensions of figure in inches
    """

    # Width of figure (in pts)
    fig_width_pt = width * fraction
    # Convert from pt to inches
    inches_per_pt = 1 / 72.27

    # Golden ratio to set aesthetic figure height
    # https://disq.us/p/2940ij3
    golden_ratio = (5**.5 - 1) / 2

    # Figure width in inches
    fig_width_in = fig_width_pt * inches_per_pt
    # Figure height in inches
    fig_height_in = fig_width_in * golden_ratio * (subplots[0] / subplots[1])

    return (fig_width_in, fig_height_in)

IGUANA_GREEN = "#6DCC8C"
GRANNY_SMITH = "#AEE7A6"
ALIZARIN_CRIMSON = "#e52736"
CORNFLOWER_BLUE = "#6F90F4"
FRESH_AIR = "#ACE7F8"
LUMBER = "#FBE1CB"
LIGHT_CRIMSON = "#F4708F"
FUNKY_YELLOW = "#F4D570"
BOOGER_BUSTER = "#D1F470"

parent = Path(__file__).parent

sns.set_context("paper")
sns.set_style("darkgrid")


def plot_error_rates():
    df = pd.read_csv(parent / "data/acc_energy.csv", index_col=0)
    ax = df.plot.bar(color=[CORNFLOWER_BLUE, IGUANA_GREEN], subplots=True, layout=(1, 2), figsize=(6, 2.3))
    ax[0][0].set_title(label="")
    ax[0][1].set_title(label="")
    ax[0][0].legend().remove()
    ax[0][1].legend().remove()
    ax[0][0].set_ylabel("Accuracy ($\%$)")
    ax[0][1].set_ylabel("Energy ($pJ$)")
    plt.savefig(parent / "figures/acc_energy.pdf", format="pdf", bbox_inches="tight")


if __name__ == "__main__":
    plot_error_rates()
