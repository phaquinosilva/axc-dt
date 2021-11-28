import re
from pathlib import Path
from typing import Dict

import pandas as pd
from quantizer import DATASETS

# Comparators
ADDERS = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]
DEFAULT = ["default"]
COMPARATORS = DEFAULT + DEDICATED + ADDERS


def extract_rates(lines: str) -> Dict[str, float]:
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
def find_accuracy(*, save_files: bool = False) -> None:
    testsets = []
    trainsets = []

    for set in DATASETS:
        test = {}
        train = {}
        for comparator in COMPARATORS:
            with open(f"quantized/{set}/output/{set}_{comparator}.output", "r") as f:
                lines = f.readlines()
            train[comparator], test[comparator] = extract_rates(lines)
        train = pd.Series(train)
        test = pd.Series(test)
        trainsets.append(train)
        testsets.append(test)

    test_rates = pd.concat(testsets, axis=1, keys=DATASETS)
    train_rates = pd.concat(trainsets, axis=1, keys=DATASETS)
    if save_files:
        test_rates.to_csv("test_error_rates.csv")
        train_rates.to_csv("train_error_rates.csv")
    return test_rates, train_rates


if __name__ == "__main__":
    test, train = find_accuracy(save_files=True)
    print(test)
