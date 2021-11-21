#include <stdlib.h>
#include <stdio.h>
#include "defns.i"

/* DEFINICOES FA*/

void sma(int a, int b, int cin, int output[])
{
    int sum[8] = {0, 1, 0, 0, 0, 0, 0, 1};
    int cout[8] = {0, 0, 1, 1, 0, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

void ama1(int a, int b, int cin, int output[])
{
    int sum[8] = {1, 1, 0, 0, 1, 0, 0, 0};
    int cout[8] = {0, 0, 1, 1, 0, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

void ama2(int a, int b, int cin, int output[])
{
    int sum[8] = {0, 1, 0, 1, 0, 0, 0, 1};
    int cout[8] = {0, 0, 0, 0, 1, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

void axa2(int a, int b, int cin, int output[])
{
    int sum[8] = {1, 1, 0, 0, 0, 0, 1, 1};
    int cout[8] = {0, 0, 0, 1, 0, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

void axa3(int a, int b, int cin, int output[])
{
    int sum[8] = {0, 1, 0, 0, 0, 0, 0, 1};
    int cout[8] = {0, 0, 0, 1, 0, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

void buf(int a, int b, int cin, int output[])
{
    output[0] = a & 1;
    output[1] = b & 1;
}

void exact(int a, int b, int cin, int output[])
{
    int sum[8] = {0, 1, 1, 0, 1, 0, 0, 1};
    int cout[8] = {0, 0, 0, 1, 0, 1, 1, 1};
    int pos = ((a << 2) + (b << 1) + cin);
    output[0] = sum[pos];
    output[1] = cout[pos];
}

/* HELPERS */

void to_binary(int input, int n, int *bin)
{
    int pow2 = 1;
    for (int i = 0; i < n; i++)
    {
        if (input & pow2)
        {
            bin[i] = 1;
        }
        else
        {
            bin[i] = 0;
        }
        pow2 = pow2 << 1;
    }
}

int to_int(int *bin, int n)
{
    int pow2 = 1;
    int value = 0;
    // int largest = bin[n-1];
    for (int i = 0; i < n; i++)
    {
        if (bin[i] == 1)
        {
            value += pow2;
        }
        pow2 *= 2;
    }

    return value;
}

/* DEFINICOES OPERACOES */

int leq(int a, int b, void (*f)(int, int, int, int *), int n)
{
    // a, b: operandos (a <= b)
    // (*f): nome do FA a ser simulado
    // n: numero de bits

    // conversao inteiro binario
    int bin_a[n];
    int bin_b[n];
    to_binary(~a, n, bin_a);
    to_binary(b, n, bin_b); // bitwise not para subtracao

    int bin_out[n];
    int int_out[2];
    int cin = 1;

    // a - b >= 0 : a >= b -> ultimo bit = 0
    // a - b < 0 : a < b -> ultimo bit = 1
    for (int i = 0; i < n; i++)
    {
        (*f)(bin_b[i], bin_a[i], cin, int_out);
        bin_out[i] = int_out[0];
        cin = int_out[1];
    }

    // retorna resultado em int
    int result = cin;
    return result;
}

/* n-Bit Dedicated Comparators */

int edc(int a, int b, int n)
{
    int bin_a[n];
    int bin_b[n];
    int i;
    to_binary(a, n, bin_a);
    to_binary(b, n, bin_b);
    int eq[n];
    for (i = 1; i < n; i++)
        eq[i] = ~(bin_a[i] ^ bin_b[i]);
    int g[n];
    int temp;
    for (i = 0; i < n; i++)
    {
        temp = 1;
        for (int k = i + 1; k < n; k++)
            temp &= eq[k];
        g[i] = temp & bin_a[i] & ~bin_b[i];
    }
    int greater = 0;
    for (i = 0; i < n; i++)
        greater |= g[i];
    return ~greater & 1;
    // return 0;
}

int axdc2(int a, int b, int n)
{
    int bin_a[n];
    int bin_b[n];
    int i;
    to_binary(a, n, bin_a);
    to_binary(b, n, bin_b);
    int eq[n];
    for (i = n / 4 + 1; i < n; i++)
        eq[i] = ~(bin_a[i] ^ bin_b[i]);
    int g[n];
    int temp;
    for (i = n / 4; i < n; i++)
    {
        temp = 1;
        for (int k = i + 1; k < n; k++)
            temp &= eq[k];
        g[i] = temp & bin_a[i] & ~bin_b[i];
    }
    int greater = 0;
    for (i = n / 4; i < n; i++)
        greater |= g[i];
    return ~greater & 1;
}

int axdc6(int a, int b, int n)
{
    int bin_a[n];
    int bin_b[n];
    int i;
    to_binary(a, n, bin_a);
    to_binary(b, n, bin_b);
    int eq[n];
    for (i = n / 2 + 1; i < n; i++)
        eq[i] = ~(bin_a[i] ^ bin_b[i]);
    int g[n];
    int temp;
    for (i = n / 2; i < n; i++)
    {
        temp = 1;
        for (int k = i + 1; k < n; k++)
            temp &= eq[k];
        g[i] = temp & bin_a[i] & ~bin_b[i];
    }
    int greater = 0;
    for (i = n / 4; i < n / 2; i++)
        greater |= ~bin_b[i];
    for (i = n / 2; i < n; i++)
        greater |= g[i];
    return ~greater & 1;
}

// int main(int argc, char *argv)
// {
//     int diff_counter = 0;
//     for (int i = 0; i < 16; i++)
//         for (int j = 0; j < 16; j++)
//             if (leq(i,j,ama2,8) != leq(i, j, ama2, 4))
//                 diff_counter++;
//     printf("%d\n", diff_counter);
// }