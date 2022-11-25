#include <iostream>
#include <cmath>
#include <omp.h>

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

int axdc1(int a, int b, int n)
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
 
void calc_metrics(int n)
{
    int size = pow(2, n);
    auto count = 0;

    #pragma omp parallel for reduction(+:count)
    for (auto i=0; i < size; i++) {
        for (auto j=0; j < size; j++) {
            count += (axdc1(i, j, n) == (i <= j)? 0 : 1);
        }
    }
    std::cout << "n = " << n << std::endl;
    std::cout << "ED = " << count << std::endl;
    std::cout << "ER = " << 100 * count / pow(size, 2) << std::endl;
    std::cout << std::endl;
}

int main()
{
    omp_set_num_threads(8);
    std::cout << "Number of devices: " << omp_get_num_devices() << std::endl;
    for (auto i=13; i <= 20; ++i) {
        calc_metrics(i);
    }
}