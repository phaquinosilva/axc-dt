from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import seaborn as sns
from skimage import measure

from matplotlib import pyplot as plt, cm, colors

# sim_data = pd.read_csv('/home/pedro/Documentos/ECLab/ACxML/SIM21/approximate 4bit comparators_decision trees - comparator characterization.csv', index_col=0)


def plot_delay_power(sim_data: "pd.DataFrame", save: bool = False) -> None:
    sim_data = sim_data.rename(columns={"delay (ps)": "Delay (ps)"})
    sim_data = sim_data.rename(columns={"power (nW)": "Power (nW)"})
    sim_data_noEXA = sim_data.drop(labels=["EXA"], axis=0, inplace=False)
    fig, ax = plt.subplots()
    df = sim_data_noEXA
    colormap = cm.seismic
    colorlist = [
        colors.rgb2hex(colormap(i)) for i in np.linspace(0, 0.9, len(df.iloc[:, 0:0]))
    ]
    for i, c in enumerate(colorlist):
        x = df["ED"][i]
        y = df["PDP (aJ)"][i]
        l = df.index[i]
        ax.scatter(x, y, label=l, s=50, c=c)
    ax.legend(ncol=3, fontsize=11)
    ax.set_xlabel("ER", fontsize=13)
    ax.set_ylabel("PDP (aJ)", fontsize=13)
    if save:
        plt.savefig()
    plt.show()


def plot_error_heatmap(
    infile_path: Path, save: bool, save_location: Optional[Path] = None
) -> None:
    def annotate_heatmap(ax, heatmap_data):
        for i in range(heatmap_data.shape[0]):
            for j in range(heatmap_data.shape[1]):
                text = ax.text(
                    j,
                    i,
                    heatmap_data[i, j],
                    ha="center",
                    va="center",
                    color="w",
                    fontsize="x-large",
                )

    if "axdc" in infile_path or "buffer" in infile_path:
        approx_comparators = "AxDC1,AxDC2,AxDC3,AxDC4,AxDC5,AxDC6".split(",")
        circuit_type = "ded"
    elif "axfc" in infile_path:
        approx_comparators = "SMA,AMA1,AMA2,AXA2,AXA3".split(",")
        circuit_type = "adder"

    df = pd.read_csv(infile_path, sep=",")
    df.rename(columns={"Unnamed: 0": "A_B"}, inplace=True)
    df["A"] = df["A_B"].apply(lambda x: x >> 4)
    df["B"] = df["A_B"].apply(lambda x: x % (2 ** 4))

    df["A+B"] = df["A"] + df["B"]
    df = df.sort_values(["A+B", "A", "B"])
    df = df.reset_index(drop=True)

    step_reduce = 2
    for approx in approx_comparators:
        heatmap_data = df[["A", "B", approx]]
        heatmap_data = heatmap_data.pivot(index="A", columns="B", values=approx)
        heatmap_data = measure.block_reduce(
            heatmap_data, (step_reduce, step_reduce), np.sum
        )
        if heatmap_data.max() == 0:
            print("skipping heatmap for adder %s with no error" % (approx))
            continue

        plt.imshow(heatmap_data, cmap="Purples", vmin=0)
        ax = plt.gca()

        ax.set_xticks(np.arange(-0.5, df["B"].max() / 2 + 1, 1), minor=False)
        ax.set_yticks(np.arange(-0.5, df["A"].max() / 2 + 1, 1), minor=False)
        print(np.arange(df["B"].max() + 1, -1, -2))
        print(np.arange(0, df["A"].max() + 2, 2))
        ax.set_xticklabels(np.arange(df["B"].max() + 1, -1, -2))
        ax.set_yticklabels(np.arange(0, df["A"].max() + 2, 2))
        annotate_heatmap(ax, heatmap_data)

        ax.grid(which="major", color="w", linestyle="-", linewidth=2)
        plt.xlabel("B value", fontsize=15)
        plt.ylabel("A value", fontsize=15)

        if save:
            plt.savefig(
                f"{save_location}heatmap_{approx}.png", dpi=800, bbox_inches="tight"
            )
            plt.close()
            plt.clf()
        else:
            plt.show()


def plot_ed_pdp(sim_data: "pd.DataFrame", save: bool = False) -> False:
    fig, ax = plt.subplots()
    colormap = cm.seismic
    colorlist = [
        colors.rgb2hex(colormap(i))
        for i in np.linspace(0, 0.9, len(sim_data.iloc[:, 0:0]))
    ]
    for i, c in enumerate(colorlist):
        x = sim_data["ED"][i]
        y = sim_data["PDP (aJ)"][i]
        l = sim_data.index[i]
        ax.scatter(x, y, label=l, s=50, c=c)
    ax.legend(ncol=3, fontsize=11)
    ax.set_xlabel("ED", fontsize=13)
    ax.set_ylabel("PDP (aJ)", fontsize=13)
    if save:
        plt.savefig("pdpxed_noEXA.png")
    else:
        plt.show()
