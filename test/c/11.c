#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int calculate(int (*operation)(int, int), int a, int b) {
    return operation(a, b);
}

int main() {
    int x = 10;
    int y = 5;

    int sum = calculate(add, x, y);
    int difference = calculate(subtract, x, y);
    operation(a, b); // GDT 的范围
    printf("Sum: %d\n", sum);
    printf("Difference: %d\n", difference);

    return 0;
}
