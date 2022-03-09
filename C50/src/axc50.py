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
    os.system(f"make -C {str(C50_DIR)}/src/")
    (C50_DIR / 'src/c5.0').rename(C50_DIR / "builds/c5.0_default")
    for adder in FA_BASED:
        ## make approximate versions
        with (C50_DIR / "src/classify.c").open("r") as f:
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
        with (C50_DIR / "src/classify.c").open("w") as f:
            f.seek(0)
            f.write(classify)

        os.system(f"make -C {str(C50_DIR)}/src/")
        (C50_DIR / 'src/c5.0').rename(C50_DIR / f"builds/c5.0_{adder}_{n_bits}b") 

        with (C50_DIR / "src/classify.c").open("r") as f:
            classify = f.read()
        for line, _, _ in CONTINUOUS_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        with (C50_DIR / "src/classify.c").open("w") as f:
            f.seek(0)
            f.write(classify)


def _build_dedicated(n_bits: int) -> None:
    """Build Dedicated Comparators C5.0 instances"""
    for comp in DEDICATED:
        with (C50_DIR / "src/classify.c").open("r") as f:
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
            with (C50_DIR / "src/classify.c").open("w") as f:
                f.seek(0)
                f.write(classify)

        os.system(f"make -C {str(C50_DIR)}/src/")
        (C50_DIR / 'src/c5.0').rename(C50_DIR / f"builds/c5.0_{comp}_{n_bits}b")

        with (C50_DIR / "src/classify.c").open("r") as f:
            classify = f.read()
        for line, _, _ in CONTINUOUS_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        classify.replace(new_line, line)
        with (C50_DIR / "src/classify.c").open("w") as f:
            f.seek(0)
            f.write(classify)


def _train_datasets(datasets: List[str] = DATASETS, n_bits: int = 8) -> None:
    if not (TOP_DIR / "comparators/n_bit/hspice/logs/").exists():
        (TOP_DIR / "comparators/n_bit/hspice/logs/").mkdir()
    for dataset in datasets:
        if not (C50_DIR / f"datasets/quantized/{dataset}/output").exists():
            (C50_DIR / f"datasets/quantized/{dataset}/output").mkdir()
        
        # Run default on raw data
        os.system(
            f"{C50_DIR.absolute()}/builds/c5.0_default -f {C50_DIR.absolute()}/datasets/raw/{dataset}/{dataset}"
            + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_default_raw.output"
        )
        # Run default on scaled data
        os.system(
            f"{C50_DIR.absolute()}/builds/c5.0_default -f {C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}_scaled"
            + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_default_scaled.output"
        )
        # Run default on scaled and quantized data
        os.system(
            f"{C50_DIR.absolute()}/builds/c5.0_default -f {C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}"
            + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_default_quantized.output"
        )
        
        # Run approximate versions on scaled and quantized data
        for comp in FA_BASED + DEDICATED:
            os.system(
                f"{C50_DIR.absolute()}/builds/c5.0_{comp}_{n_bits}b -f {C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}"
                + f" > {C50_DIR.absolute()}/datasets/quantized/{dataset}/output/{dataset}_{comp}.output"
            )
            os.rename(
                f"{C50_DIR.absolute()}/datasets/quantized/{dataset}/{dataset}.testlog",
                f"{TOP_DIR.absolute()}/comparators/n_bit/hspice/logs/{dataset}_{comp}.testlog",
            )

def build(
    *,
    n_bits: int = 8,
) -> None:
    if not (C50_DIR / 'builds').exists():
        (C50_DIR / 'builds').mkdir()
    _build_fa_based(n_bits=n_bits)
    _build_dedicated(n_bits=n_bits)

def train(*, n_bits: int = 8, datasets: List[str] = DATASETS) -> None:
    _train_datasets(datasets=datasets,n_bits=n_bits)

