#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))

int main() {
    int num1 = 10;
    int num2 = 20;
    int max = MAX(num1, num2);

    printf("Max: %d\n", max);
    return 0;
}

int f() {
    int i = 0;

    loop_start:
    for (; i < 10; i++) {
        if (i == 5) {
            goto loop_end;
        }
        printf("Value: %d\n", i);
    }

    loop_end:
    printf("Loop ended at %d\n", i);

    return 0;
}
