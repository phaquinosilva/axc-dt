from math import floor, ceil
from pathlib import Path
from typing import Dict
from shutil import copy2

import numpy as np
import pandas as pd

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
    info = scale_data(train, test, attr_types)

    (FILE_DIR / "quantized").mkdir(parents=True, exist_ok=True)
    (FILE_DIR / f"./quantized/{dataset}").mkdir(parents=True, exist_ok=True)

    test.convert_dtypes().to_csv(
        FILE_DIR / f"./quantized/{dataset}/{dataset}_scaled.test",
        header=False,
        index=False,
        na_rep="?",
    )
    train.convert_dtypes().to_csv(
        FILE_DIR / f"./quantized/{dataset}/{dataset}_scaled.data",
        header=False,
        index=False,
        na_rep="?",
    )
    
    for attribute in attributes:
        if attr_types[attribute] == 'continuous':
            train[attribute] = pd.Series(map(lambda x: floor(x) if not np.isnan(x) else np.nan, train[attribute]))
            test[attribute] = pd.Series(map(lambda x: floor(x) if not np.isnan(x) else np.nan, test[attribute]))

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

    info.convert_dtypes().to_csv(FILE_DIR / f"./quantized/{dataset}/{dataset}.info",)

    if not (FILE_DIR / f"quantized/{dataset}/{dataset}.names").exists():
        copy2(
            FILE_DIR / f"raw/{dataset}/{dataset}.names",
            FILE_DIR / f"quantized/{dataset}/{dataset}.names",
        )
    
    if not (FILE_DIR / f"quantized/{dataset}/{dataset}_scaled.names").exists():
        copy2(
            FILE_DIR / f"raw/{dataset}/{dataset}.names",
            FILE_DIR / f"quantized/{dataset}/{dataset}_scaled.names",
        )


def scale_data(
    train: "pd.DataFrame", test: "pd.DataFrame", attribute_type: Dict[str, str]
) -> "pd.DataFrame":
    ranges = []
    name = []
    for col in train:
        # data can only be continuous or categorical -- we're only interested in continuous data
        if attribute_type[col] == "categorical":
            continue
        xmin = train[col].min()
        xmax = train[col].max()
        if test[col].min() < xmin:
            xmin = test[col].min()
        if test[col].max() > xmax:
            xmax = test[col].max()
        if xmin == xmax:
            continue

        range = xmax - xmin
        nbits = ceil(np.log2(range))

        ranges.append({"range": range, "nbits": nbits})
        name.append(col)

        scale = (
            lambda x: (x - xmin) * (2 ** 8 - 1) / (xmax - xmin)
            if not np.isnan(x)
            else np.nan
        )
        train[col] = pd.Series(map(scale, train[col]))
        test[col] = pd.Series(map(scale, test[col]))
    return pd.DataFrame(ranges, index=name)


if __name__ == "__main__":
    for name in DATASETS:
        preprocess(name)
