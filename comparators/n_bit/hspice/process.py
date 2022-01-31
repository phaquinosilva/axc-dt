import os
from pathlib import Path
from typing import Dict

import pandas as pd
from input_generator import count_repeated
from runner import COMPARATORS, DATASETS

NOMINAL_VOLTAGE = 0.7
SIMULATION_TIME = 2.5e-9


def process_comparators(name: str, *, enable_cleanup: bool = False) -> None:
    results = {}
    result_dir = Path(__file__).parents[3] / "results/"
    for circuit in COMPARATORS:
        results[circuit] = process_results(circuit, name, enable_cleanup=enable_cleanup)
    if not result_dir.exists():
        result_dir.mkdir()
    df = pd.DataFrame(results).transpose()
    print(f"{name}:\n{df}\n")
    df.to_csv(
        result_dir / f"{name}_operation_results.csv"
    )


def process_results(
    comparator: str, dataset: str, *, enable_cleanup: bool = False
) -> Dict:
    """Process results obtained from HSPICE"""
    energy_list = []
    power_list = []
    n_ops = 0

    data_path = Path(__file__).parents[3]
    with (data_path / f"C50/datasets/raw/{dataset}/{dataset}.test").open("r") as f:
        n_inputs = len(f.readlines())
    count = count_repeated(
        Path(__file__).parent / f"logs/{dataset}_{comparator}.testlog"
    )

    for id, pair in enumerate(count):
        num, _ = pair
        n_ops += num

        filename = (
            Path(__file__).parent / f"outputs/{dataset}/result_{comparator}_{id}.csv"
        )

        res_df = pd.read_csv(filename, skiprows=3, na_values="failed")
        energy = abs(res_df["q_dut"].iloc[0] * NOMINAL_VOLTAGE)
        energy_list.append(energy * num)
        power = energy / SIMULATION_TIME
        power_list.append(power * num)
        if enable_cleanup:
            os.remove(filename)

    total_energy = sum(energy_list)
    total_power = sum(power_list)
    avg_power = total_power / n_inputs

    return {
        "energy": total_energy,
        "avg_power": avg_power,
        "n_ops": n_ops,
    }


if __name__ == "__main__":
    for set in DATASETS:
        process_comparators(set)
