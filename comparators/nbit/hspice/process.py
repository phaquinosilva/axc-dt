import pandas as pd
from pathlib import Path
import os
from typing import Dict


NOMINAL_VOLTAGE = 0.7
SIMULATION_TIME = 2.5e-9


def process_comparators(name: str, enable_cleanup: bool = False) -> None:
    results = {}
    comparators = ["edc", "axdc2", "axdc6", "sma", "ama1", "ama2"]
    for circuit in comparators:
        results[circuit] = process_results(circuit, name, enable_cleanup)
    prime = pd.DataFrame(results)
    if not (Path.cwd() / "results/").exists():
        (Path.cwd() / "results/").mkdir()
    prime.to_csv("./results/" + name + "_operation_results.csv")


def process_results(
    comparator: str, dataset: str, enable_cleanup: bool = False
) -> Dict:
    """Process results obtained from HSPICE"""
    energy_list = []
    power_list = []
    p = Path.cwd()
    for csv in p.glob(f"*outputs/{dataset}/result_{comparator}_*.csv"):
        res_df = pd.read_csv(csv, skiprows=3, na_values="failed")
        energy = abs(res_df["q_dut"].iloc[0] * NOMINAL_VOLTAGE)
        energy_list.append(energy)
        power = energy / SIMULATION_TIME
        power_list.append(power)
        if enable_cleanup:
            os.remove(csv)
    total_energy = sum(energy_list)
    total_power = sum(power_list)
    n_ops = len(energy_list)
    avg_energy = total_energy / n_ops
    avg_power = total_power / n_ops  # para cada comparação
    return {
        "energy": total_energy,
        "power": total_power,
        "avg_energy": avg_energy,
        "avg_power": avg_power,
        "n_ops": n_ops,
    }


if __name__ == "__main__":

    data = ["iris", "forest", "health"]
    for set in data:
        process_comparators(set)
