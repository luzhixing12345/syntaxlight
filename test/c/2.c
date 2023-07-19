
#include <stdio.h>

void f(double a[restrict static 3][5]);

int x(int a[static restrict 3]);

double maximum(int n, int m, double a[*][*]);

int main() {
    printf("__STDC_VERSION__ = %ld\n", __STDC_VERSION__);
    int y = sizeof(const int );
    int a[10][20];
    maximum(10, 20, a);
    return 0;
}

int value = 10;
int value2;
int (abc(int x)) {

}

int a, f(int x);

int x[3];
// 123
int main() {
    auto int x = 10; // 123
    printf("x = %d\n",x);
    return 0;
}

