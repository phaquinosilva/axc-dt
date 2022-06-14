#!/home/pedro/.miniconda3/bin/python

import os
from pathlib import Path

import pandas as pd  # type: ignore

SIM_TIME = 3e-9
VOLTAGE = 0.7


def organize_results(gate):
    results = []
    p = Path(".")
    for csv in p.glob(f"**/result_{gate}_*.csv"):
        res_df = pd.read_csv(csv, skiprows=3, na_values="failed")
        print(res_df)
        # seleciona colunas relevantes
        delay_df = res_df.filter(regex="tp")
        power = (-1) * res_df["q_dut"].iloc[0] * VOLTAGE / SIM_TIME
        # pior caso de atraso
        delay = delay_df.max(axis=1).iloc[0]
        results.append({"delay": delay, "power": power})
        # limpa diretorio para restarem somente os arquivos relevantes
        os.remove(csv)
    sums_res = pd.DataFrame(results)
    avg_pow = sums_res["power"].mean()
    delay = sums_res["delay"].max(axis=0)
    return {"delay": delay, "power": avg_pow}


def run_processing():
    gates = ["inv", "mux21", "nand2", "nand3", "nand4", "nand5", "nor2", "nor4", "xnor"]
    results = {}
    for gate in gates:
        results[gate] = organize_results(gate)
    results_df = pd.DataFrame(results)
    results_df.to_csv("gate_results.csv")
    print(results_df)


if __name__ == "__main__":
    run_processing()
