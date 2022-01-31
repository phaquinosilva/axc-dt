from math import floor
from pathlib import Path
from typing import Dict
import numpy as np
import pandas as pd
from pyparsing import ZeroOrMore

NUMERICAL = ["breast-cancer", "iris", "forest"]
MIXED = ["adult", "heart-disease", "arrhythmia"]
DATASETS = NUMERICAL + MIXED

FILE_DIR = Path(__file__).parent


def preprocess(dataset: str, bits: int = 8, signed: bool = False) -> None:
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
    with (FILE_DIR / f"./raw/{dataset}/{dataset}.names").open("r") as f:
        for line in f.readlines()[2:]:
            attr_name, attr_type = line.split(":")
            attr_name = attr_name.replace(" ", "")
            attributes.append(attr_name)
            attr_types[attr_name] = (
                "continuous" if "continuous" in attr_type else "categorical"
            )
    # read training data into dataframe
    train = pd.read_csv(
        FILE_DIR / f"./raw/{dataset}/{dataset}.data",
        names=attributes,
        na_values="?",
        na_filter=True,
    )
    # read test dataset into dataframe
    try:
        test = pd.read_csv(
            FILE_DIR / f"./raw/{dataset}/{dataset}.test",
            names=attributes,
            na_values="?",
            na_filter=True,
        )
    except FileNotFoundError:
        # TODO: Generate test file if not found
        ("No test file found...")

    print(dataset)
    scale_data(train, test, attr_types)
    # print(test)
    test.convert_dtypes().to_csv(
        FILE_DIR / f"./quantized/{dataset}/{dataset}.test",
        header=False,
        index=False,
        na_rep="?",
    )
    train.convert_dtypes().to_csv(
        FILE_DIR / f"./quantized/{dataset}/{dataset}.data",
        header=False,
        index=False,
        na_rep="?",
    )


def scale_data(train: "pd.DataFrame", test: "pd.DataFrame", attribute_type: Dict[str, str]) -> "pd.DataFrame":
    numeric = [
        col
        for col in train
        if (str(train.dtypes[col]) == "float64" or (str(train.dtypes[col]) == "int64"))
    ]
    for col in numeric:
        if attribute_type[col] == 'categorical':
            continue
        xmin = train[col].min()
        xmax = train[col].max()
        if test[col].min() < xmin:
            xmin = test[col].min()
        if test[col].max() > xmax:
            xmax = test[col].max()
        if xmin == xmax and xmax < 2**8:
            continue

        scale = (
            lambda x: floor((x - xmin) * 2 ** 8 / (xmax - xmin))
            if not np.isnan(x)
            else np.nan
        )
        train[col] = pd.Series(map(scale, train[col]))
        test[col] = pd.Series(map(scale, test[col]))


if __name__ == "__main__":
    for name in DATASETS:
        preprocess(name)
