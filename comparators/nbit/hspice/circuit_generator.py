"""
SPICE subcircuits generator for n-bit AxC dedicated
comparator circuits
"""


def spicegen_edc(n):
    """Generate EDC"""
    # output file
    f = open("edc_%db.cir" % n, "w+")
    # signal information
    a_in = ["a%d" % i for i in range(n)]
    b_in = ["b%d" % i for i in range(n)]
    # initialize file
    f.write(
        """* %d-bit Exact Dedicated Comparator\n\n.include gates.cir\n\n.subckt comparator %s %s leq vdd\n"""
        % (n, " ".join(a_in), " ".join(b_in))
    )
    # compute xnors
    for i in range(1, n):
        f.write("   Xeq%d a%d b%d eq%d vdd xnor\n" % (i, i, i, i))
    f.write("\n")
    # negate B
    for i in range(n):
        f.write("   Xnb%d b%d nb%d vdd inv\n" % (i, i, i))
    f.write("\n")
    # compute greater for each bit
    count = 0
    for i in range(n - 1, -1, -1):
        eqs = ["eq%d" % j for j in range(n - 1, i, -1)]
        f.write(f"   Xn{i} a{i} nb{i} %s n{i} vdd nand{2+len(eqs)}\n" % " ".join(eqs))
    f.write("\n")
    # compute less or equal than
    ns = ["n%d" % i for i in range(n)]
    f.write("   Xgr %s gr vdd nand%d\n" % (" ".join(ns), len(ns)))
    f.write("   Xleq gr leq vdd inv\n.ends")
    f.close()


def spicegen_axdc2(n):
    """Generate AxDC2 description"""
    # output file
    f = open("axdc2_%db.cir" % n, "w+")
    # signal information
    a_in = ["a%d" % i for i in range(n)]
    b_in = ["b%d" % i for i in range(n)]
    n_4 = int(n / 4)
    # initialize file
    f.write(
        "* %d-bit Approximate Dedicated Comparator 2\n\n.include gates.cir"
        + "\n\n.subckt comparator %s %s leq vdd\n" % (n, " ".join(a_in), " ".join(b_in))
    )
    # compute xnors
    for i in range(n_4 + 1, n):
        f.write("   Xeq%d a%d b%d eq%d vdd xnor\n" % (i, i, i, i))
    f.write("\n")
    # negate B
    for i in range(n_4, n):
        f.write("   Xnb%d b%d nb%d vdd inv\n" % (i, i, i))
    f.write("\n")
    # compute greater for each bit
    for i in range(n - 1, n_4 - 1, -1):
        eqs = ["eq%d" % j for j in range(n - 1, i, -1)]
        f.write(
            "   Xn%d a%d nb%d %s n%d vdd nand%d\n"
            % (i, i, i, " ".join(eqs), i, (2 + len(eqs)))
        )
    f.write("\n")
    # compute less or equal than
    ns = ["n%d" % i for i in range(n_4, n)]
    f.write("   Xgr %s gr vdd nand%d\n" % (" ".join(ns), len(ns)))
    f.write("   Xleq gr leq vdd inv\n.ends")
    f.close()


def spicegen_axdc6(n):
    """Generate AxDC6 description"""
    # output file
    f = open(f"axdc6_{n}b.cir", "w+")
    # signal information
    a_in = ["a%d" % i for i in range(n)]
    b_in = ["b%d" % i for i in range(n)]
    n_2 = int(n / 2)
    n_4 = int(n / 4)
    # initialize file
    f.write(
        f"* {n}-bit Approximate Dedicated Comparator 6\n\n.include gates.cir\n"
        + "\n.subckt comparator %s %s leq vdd\n" % (" ".join(a_in), " ".join(b_in))
    )
    # compute xnors
    for i in range(n_2 + 1, n):
        f.write(f"   Xeq{i} a{i} b{i} eq{i} vdd xnor\n")
    f.write("\n")
    # negate B
    for i in range(n_2, n):
        f.write(f"   Xnb{i} b{i} nb{i} vdd inv\n")
    f.write("\n")
    # compute greater for each bit
    count = 0
    for i in range(n - 1, n_2 - 1, -1):
        eqs = ["eq%d" % j for j in range(n - 1, i, -1)]
        f.write(
            "   Xn%d a%d nb%d %s n%d vdd nand%d\n"
            % (i, i, i, " ".join(eqs), i, (2 + len(eqs)))
        )
    f.write("\n")
    # buffer b inputs
    for i in range(n_4, n_2):
        f.write(
            f"   Xib{i} b{i} ib{i} vdd inv\n   Xbb{i} ib{i} bb{i} vdd inv\n"
        )
    f.write("\n")
    # compute less or equal than
    ns = ["n%d" % i for i in range(n_2, n)]
    bs = ["bb%d" % i for i in range(n_4, n_2)]
    f.write(
        "   Xgr %s %s gr vdd nand%d\n" % (" ".join(ns), " ".join(bs), len(ns) + len(bs))
    )
    f.write("   Xleq gr leq vdd inv\n.ends")
    f.close()


def spicegen_adder(adder, n):
    """
    Generates SPICE for full adder based comparators (use ripple carry architecture)
    """
    pass


def gates(n):
    """
    Generates large NOR and NAND gates in SPICE for use in dedicated comparators.
    Adds created circuits to 'rtl_utils.cir' file.
    """
    pass
