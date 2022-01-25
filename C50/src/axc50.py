import os
from pathlib import Path
from typing import List

# Comparators
FA_BASED = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]

# Datasets
NUMERICAL = ["breast-cancer", "iris", "forest"]
MIXED = ["adult", "heart-disease", "arrhythmia"]
DATASETS = NUMERICAL + MIXED

# Approximated operations in C5.0
CONTINUOUS_TESTS = [
    ("if ( !(Val <= T->Lower) )", "Val", "T->Lower"),
    ("else if ( !(T->Upper <= Val) )", "T->Upper", "Val"),
    ("if ( Val <= T->Lower )", "Val", "T->Lower"),
    ("else if ( T->Upper <= Val )", "T->Upper", "Val"),
    ("else if ( Val <= T->Mid )", "Val", "T->Mid"),
]

C50_DIR = Path(__file__).parents[1]
TOP_DIR = Path(__file__).parents[2]

def _build_fa_based(n_bits: int) -> None:
    """Build FA-based comparators C5.0 instances"""
    os.system("make")
    os.rename("c5.0", "../build/c5.0_default")
    for adder in FA_BASED:
        ## make approximate versions
        with open("classify.c", "r") as f:
            classify = f.read()

        replaced_lines = {}
        for line, val1, val2 in CONTINUOUS_TESTS:
            new_line = f"if ( leq({val1}, {val2}, {adder}, {n_bits}) )"
            if "!" in line:
                new_line = f"if ( !leq({val1}, {val2}, {adder}, {n_bits}) )"
            if "else" in line:
                new_line = "else " + new_line

            replaced_lines[line] = new_line
            classify = classify.replace(line, new_line)
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)

        os.system("make")
        os.rename("c5.0", f"../build/c5.0_{adder}_{n_bits}b")

        with open("classify.c", "r") as f:
            classify = f.read()
        for line, _, _ in CONTINUOUS_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def _build_dedicated(n_bits: int) -> None:
    """Build Dedicated Comparators C5.0 instances"""
    for comp in DEDICATED:
        with open("classify.c", "r") as f:
            classify = f.read()

        replaced_lines = {}
        for line, val1, val2 in CONTINUOUS_TESTS:
            new_line = f"if ( {comp}({val1}, {val2}, {n_bits}) )"
            if "!" in line:
                new_line = f"if ( !{comp}({val1}, {val2}, {n_bits}) )"
            if "else" in line:
                new_line = "else " + new_line
            replaced_lines[line] = new_line
            classify = classify.replace(line, new_line)
            with open("classify.c", "w") as f:
                f.seek(0)
                f.write(classify)

        os.system("make")
        os.rename("c5.0", f"../build/c5.0_{comp}_{n_bits}b")

        with open("classify.c", "r") as f:
            classify = f.read()
        for line, _, _ in CONTINUOUS_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        classify.replace(new_line, line)
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def _train_datasets(datasets: List[str] = DATASETS, n_bits: int = 8) -> None:
    for dataset in datasets:
        if not (C50_DIR / f"datasets/quantized/{dataset}/output/").exists():
            (C50_DIR / f"datasets/quantized/{dataset}/output/").mkdir()
        os.system(
            f"{C50_DIR.absolute()}/build/c5.0_default -f {C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}"
            + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_default.output"
        )
        for comp in FA_BASED + DEDICATED:
            os.system(
                f"{C50_DIR.absolute()}/build/c5.0_{comp}_{n_bits}b -f {C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}"
                + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_{comp}.output"
            )
            os.rename(
                f"{C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}.testlog",
                f"{TOP_DIR.absolute()}/comparators/n_bit/hspice/logs/{dataset}_{comp}.testlog",
            )


def runner(
    *,
    n_bits: int = 8,
    build: bool = False,
    train: bool = True,
) -> None:
    if build:
        _build_fa_based(n_bits=n_bits)
        _build_dedicated(n_bits=n_bits)
    if train:
        _train_datasets(n_bits=n_bits)


if __name__ == "__main__":
    print('Build approximate versions? [y/N]')
    build = False
    train = True
    if input() in ['y', 'yes', 'Y']:
        build = True
    print('Train approximate C5.0 versions in all datasets? [Y/n]')
    if input() in ['n', 'no', 'N']:
        train = False
    runner(build=build, train=train)
