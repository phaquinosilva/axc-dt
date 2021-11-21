import os
from pathlib import Path

FA_BASED = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]

CATEGORICAL = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
MIXED = ["health", "iris", "forest"]

ATTRIBUTE_TESTS = [
    ("if ( Dv <= T->Forks )", "Dv", "T->Forks"),
    ("if ( Dv <= MaxAttVal[T->Tested] )", "Dv", "MaxAttVal[T->Tested]"),
    ("if ( !(Val <= T->Lower) )", "Val", "T->Lower"),
    ("else if ( !(T->Upper <= Val) )", "T->Upper", "Val"),
    ("if ( Val <= T->Lower )", "Val", "T->Lower"),
    ("else if ( T->Upper <= Val )", "T->Upper", "Val"),
    ("else if ( Val <= T->Mid )", "Val", "T->Mid"),
]


def build_fa_based(n_bits: int) -> None:
    """Build FA-based comparators C5.0 instances"""
    os.system("make")
    os.rename("c5.0", "../build/full_approx/c5.0_default")
    for adder in FA_BASED:
        ## make approximate versions
        with open("classify.c", "r") as f:
            classify = f.read()

        replaced_lines = {}
        for line, val1, val2 in ATTRIBUTE_TESTS:
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
        os.rename("c5.0", f"../build/full_approx/c5.0_{adder}_{n_bits}b")

        with open("classify.c", "r") as f:
            classify = f.read()
        for line, _, _ in ATTRIBUTE_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def build_dedicated(n_bits: int) -> None:
    """Build Dedicated Comparators C5.0 instances"""
    for comp in DEDICATED:
        with open("classify.c", "r") as f:
            classify = f.read()

        replaced_lines = {}
        for line, val1, val2 in ATTRIBUTE_TESTS:
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
        os.rename("c5.0", f"../build/full_approx/c5.0_{comp}_{n_bits}b")

        with open("classify.c", "r") as f:
            classify = f.read()
        for line, _, _ in ATTRIBUTE_TESTS:
            new_line = replaced_lines[line]
            classify = classify.replace(new_line, line)
        classify.replace(new_line, line)
        with open("classify.c", "w") as f:
            f.seek(0)
            f.write(classify)


def train(*, enable_build: bool = False) -> None:
    if enable_build:
        build_fa_based(n_bits=8)
        build_dedicated(n_bits=8)
        build_fa_based(n_bits=4)
        build_dedicated(n_bits=4)

    for dataset in MIXED:
        if not (Path(f"../datasets/raw/{dataset}/output/")).exists():
            (Path(f"../datasets/raw/{dataset}/output/")).mkdir()
        os.system(
            f"../build/full_approx/c5.0_default -f ../datasets/quantized/{dataset}/{dataset}"
            + f" > ../datasets/quantized/{dataset}/output/{dataset}_default.output"
        )
        for comp in FA_BASED + DEDICATED:
            os.system(
                f"../build/full_approx/c5.0_{comp}_8b -f ../datasets/quantized/{dataset}/{dataset}"
                + f" > ../datasets/quantized/{dataset}/output/{dataset}_{comp}.output"
            )
            os.rename(
                f"../datasets/quantized/{dataset}/{dataset}.testlog",
                f"../../comparators/nbit/hspice/logs/{dataset}_{comp}.testlog",
            )
    for dataset in CATEGORICAL:
        if not (Path(f"../datasets/raw/{dataset}/output/")).exists():
            (Path(f"../datasets/raw/{dataset}/output/")).mkdir()
        os.system(
            f"../build/full_approx/c5.0_default -f ../datasets/raw/{dataset}/{dataset}"
            + f" > ../datasets/raw/{dataset}/output/{dataset}_default.output"
        )
        for comp in FA_BASED + DEDICATED:
            os.system(
                f"../build/full_approx/c5.0_{comp}_4b -f ../datasets/raw/{dataset}/{dataset}"
                + f" > ../datasets/raw/{dataset}/output/{dataset}_{comp}.output"
            )
            os.rename(
                f"../datasets/raw/{dataset}/{dataset}.testlog",
                f"../../comparators/nbit/hspice/logs/{dataset}_{comp}.testlog",
            )


if __name__ == "__main__":
    train(enable_build=True)
