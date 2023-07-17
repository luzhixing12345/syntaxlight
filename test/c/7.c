#include <stdio.h>

// 结构体定义
struct Person {
    char name[20];
    int age;
};

// 函数声明
int addNumbers(int x, int y);
void printArray(int arr[], int size);

int main() {
    // 变量声明与赋值
    int a = 10;
    float b = 3.14;
    char c = 'A';

    // 数组
    int numbers[] = {1, 2, 3, 4, 5};

    // 结构体实例化
    struct Person person;
    strcpy(person.name, "John");
    person.age = 25;

    // 条件语句
    if (a > 5 && b < 10.0) {
        printf("a is greater than 5 and b is less than 10.0\n");
    } else if (a == 5 || c == 'B') {
        printf("a is equal to 5 or c is 'B'\n");
    } else {
        printf("None of the conditions are satisfied\n");
    }

    // 循环语句
    int i;
    for (i = 0; i < 5; i++) {
        printf("%d ", numbers[i]);
    }
    printf("\n");

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

    // 函数调用
    int sum = addNumbers(a, 5);
    printf("Sum: %d\n", sum);

    // 数组作为函数参数
    printArray(numbers, 5);

    return 0;
}

// 自定义函数
int addNumbers(int x, int y) {
    return x + y;
}

void printArray(int arr[], int size) {
    int i;
    for (i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
    printf("\n");
}
