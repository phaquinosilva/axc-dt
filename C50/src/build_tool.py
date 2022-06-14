import os
from pathlib import Path

from axc50 import CONTINUOUS_TESTS, DEDICATED, FA_BASED

CATEGORICAL_TESTS = [
    ("if ( Dv <= T->Forks )", "Dv", "T->Forks"),
    ("if ( Dv <= MaxAttVal[T->Tested] )", "Dv", "MaxAttVal[T->Tested]"),
]

ATTRIBUTE_TESTS = CATEGORICAL_TESTS + CONTINUOUS_TESTS


def approximate_c50(
    comp: str, n_bits: int, *, enable_cleanup: bool = False, enable_build: bool = False
) -> None:
    """
    Create C5.0 approximation
    :param comp:
        a string with the comparator name (only dedicated for now)
    :param n_bits:
        number of bits in comparator
    :param enable_cleanup:
        if True, returns classify.c to original state
    :param enable_build:
        if True, builds c5.0 approximation binary
    """

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

        if enable_build:
            os.system("make")
            os.rename("c5.0", f"c5.0_{comp}_{n_bits}b")

        if enable_cleanup:
            with open("classify.c", "r") as f:
                classify = f.read()
            for line, _, _ in CONTINUOUS_TESTS:
                new_line = replaced_lines[line]
                classify = classify.replace(new_line, line)
            classify.replace(new_line, line)
            with open("classify.c", "w") as f:
                f.seek(0)
                f.write(classify)


approximate_c50("axdc6", 8, enable_build=True)


def _train_categorical(n_bits: int) -> None:
    CATEGORICAL = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
    for dataset in CATEGORICAL:
        if not (Path(f"../datasets/raw/{dataset}/output/")).exists():
            (Path(f"../datasets/raw/{dataset}/output/")).mkdir()
        os.system(
            f"../build/full_approx/c5.0_default -f ../datasets/raw/{dataset}/{dataset}"
            + f" > ../datasets/raw/{dataset}/output/{dataset}_default.output"
        )
        for comp in FA_BASED + DEDICATED:
            os.system(
                f"../build/full_approx/c5.0_{comp}_{n_bits}b -f ../datasets/raw/{dataset}/{dataset}"
                + f" > ../datasets/raw/{dataset}/output/{dataset}_{comp}.output"
            )
            os.rename(
                f"../datasets/raw/{dataset}/{dataset}.testlog",
                f"../../comparators/nbit/hspice/logs/{dataset}_{comp}.testlog",
            )
