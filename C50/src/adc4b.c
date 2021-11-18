
int leq_exact(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    int eq1 = ~(bin_a[1] ^ bin_b[1]);
    int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & eq1);
    return (n0 & n1 & n2 & n3) & 1;
}

int leq_a1(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    int eq1 = ~(bin_a[1] ^ bin_b[1]);
    int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    int n0 = ~(eq3 & eq2 & eq1);
    return (n0 & n1 & n2 & n3) & 1;
}

int leq_a2(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    // int eq1 = ~(bin_a[1] ^ bin_b[1]);
    int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    // int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & eq1);
    return (n1 & n2 & n3) & 1;
}

int leq_a3(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    // int eq1 = ~(bin_a[1] ^ bin_b[1]);
    int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    // int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & eq1);
    return (bin_a[0] & n1 & n2 & n3) & 1;
}

int leq_a4(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    // int eq1 = ~(bin_a[1] ^ bin_b[1]);
    int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    // int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & bin_a[1]);
    return (n0 & bin_a[1] & n2 & n3) & 1;
}

int leq_a5(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    // int eq1 = ~(bin_a[1] ^ bin_b[1]);
    // int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    // int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    // int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & eq1);
    return (bin_a[0] & bin_a[1] & n2 & n3) & 1;
}

int leq_a6(int a, int b) {
    int bin_a[4];
    int bin_b[4];
    to_binary(a, 4, bin_a);
    to_binary(b, 4, bin_b);
    // int eq1 = ~(bin_a[1] ^ bin_b[1]);
    // int eq2 = ~(bin_a[2] ^ bin_b[2]);
    int eq3 = ~(bin_a[3] ^ bin_b[3]);
    int n3 = ~(bin_a[3] & ~bin_b[3]);
    int n2 = ~(bin_a[2] & ~bin_b[2] & eq3);
    // int n1 = ~(bin_a[1] & ~bin_b[1] & eq3 & eq2);
    // int n0 = ~(bin_a[0] & ~bin_b[0] & eq3 & eq2 & eq1);
    return (bin_a[1] & n2 & n3) & 1;
}

