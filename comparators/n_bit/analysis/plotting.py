from functools import partial
from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from axc_full_adders import ama1, ama2, sma
from nbit_comparators import exact_leq, leq, n_axdc1, n_axdc2

from pathlib import Path

parent = Path(__file__).parent

# NOTE: These configurations work for a functioning LaTeX installation.
# If you don't have LaTeX installed and configure for matplotlib fonts rendering, 
# you can comment out the following lines.
size=10
params = {
        'text.usetex': True,
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
    """
    Set figure dimensions to avoid scaling in LaTeX.

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
YINMN_BLUE = "#295095"
INDIGO = "#4B0082"
BLUEBERRY = "#824BFF"

sns.set_context("paper", rc={"lines.linewidth": 2.5})
sns.set_style("darkgrid")

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=50):
    from matplotlib.colors import LinearSegmentedColormap
    new_cmap = LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

cmap = sns.color_palette("Blues", as_cmap=True)
cmap = truncate_colormap(cmap, 0.0, 0.9)

def plot_heatmap(
    n_bits: int,
    comparator: Callable,
    group: int = 2,
    save_name: Optional[str] = None,
    percentage: bool = False,
) -> None:
    """
    Plot a heatmap of the error rates of a comparator.
    """
    # TODO: Add support for parallel execution with joblib. This is important for n > 8 because the runtimes increase exponentially.
    size = 2**n_bits
    errors = np.zeros((size // group, size // group))
    count = 0
    for i in range(size):
        for j in range(size):
            if exact_leq(i, j) != comparator(a=i, b=j, n=n_bits):
                errors[i // group, j // group] += 1
                count += 1
    labels = [f"[{i*group} - {(i+1)*group-1}]" for i in range(size // group)]
    df = pd.DataFrame(errors, index=labels, columns=labels)

    perc = df.copy()
    perc = perc.div(count).multiply(100)
    annot = df.astype(int).astype(str) + "\n" + perc.round(1).astype(str) + "\%"

    ax = sns.heatmap(df+10, cmap=cmap, cbar=False, annot=annot, fmt="")
    ax.set_ylabel("$A\ values$")
    ax.set_xlabel("$B\ values$")
    if save_name:
        plt.savefig(save_name, format="pdf", bbox_inches="tight")
    else:
        plt.show()
    plt.close()


def create_hmplots():
    n = 4
    n_group = 2
    percent = False

    ama1_nb = partial(leq, n=n, adder=ama1)
    ama2_nb = partial(leq, n=n, adder=ama2)
    sma_nb = partial(leq, n=n, adder=sma)
    n_axdc1_nb = partial(n_axdc1, n=n)
    n_axdc2_nb = partial(n_axdc2, n=n)

    plot_heatmap(
        n,
        ama1_nb,
        group=n_group,
        save_name=parent / f"figures/ama1_{n}b.pdf",
        percentage=percent,
    )
    plot_heatmap(
        n,
        ama2_nb,
        group=n_group,
        save_name=parent / f"figures/ama2_{n}b.pdf",
        percentage=percent,
    )
    plot_heatmap(
        n,
        sma_nb,
        group=n_group,
        save_name=parent / f"figures/sma_{n}b.pdf",
        percentage=percent,
    )
    plot_heatmap(
        n,
        n_axdc1_nb,
        group=n_group,
        save_name=parent / f"figures/axdc1_{n}b.pdf",
        percentage=percent,
    )
    plot_heatmap(
        n,
        n_axdc2_nb,
        group=n_group,
        save_name=parent / f"figures/axdc2_{n}b.pdf",
        percentage=percent,
    )


def plot_error_rates():
    pd.read_csv(parent / "data/error_rates_axdc1.csv").plot(
        x="n",
        y="ER",
        legend=None,
        xlabel="$Bitwidth$",
        ylabel="$Error\ Rate\ (ER)$",
        figsize=set_size(300),
        color=IGUANA_GREEN,
    )
    plt.savefig(
        parent / "figures/error_rates_axdc1.pdf", format="pdf", bbox_inches="tight"
    )


if __name__ == "__main__":
    create_hmplots()
    # plot_error_rates()
