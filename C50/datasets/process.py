import re
from pathlib import Path
from typing import Dict

import pandas as pd

# Comparators
ADDERS = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]
DEFAULT = ["default"]
COMPARATORS = DEFAULT + DEDICATED + ADDERS

# Datasets
CATEGORICAL = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
MIXED = ["health", "iris", "forest"]


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
    training_rate = extract_percentage(training_eval)
    test_rate = extract_percentage(test_eval)
    return training_rate, test_rate


# TODO: #2 Improve readability/maintainability of this function
def find_error_rates():
    testsets = []
    trainsets = []

    for set in CATEGORICAL:
        test = {}
        train = {}
        for comparator in COMPARATORS:
            with open(f"raw/{set}/output/{set}_{comparator}.output", "r") as f:
                lines = f.readlines()
            tr, te = extract_rates(lines)
            train[comparator] = tr
            test[comparator] = te
        print(train)
        print(test)
        train = pd.Series(train)
        test = pd.Series(test)
        trainsets.append(train)
        testsets.append(test)

    for set in MIXED:
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

    test_rates = pd.concat(testsets, axis=1, keys=CATEGORICAL + MIXED)
    train_rates = pd.concat(trainsets, axis=1, keys=CATEGORICAL + MIXED)
    print(test_rates)
    print(train_rates)
    test_rates.to_csv(Path(__file__).parents[2] / f"test_error_rates.csv")
    train_rates.to_csv(Path(__file__).parents[2] / f"train_error_rates.csv")


if __name__ == "__main__":
    find_error_rates()
