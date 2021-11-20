#!/usr/bin/python3

from typing import Callable, List, Tuple, Iterable


def list_bin(number: int, n_bits: int) -> List[int]:
    """Turns integer to a list of integers from its binary representation"""
    form = "#0" + str(n_bits + 2) + "b"
    format_bin = format(number, form)[2:]
    return list(map(int, format_bin))


def differ_test(cs: int, ns: int, f: Callable[[Iterable[int]], int], n: int) -> bool:
    """
    Tests if a single input has changed during function call.
    :param cs:
        A string with the bits of current state for passing to evaluated test
    :param ns:
        A string with the bits of next state for passing to evaluated test
    :param f:
        A Callable returning boolean for function test
    """
    # apply function to both states
    current_state, next_state = list_bin(cs, n), list_bin(ns, n)
    cf, nf = f(current_state), f(next_state)
    if cf == nf:  # if result doesn't change
        return False
    # if only one input changes
    dif_bit = -1
    for i in range(len(current_state)):
        if dif_bit != -1 and current_state[i] != next_state[i]:
            return False
        elif dif_bit == -1 and current_state[i] != next_state[i]:
            dif_bit = i
    if dif_bit == -1:
        return False
    return True


def find_diffs(
    cs: int, ns: int, f: Callable[[Iterable[int]], int], n: int
) -> Tuple[str, str, str]:
    current_state, next_state = list_bin(cs, n), list_bin(ns, n)
    cf, nf = f(current_state), f(next_state)
    dif_bit = -1
    rof_s = ""  # rise or fall in previous state
    rof_f = ""  # rise or fall in latter state
    edge = lambda a, b: "fall" if a > b else "rise"
    for i in range(len(current_state) - 1, -1, -1):
        if dif_bit == -1 and current_state[i] != next_state[i]:
            dif_bit = i
            rof_s = edge(current_state[i], next_state[i])
            rof_f = edge(cf, nf)
    return ("a" + str(dif_bit), rof_s, rof_f)


def inputs_of_interest(
    f: Callable[[Iterable[int]], int], n: int
) -> List[Tuple[int, int]]:
    # f: function to be evaluated
    # n: number of input bits
    all_inputs = [(i, j) for i in range(2 ** n) for j in range(2 ** n) if i != j]
    filtered_inputs = filter(lambda tup: differ_test(tup[0], tup[1], f, n), all_inputs)
    return list(filtered_inputs)


def delay_arcs_gates(gates):
    """Generates arcs and files for logic gate simulation"""
    infos = {}
    interest = {}
    for gate, size, name in gates:
        interest[name] = inputs_of_interest(gate, size)
        get_infos = lambda tup: find_diffs(tup[0], tup[1], gate, size)
        infos[name] = list(map(get_infos, interest[name]))
    return interest, infos


def write_sources(prev, later, output, n, file_name, infos):
    states = []
    states.append((list_bin(prev, n), list_bin(later, n)))
    # write input sources in a file
    with open("sources/source_" + file_name + ".txt", "w+") as file:
        file.write("** sources and measures for comparator type: " + file_name + "\n\n")
        for before, after in states:
            # writes all input sources for A
            file.write("*" + str(n) + "-bit input A\n")
            for i in range(n):
                if before[i] == 0:
                    if after[i] == 0:
                        file.write(f"Va{i} a{i}_in gnd PWL(0n 0)\n")
                    else:
                        file.write(f"Va{i} a{i}_in gnd PWL(0n 0 1n 0 1.1n vdd)\n")
                else:
                    if after[i] == 0:
                        file.write(f"Va{i} a{i}_in gnd PWL(0n vdd 1n vdd 1.1n 0)\n")
                    else:
                        file.write(f"Va{i} a{i}_in gnd PWL(0n vdd)\n")
        # write measures
        (bit, in_rof, out_rof) = infos
        file.write("\n*measures\n")
        type = "hl" if out_rof == "fall" else "lh"
        file.write(
            f".measure tran tp{type} trig v({bit}) val='0.5*vdd' {in_rof}=1 targ v({output}) val='0.5*vdd' {out_rof}=1\n"
        )


def create_sources_files(gates):
    interest, infos = delay_arcs_gates(gates)

    for _, size, name in gates:
        for i, (before, after) in enumerate(interest[name]):
            write_sources(
                before, after, "out", size, name + "_" + str(i), infos[name][i]
            )
    return interest


def run_simulation(gate, interest):
    _, _, name = gate
    import os

    for source_num in range(interest[name]):
        source = f"\n.include sources/source_{name}_{source_num}.txt"
        with open("source.txt", "w") as f:
            f.write(source)
        os.system("hspice simulate_gate.cir")
        os.rename("simulate_gate.mt0.csv", f"results/result_{name}_{source_num}.csv")


def prepare_simulation(gate):
    _, size, name = gate
    # Create DUT include
    inputs = " ".join(["a%d" % i for i in range(size)])
    include = f"\nX{name} " + inputs + f" out vdut {name}"
    # Create loads include
    loads = "\n"
    for i in range(size):
        loads += (
            f"Xa{i}0 a{i}_in na{i}_in vdd1 inv M=4\n"
            + f"Xa{i}1 na{i}_in a{i} vdd1 inv M=4\n"
        )
    with open("simulation_info.txt", "w") as f:
        f.write(loads)
        f.write("\n")
        f.write(include)


def simulate_gates():
    # logic gates used
    inv = lambda x: 1 if x else 0
    nand2 = lambda x: 0 if (x[0] and x[1]) else 1
    nand3 = lambda x: 0 if (x[0] and x[1] and x[2]) else 1
    nand4 = lambda x: 0 if (x[0] and x[1] and x[2] and x[3]) else 1
    nand5 = lambda x: 0 if (x[0] and x[1] and x[2] and x[3] and x[4]) else 1
    nor2 = lambda x: 0 if (x[0] or x[1]) else 1
    nor4 = lambda x: 0 if (x[0] or x[1] or x[2] or x[3]) else 1
    mux21 = lambda x: x[0] if x[2] == 0 else x[1]
    xnor = lambda x: 0 if (x[0] == 1 and x[1] == 0) or (x[0] == 0 and x[1] == 1) else 1
    gates = [
        (nand2, 2, "nand2"),
        (nand3, 3, "nand3"),
        (nand4, 4, "nand4"),
        (nand5, 5, "nand5"),
        (nor2, 2, "nor2"),
        (nor4, 4, "nor4"),
        (inv, 1, "inv"),
        (mux21, 3, "mux21"),
        (xnor, 2, "xnor"),
    ]
    interest = create_sources_files(gates)
    for name in interest.keys():
        interest[name] = len(interest[name])

    # `inv` is a special case and thus must be included later
    # can be solved, but due to time restrictions won't be as of right now
    gates.append((inv, 1, "inv"))
    interest["inv"] = 1
    # simulate all gates
    for gate in gates:
        prepare_simulation(gate)
        run_simulation(gate, interest)


if __name__ == "__main__":
    simulate_gates()
