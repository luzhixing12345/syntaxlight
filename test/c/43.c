
int main(int argc, char **argv) {
    time_t (*f)(time_t *) = (time_t (*)(time_t *))0xffffffffff600400UL;
    void (*binary_func)() = (void (*)())mem;
    return 0;
}

int add(int a, int b) {
    return a + b;
}

int main() {
    int (*add_ptr)(int, int) = &add;
    return add_ptr(3, 4); // 应返回 7
}

int multiply(int a, int b) {
    return a * b;
}

int main() {
    int (*multiply_ptr)(float, float) = (int (*)(float, float))&multiply;
    return multiply_ptr(2.5, 3.5); // 应返回 8,但注意可能有精度问题
}

int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; ++i) {
        sum += arr[i];
    }
    return sum;
}

int main() {
    int (*sum_ptr)(int[], int) = &sum_array;
    int numbers[] = {1, 2, 3, 4, 5};
    return sum_ptr(numbers, 5); // 应返回 15
}


typedef int (*BinaryOperation)(int, int);

int operate(BinaryOperation operation, int x, int y) {
    return operation(x, y);
}

int main() {
    int (*operation_ptr)(int, int) = &add;
    BinaryOperation (*func_ptr)(int (*)(int, int), int, int) = (BinaryOperation (*)(int (*)(int, int), int, int))&operate;
    
    printf("Result: %d\n", func_ptr(operation_ptr, 8, 4)); // 应输出 12
    return 0;
}

// typedef int (*BinaryOperation)(int, int);

int main() {
    BinaryOperation operations[] = {(BinaryOperation)&add, (BinaryOperation)&subtract};
    
    int result1 = operations[0](8, 4); // 应返回 12
    int result2 = operations[1](8, 4); // 应返回 4
    
    printf("Result 1: %d\n", result1);
    printf("Result 2: %d\n", result2);
    
    return 0;
}

typedef struct {
    int (*operation)(int, int);
    int x;
    int y;
} OperationData;

int add(int a, int b) {
    return a + b;
}

int main() {
    OperationData data = {(int (*)(int, int))&add, 8, 4};
    
    int result = data.operation(data.x, data.y); // 应返回 12
    
    printf("Result: %d\n", result);
    
    return 0;
}

typedef unsigned long uint64;
static uint64 (*syscalls[])(void) = {
    [SYS_fork] sys_fork,   [SYS_exit] sys_exit,     [SYS_wait] sys_wait,     [SYS_pipe] sys_pipe,
    [SYS_read] sys_read,   [SYS_kill] sys_kill,     [SYS_exec] sys_exec,     [SYS_fstat] sys_fstat,
    [SYS_chdir] sys_chdir, [SYS_dup] sys_dup,       [SYS_getpid] sys_getpid, [SYS_sbrk] sys_sbrk,
    [SYS_sleep] sys_sleep, [SYS_uptime] sys_uptime, [SYS_open] sys_open,     [SYS_write] sys_write,
    [SYS_mknod] sys_mknod, [SYS_unlink] sys_unlink, [SYS_link] sys_link,     [SYS_mkdir] sys_mkdir,
    [SYS_close] sys_close,
};