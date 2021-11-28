from typing import Dict, Tuple

import numpy as np
import pandas as pd
from fxpmath import Fxp

NUMERICAL = ["breast-cancer", "iris", "forest"]
MIXED = ["adult", "heart-disease", "arrhythmia"]
DATASETS = NUMERICAL + MIXED


def process(dataset: str, bits: int = 8, signed: bool = False) -> None:
    """
    Process a dataset in the format used in C5.0.
    Maps datapoints to fixed point values to be used with fixed bit width
    arithmetic blocks.
    :param dataset:
        A string with the name of the dataset. The dataset will be searched in a directory
        'raw/{dataset}/{dataset}/' in the same root as this file
    :param bits:
        An integer with the number of bits to be used in quantization
    :param signed:
        A boolean flag used to set quantization for signed and unsigned integers

    """
    attributes = []
    attr_types = {}
    with open("./raw/%s/%s.names" % (dataset, dataset), "r") as f:
        for line in f.readlines()[2:]:
            attr_name, attr_type = line.split(":")
            attr_name = attr_name.replace(" ", "")
            attributes.append(attr_name)
            attr_types[attr_name] = (
                "continuous" if "continuous" in attr_type else "categorical"
            )
    # print(attributes)
    # print(attr_types)
    # read training data into dataframe
    train = pd.read_csv(
        "./raw/%s/%s.data" % (dataset, dataset),
        names=attributes,
        na_values="?",
        na_filter=True,
    )
    print(train)
    # read test dataset into dataframe
    try:
        test = pd.read_csv(
            "./raw/%s/%s.test" % (dataset, dataset),
            names=attributes,
            na_values="?",
            na_filter=True,
        )
    except FileNotFoundError:
        print("No test file found...")

    if signed:
        make_values_positive(train, test)
    # print(train)
    preprocess_values(name=dataset, train=train, test=test, bits=bits, signed=signed)

    test.convert_dtypes().to_csv(
        "./quantized/%s/%s.test" % (dataset, dataset),
        header=False,
        index=False,
        na_rep="?",
    )
    train.convert_dtypes().to_csv(
        "./quantized/%s/%s.data" % (dataset, dataset),
        header=False,
        index=False,
        na_rep="?",
    )


def preprocess_values(
    name: str,
    train: "pd.DataFrame",
    test: "pd.DataFrame",
    bits: int,
    signed: bool = False,
) -> Tuple["pd.DataFrame", "pd.DataFrame"]:
    """Quantize training values in dataset using a fraction that generates
    the least error in comparison with non quantized data.

    :param name:
        A string with the name of the dataset
    :param test:
        A DataFrame with the data read from .data file
    :param bits:
        An integer with the number of bits to be used in the target application
    :param signed:
        A boolean flag if quantization is to happen with signed or unsigned fixed point values

    :return:
        A DataFrame with the new quantized dataset to be written on a new .data file
    """
    fraction: Dict = dict()
    nums = [
        col
        for col in train
        if (str(train.dtypes[col]) == "float64" or (str(train.dtypes[col]) == "int64"))
    ]
    # print(floats)
    print(f"{len(nums)} columns to run quantization")
    # Test if quantization is needed, rather than fixed point
    for col in nums:
        # print(train)
        train_max = train[col].max()
        test_max = max(test[col])

        if train_max >= 2 ** bits or test_max >= 2 ** bits:
            print(train_max)
            print(test_max)
            print()
            print(f"running quantization on column {col}...")
            n_shifts = lambda x: len(bin(int(x))[2:]) - bits
            shifts = n_shifts(test_max) if test_max > train_max else n_shifts(train_max)
            print(shifts)
            fix_representation = lambda x: int(x) >> shifts
            test[col] = (test[col]).map(fix_representation, na_action="ignore")
            train[col] = (train[col]).map(fix_representation, na_action="ignore")
            fraction[col] = {'size': None}

    for col in nums:
        if col in list(fraction.keys()):
            print(f"skipping quantized column {col}")
            continue
        if col in train.select_dtypes("integer"):
            print(f"skip integer column {col}")
            continue
        # Quantization will not be needed, use fixed point
        min_error = np.Inf
        best_frac = 0
        for frac_size in range(bits + 1):
            for it, df in enumerate([train, test]):
                # print(f"testing frac_size={frac_size} in {col}")
                col_frac = df[col].map(
                    lambda x: Fxp(
                        x, signed=False, n_word=bits, n_frac=frac_size
                    ).get_val(),
                    na_action="ignore",
                )
                error = (df[col] - col_frac).sum() ** 2
                if error < min_error:
                    best_frac = frac_size
                    min_error = error
                    fraction[col] = {"error": min_error}
        fix_rep = lambda x: int(
            Fxp(x, signed=False, n_word=bits, n_frac=best_frac).bin(), base=2
        )
        train[col] = train[col].map(fix_rep, na_action="ignore")
        test[col] = test[col].map(fix_rep, na_action="ignore")
        fraction[col] = {"size": best_frac}


    fraction_pd = pd.DataFrame(fraction)
    fraction_pd.to_csv(f"./quantized/{name}/{name}.fraction")
    return fraction


def make_values_positive(
    train: "pd.DataFrame", test: "pd.DataFrame"
) -> Dict[str, float]:
    print("removing signed representation")
    non_obj = [
        col
        for col in train
        if (str(train.dtypes[col]) == "float64" or str(train.dtypes[col]) == "int64")
    ]
    min_col = {}
    for col in non_obj:
        train_min = float(min(train[col]))
        test_min = float(min(test[col]))
        min_col[col] = train_min if train_min < test_min else test_min
        if min_col[col] < 0:
            train[col] = train[col] - min_col[col]
            test[col] = test[col] - min_col[col]


if __name__ == "__main__":
    for name in ['heart-disease']:
        process(name, signed=True)
