import functools
from typing import Callable

import pandas as pd

from comparators.n_bit.analysis.nbit_comparators import (ama1, ama2, exact_leq,
                                                         leq, n_axdc1, n_axdc2,
                                                         sma)


def _compute_metrics(n_bits: int, comparator: Callable) -> "pd.Series":
    size = 2**n_bits

    def count_errors(i):
        counter = 0
        for j in range(size):
            if exact_leq(i, j) != comparator(a=i, b=j, n=n_bits):
                counter += 1
        return counter

    from time import time

    if n_bits >= 8:
        from joblib import Parallel, delayed

        s = time()
        error_counter = sum(
            Parallel(n_jobs=8)(delayed(count_errors)(i) for i in range(size))
        )
        runtime = time() - s
    else:
        s = time()
        error_counter = sum(count_errors(i) for i in range(size))
        runtime = time() - s
    return pd.Series(
        {
            "ED": error_counter,
            "ER": 100 * error_counter / 2 ** (2 * n_bits),
            "runtime": runtime,
        }
    )


def calculate_error_metrics(n_bits):
    ADDERS = [sma, ama1, ama2]
    DEDICATED = [n_axdc1, n_axdc2]
    COMPARATORS = DEDICATED  # + ADDERS
    COMPARATOR_NAMES = [comparator.__name__ for comparator in COMPARATORS]
    rates = []

    for comparator in COMPARATORS:
        print(f"Computing metrics for {n_bits} bit {comparator.__name__}")
        if comparator in ADDERS:
            comparator = functools.partial(leq, adder=comparator)
        rates.append(_compute_metrics(n_bits, comparator))
    return pd.concat(rates, axis=0, keys=COMPARATOR_NAMES)
