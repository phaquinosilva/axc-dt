import re
from pathlib import Path
from typing import Dict, List

import pandas as pd

from C50.datasets.quantizer import DATASETS

# Comparators
ADDERS = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]
DEFAULT = ["default_raw", "default_scaled", "default_quantized"]
COMPARATORS = DEFAULT + DEDICATED + ADDERS

FILE_DIR = Path(__file__).parent
C50_DIR = Path(__file__).parents[1]
TOP_DIR = Path(__file__).parents[2]


def extract_accuracy(lines: str) -> Dict[str, float]:
    """Finds error rates in file"""
    extract_percentage = lambda x: float(re.findall("\d+\.\d", x)[0])
    for line_id, line in enumerate(lines):
        if "Evaluation on training data" in line:
            training_eval = lines[line_id + 6]
        if "Evaluation on test data" in line:
            test_eval = lines[line_id + 6]
            # always after training data, so when we're done, break
            break
    training_acc = 100 - extract_percentage(training_eval)
    test_acc = 100 - extract_percentage(test_eval)
    return training_acc, test_acc


# TODO: #2 Improve readability/maintainability of this function
def process_results(
    *, datasets: List[str] = DATASETS, save_files: bool = False
) -> None:
    testsets = []
    trainsets = []

    for set in datasets:
        print(f"Processing {set} outputs...")
        test = {}
        train = {}
        for comparator in COMPARATORS:
            with open(
                FILE_DIR / f"quantized/{set}/output/{set}_{comparator}.output", "r"
            ) as f:
                lines = list(f)
            train[comparator], test[comparator] = extract_accuracy(lines)
        train = pd.Series(train)
        test = pd.Series(test)
        trainsets.append(train)
        testsets.append(test)

    test_rates = pd.concat(testsets, axis=1, keys=datasets)
    train_rates = pd.concat(trainsets, axis=1, keys=datasets)
    if save_files:
        (TOP_DIR / "results").mkdir(parents=True, exist_ok=True)
        test_rates.to_csv(TOP_DIR / "results/test_accuracy.csv")
        train_rates.to_csv(TOP_DIR / "results/train_accuracy.csv")

    print(f"Train accuracy:\n{train_rates}")
    print(f"Test accuracy:\n{test_rates}")

    return test_rates, train_rates


if __name__ == "__main__":
    test, train = process_results(save_files=True)
