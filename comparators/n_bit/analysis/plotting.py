from functools import partial
from typing import Callable, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from axc_full_adders import ama1, ama2, sma
from nbit_comparators import exact_leq, leq, n_axdc1, n_axdc2

def plot_heatmap(
    n_bits: int, comparator: Callable, group: int = 2, save_name: Optional[str] = None
) -> None:
    size = 2**n_bits
    errors = np.zeros((size // group, size // group))
    count = 0
    for i in range(size):
        for j in range(size):
            if exact_leq(i, j) != comparator(a=i, b=j, n=n_bits):
                errors[i // group, j // group] += 1
                count += 1
    labels = [f"[{i*group} - {(i+1)*group-1}]" for i in range(size // group)]
    df = pd.DataFrame(100 * errors / count, index=labels, columns=labels)
    ax = sns.heatmap(df, cmap="Blues", cbar=False, annot=True, fmt=".1f")
    ax.set_ylabel("A values")
    ax.set_xlabel("B values")
    for t in ax.texts:
        t.set_text(t.get_text() + "%")
    if save_name:
        plt.savefig(save_name, format="pdf", bbox_inches="tight")
    else:
        plt.show()
    plt.close()


if __name__ == "__main__":
    from pathlib import Path

    parent = Path(__file__).parent

    n = 8
    n_group = 32

    ama1_nb = partial(leq, n=n, adder=ama1)
    ama2_nb = partial(leq, n=n, adder=ama2)
    sma_nb = partial(leq, n=n, adder=sma)
    n_axdc1_nb = partial(n_axdc1, n=n)
    n_axdc2_nb = partial(n_axdc2, n=n)

    plot_heatmap(n, ama1_nb, group=n_group, save_name=parent / f"figures/ama1_{n}b.pdf")
    plot_heatmap(n, ama2_nb, group=n_group, save_name=parent / f"figures/ama2_{n}b.pdf")
    plot_heatmap(n, sma_nb, group=n_group, save_name=parent / f"figures/sma_{n}b.pdf")
    plot_heatmap(
        n, n_axdc1_nb, group=n_group, save_name=parent / f"figures/axdc1_{n}b.pdf"
    )
    plot_heatmap(
        n, n_axdc2_nb, group=n_group, save_name=parent / f"figures/axdc2_{n}b.pdf"
    )
