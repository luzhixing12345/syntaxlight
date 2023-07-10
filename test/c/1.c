#include <stdio.h>

void f(double a[restrict static 3][5]);

int x(int a[static restrict 3]);

double maximum(int n, int m, double a[*][*]);

int main() {
    printf("__STDC_VERSION__ = %ld\n", __STDC_VERSION__);
    return 0;
}