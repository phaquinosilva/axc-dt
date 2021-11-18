from typing import Dict
import pandas as pd
import numpy as np
from fxpmath import Fxp


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
    f = open("./raw/%s/%s.names" % (dataset, dataset), "r")
    for line in f.readlines()[2:]:
        attr_name, _ = line.split(":")
        attr_name = attr_name.replace(" ", "")
        attributes.append(attr_name)
    # read dataset into dataframe
    df = pd.read_csv("./raw/%s/%s.data" % (dataset, dataset), names=attributes)
    col_min = make_training_values_positive(df)
    info = quantize_training_values(dataset, df, bits, signed)
    # try processing training values
    try:
        test = pd.read_csv("./raw/%s/%s.test" % (dataset, dataset), names=attributes)
        make_test_values_positive(test, col_min)
        quantize_test_values(test, info, bits, signed)
        test.to_csv(
            "./quantized/%s/%s.test" % (dataset, dataset), header=False, index=False
        )
    except FileNotFoundError:
        print("No test file found...")
    finally:
        df.to_csv(
            "./quantized/%s/%s.data" % (dataset, dataset), header=False, index=False
        )


def quantize_training_values(
    name: str, df: "pd.DataFrame", bits: int, signed: bool = False
) -> "pd.DataFrame":
    """Quantize training values in dataset using a fraction that generates
    the least error in comparison with non quantized data.

    :param name:
        A string with the name of the dataset
    :param df:
        A DataFrame with the data read from .data file
    :param bits:
        An integer with the number of bits to be used in the target application
    :param signed:
        A boolean flag if quantization is to happen with signed or unsigned fixed point values

    :return:
        A DataFrame with the new quantized dataset to be written on a new .data file
    """
    info = {}
    floats = [col for col in df if (str(df.dtypes[col]) == "float64")]
    for col in floats:
        info[col] = {}
        min_erro = np.Inf
        best_frac = 0
        col_orig = df[col]
        for frac_size in range(bits):
            col_frac = col_orig.apply(
                lambda x: Fxp(x, signed=signed, n_word=bits, n_frac=frac_size).get_val()
            )
            erro = (col_orig - col_frac) ** 2
            if max(erro) < min_erro:
                best_frac = frac_size
                min_erro = max(erro)
                info[col]["error"] = min_erro
        int_col = col_orig.apply(
            lambda x: int(
                Fxp(x, signed=signed, n_word=bits, n_frac=best_frac).bin(), base=2
            )
        )
        df[col] = int_col
        info[col]["frac_size"] = best_frac
    info_pd = pd.DataFrame(info)
    info_pd.to_csv("./quantized/%s/%s.info" % (name, name))
    return info


def quantize_test_values(
    df: "pd.DataFrame", info: "pd.DataFrame", bits: int, signed: bool = False
) -> None:
    floats = [col for col in df if (str(df.dtypes[col]) == "float64")]
    for col in floats:
        best_frac = info[col]["frac_size"]
        col_orig = df[col]
        int_col = col_orig.apply(
            lambda x: int(
                Fxp(x, signed=signed, n_word=bits, n_frac=best_frac).bin(), base=2
            )
        )
        df[col] = int_col


def make_training_values_positive(df: "pd.DataFrame") -> Dict:
    non_obj = [col for col in df if (str(df.dtypes[col]) != "object")]
    min_col = {}
    for col in non_obj:
        if min(df[col]) < 0:
            df[col] = df[col] - min(df[col])
        min_col[col] = min(df[col])
    return min_col


def make_test_values_positive(df: "pd.DataFrame", min_col: Dict) -> None:
    non_obj = [col for col in df if (str(df.dtypes[col]) != "object")]
    for col in non_obj:
        if min_col[col] < 0:
            df[col] = df[col] - min_col


if __name__ == "__main__":
    name = input()
    process(name)
