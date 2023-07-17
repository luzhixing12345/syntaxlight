#include <stdio.h>

int main() {
    // 变量声明与赋值
    int a = 10;
    float b = 3.14;
    char c = 'A';

    // 条件语句
    if (a > 5) {
        printf("a is greater than 5\n");
    } else {
        printf("a is less than or equal to 5\n");
    }

    // 循环语句
    int i;
    for (i = 0; i < 5; i++) {
        printf("Iteration %d\n", i);
    }

    // switch语句
    int choice = 2;
    switch (choice) {
        case 1:
            printf("You selected option 1\n");
            break;
        case 2:
            printf("You selected option 2\n");
            break;
        case 3:
            printf("You selected option 3\n");
            break;
        default:
            printf("Invalid choice\n");
    }

    // 函数定义与调用
    int sum = addNumbers(a, 5);
    printf("Sum: %d\n", sum);

    return 0;
}

// 自定义函数
int addNumbers(int x, int y) {
    return x + y;
}
