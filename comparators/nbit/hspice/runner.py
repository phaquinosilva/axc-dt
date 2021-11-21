import os
from pathlib import Path

from input_generator import create_input_sources

ADDERS = ["sma", "ama1", "ama2"]
DEDICATED = ["edc", "axdc2", "axdc6"]
COMPARATORS = ADDERS + DEDICATED

CATEGORICAL = ["mushroom", "car", "kr-vs-kp", "splice", "tic-tac-toe"]
MIXED = ["health", "iris", "forest"]
DATASETS = CATEGORICAL + MIXED


def simulate_operations(name: str, n_bits: int) -> None:
    """
    Simulates the comparisons made in a DT application
    with n-bit comparators
    """
    total_simulations = 0
    for circuit in COMPARATORS:
        if circuit in ADDERS:
            create_rca_include(circuit, n_bits)
        op_list = create_input_sources(
            inputs_file=Path(__file__).parent / f"logs/{name}_{circuit}.testlog",
            saving_dir=Path(__file__).parent / "sources",
            n=n_bits,
        )
        num_samples = len(op_list)
        total_simulations += num_samples
        for i in range(num_samples):
            run_simulation(comparator=circuit, op_index=i, n_bits=n_bits, dataset=name)
    return total_simulations


def create_rca_include(fa: str, n: int) -> None:
    """Create SPICE description for n-bit Ripple Carry Adder using specified FA"""
    rca_text = f"* {n} bit Ripple Carry Adder\n"
    a = " ".join(["a%d" % i for i in range(n)])
    b = " ".join(["b%d" % i for i in range(n)])
    s = " ".join(["s%d" % i for i in range(n)])
    rca_text += f".subckt rca{n}b {a} {b} c0 {s} c{n} vdd\n"
    for i in range(n):
        rca_text += f"XFA{i} a{i} b{i} c{i} s{i} c{i+1} vdd {fa}\n"
    rca_text += ".ends"
    with open("rca.cir", "w") as f:
        f.write(rca_text)


def run_simulation(comparator: str, op_index: int, n_bits: int, dataset: str) -> None:
    """Runs simulation for a single operation"""
    with open("simulation_info.txt", "w") as f:
        f.seek(0)
        if comparator in ADDERS:
            f.write(f".include fas/{comparator}.cir\n")
            f.write(".include rca.cir\n")
            f.write(f".include comparators/axfa_{n_bits}b.cir\n")
        else:
            f.write(f".include comparators/{comparator}_{n_bits}b.cir\n")
        f.write(f".include sources/source_operation_{op_index}.txt\n")
    inputs = (
        " ".join(["a%d" % i for i in range(n_bits)])
        + " "
        + " ".join(["b%d" % i for i in range(n_bits)])
    )
    with open("circuit.cir", "r") as f:
        contents = f.read()
    contents = contents.replace("<inputs>", inputs)
    with open("circuit.cir", "w") as f:
        f.seek(0)
        f.write(contents)
    os.system("hspice circuit.cir")
    with open("circuit.cir", "r") as f:
        contents = f.read()
    contents = contents.replace(inputs, "<inputs>")
    with open("circuit.cir", "w") as f:
        f.seek(0)
        f.write(contents)
    if not (Path(__file__) / f"outputs/{dataset}").exists():
        (Path(__file__) / f"outputs/{dataset}").mkdir()
    os.rename(
        "./circuit.mt0.csv",
        f"outputs/{dataset}/result_{comparator}_{op_index}.csv",
    )


if __name__ == "__main__":
    total_simulations = 0
    for dataset in CATEGORICAL:
        total_simulations += simulate_operations(dataset, 4)
    for dataset in MIXED:
        total_simulations += simulate_operations(dataset, 8)
    print(total_simulations)
