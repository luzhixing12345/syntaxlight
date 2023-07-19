int main() {
    int arr[5] = {1, 2, 3, 4, 5};
    int* ptr1 = arr;
    int* ptr2 = &arr[3];

    // 指针相减得到元素之间的距离
    ptrdiff_t distance = ptr2 - ptr1;
    
    // 访问指针所指向的元素
    int value = *ptr1;

    // 使用指针访问数组元素
    for (int i = 0; i < 5; i++) {
        printf("Value at index %d: %d\n", i, *(arr + i));
    }

    return 0;
}

int main() {
    int** matrix;
    int rows = 3;
    int cols = 4;

    // 分配二维数组内存
    matrix = (int**)malloc(rows * sizeof(int*));
    for (int i = 0; i < rows; i++) {
        matrix[i] = (int*)malloc(cols * sizeof(int));
    }

    // 访问二维数组元素
    matrix[1][2] = 10;
    int value = *(*(matrix + 1) + 2);

    // 释放二维数组内存
    for (int i = 0; i < rows; i++) {
        free(matrix[i]);
    }
    free(matrix);

    return 0;
}

int add(int a, int b) {
    return a + b;
}

int subtract(int a, int b) {
    return a - b;
}

int main() {
    int (*funcPtr)(int, int);

    // 指向加法函数的指针
    funcPtr = &add;
    int sum = funcPtr(3, 4);

    // 指向减法函数的指针
    funcPtr = &subtract;
    int difference = funcPtr(5, 2);

    return 0;
}
