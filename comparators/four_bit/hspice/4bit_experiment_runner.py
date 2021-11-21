import os
from pathlib import Path

import pandas as pd

################################# Runner SCRIPT #################################

## SUBTRACTOR CIRCUITS ##


def simulate_axfc():
    """Run simulation for 4bit adder comparators"""
    fa = ["ema", "exa", "sma", "ama1", "ama2", "axa2", "axa3"]
    sample_sizes = [480, 480, 340, 340, 256, 480, 480]
    results = {}
    for i in range(len(fa)):
        # altera FA no arquivo de simulacao
        pre(fa[i])
        # executa simulacao nas somas da amostra
        for j in range(sample_sizes[i]):
            run_sim_adders("comp_subtractor", j, fa[i])
        # retorna arquivo pro original
        post(fa[i])
        results[fa[i]] = organize_axfa_results(5e-9, 0.7, "comp_subtractor", fa[i])
    prime = pd.DataFrame(results)
    prime.to_csv("./results/comp_subtractor_results.csv")


def run_sim_adders(comparator, comp_num, cell):
    """Runs simulation for adder based comparators (AxFA)"""

    # sets type of sources file and name of output file
    adder = ".include fas/" + cell + ".cir\n"
    source = ".include sources/"
    if cell == "exa" or cell == "ema":
        name = (
            "results/result_" + comparator + "_" + cell + "_" + str(comp_num) + ".csv"
        )
        source += "source_exact_" + str(comp_num) + ".cir\n"
    else:
        name = (
            "results/result_" + comparator + "_" + cell + "_" + str(comp_num) + ".csv"
        )
        source += "source_" + cell + "_" + str(comp_num) + ".cir\n"

    with open("./nondef_params.txt", "w") as f:
        f.seek(0)
        f.write(source)
        f.write(adder)

    os.system("hspice " + comparator + ".cir")
    os.rename("./" + comparator + ".mt0.csv", name)


def organize_axfa_results(sim_time, voltage, comparator, cell):
    """Process results obtained from AxFA simulations"""
    adder_results = []
    p = Path(".")
    for csv in list(p.glob("**/result_" + comparator + "_" + cell + "_*.csv")):
        res_df = pd.read_csv(csv, skiprows=3, na_values="failed")
        print(res_df)
        # select relevant columns
        delay_df = res_df.filter(regex="tp")
        if cell == "AXA2" or cell == "AXA3" or cell == "EXA":
            power = (
                (-1)
                * (res_df["q_dut"].iloc[0] + res_df["q_in"].iloc[0])
                * voltage
                / sim_time
            )
        else:
            power = (-1) * res_df["q_dut"].iloc[0] * voltage / sim_time
        # find critical delay
        delay = delay_df.max(axis=1).iloc[0]
        adder_results.append({"delay": delay, "power": power})
        # remove individual simulation outputs
        os.remove(csv)
    sums_res = pd.DataFrame(adder_results)
    avg_pow = sums_res["power"].mean()
    delay = sums_res["delay"].max(axis=0)
    return {"delay": delay, "power": avg_pow}


def pre(adder):
    """
    Prepare circuit for simulation.
    Substitutes adder in simulation file for adder used in current simulation.
    """
    with open("./array_adders/4bRCA.cir", "r") as f:
        filedata = f.read()
    newdata = filedata.replace("ema", adder)
    with open("./array_adders/4bRCA.cir", "w") as f:
        f.seek(0)
        f.write(newdata)


def post(adder):
    """
    Prepares adder for next simulation after current iteration.
    Substitutes adder currently in file with the default.
    """
    with open("./array_adders/4bRCA.cir", "r") as f:
        filedata = f.read()
    newdata = filedata.replace(adder, "ema")
    with open("./array_adders/4bRCA.cir", "w") as f:
        f.seek(0)
        f.write(newdata)


## DEDICATED CIRCUITS ##


def simulate_axdc():
    """Runs simulation for 4bit dedicated comparators"""
    comparators = [
        "comp_exact",
        "comp_approx1",
        "comp_approx2",
        "comp_approx3",
        "comp_approx4",
        "comp_approx5",
        "comp_approx6",
    ]
    sample_sizes = [480, 448, 448, 368, 368, 256, 352]
    results = {}
    for i in range(len(sample_sizes)):
        # simulação para subtratores
        for j in range(sample_sizes[i]):
            run_sim_dedicated(comparator=comparators[i], comp_num=j)
        results[comparators[i]] = process_axdc_results(5e-9, 0.7, comparators[i])
    prime = pd.DataFrame(results)
    prime.to_csv("./results/comp_dedicated_results.csv")


def run_sim_dedicated(comparator, comp_num):
    name = "results/result_" + comparator + "_" + str(comp_num) + ".csv"
    source = ".include sources/source_" + comparator + "_" + str(comp_num) + ".cir\n"
    if comparator == "comp_exact":
        with open("nondef_params.txt", "w") as f:
            f.seek(0)
            f.write(source)
        os.system("hspice comp_dedicated.cir")
        os.rename("./comp_dedicated.mt0.csv", name)
    else:
        with open("nondef_params.txt", "w") as f:
            f.seek(0)
            f.write(".include comparators/4bit_" + comparator + ".cir\n")
            f.write(source)
        os.system("hspice comp_dedicated_approx.cir")
        os.rename("./comp_dedicated_approx.mt0.csv", name)


def process_axdc_results(sim_time, voltage, comparator):
    comp_results = []
    p = Path(".")
    for csv in list(p.glob("**/result_" + comparator + "_*.csv")):
        res_df = pd.read_csv(csv, skiprows=3, na_values="failed")
        print(res_df)
        # seleciona colunas relevantes
        delay_df = res_df.filter(regex="tp")
        power = (-1) * res_df["q_dut"].iloc[0] * voltage / sim_time
        # pior caso de atraso
        delay = delay_df.max(axis=1).iloc[0]
        comp_results.append({"delay": delay, "power": power})
        # limpa diretorio para restarem somente os arquivos relevantes
        os.remove(csv)
    sums_res = pd.DataFrame(comp_results)
    avg_pow = sums_res["power"].mean()
    delay = sums_res["delay"].max(axis=0)
    return {"delay": delay, "power": avg_pow}


if __name__ == "__main__":
    simulate_axfc()
    simulate_axdc()
