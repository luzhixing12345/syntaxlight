
# c
## [1.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/1.c)

```c
#define container_of(ptr, type, member) ({				\
	void *__mptr = (void *)(ptr);					\
	static_assert(__same_type(*(ptr), ((type *)0)->member) ||	\
		      __same_type(*(ptr), void),			\
		      "pointer type mismatch in container_of()");	\
	((type *)(__mptr - offsetof(type, member))); })

static int proc_ipc_dointvec_minmax_orphans(struct ctl_table *table, int write,
		void *buffer, size_t *lenp, loff_t *ppos)
{
	struct ipc_namespace *ns =
		container_of(table->data, struct ipc_namespace, shm_rmid_forced);
	int err;

	err = proc_dointvec_minmax(table, write, buffer, lenp, ppos);

	if (err < 0)
		return err;
	if (ns->shm_rmid_forced)
		shm_destroy_orphaned(ns);
	return err;
}


int i;
char *s, *dest;
int src;
int *other_numbers;
argparse_option options[] = {
    XBOX_ARG_BOOLEAN(NULL, [-h][--help][help = "show help information"]),
    XBOX_ARG_BOOLEAN(NULL, [-v][--version][help = "show version"]),
    XBOX_ARG_INT(&i, [-i][--input][help = "input file"]),
    XBOX_ARG_STR(&s, [-s][--string]),
    XBOX_ARG_STR_GROUP(&dest, [name = dest][help = "destination"]),
    XBOX_ARG_INT_GROUP(&src, [name = src][help = "source"]),
    XBOX_ARG_INT_GROUPS(&other_numbers, [name = "other-number"][help = "catch the other number..."]),
    XBOX_ARG_END()
};
```
## [2.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/2.c)

```c

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

// include/linux/container_of.h

#define container_of(ptr, type, member) ({				\
	void *__mptr = (void *)(ptr);					\
	static_assert(__same_type(*(ptr), ((type *)0)->member) ||	\
		      __same_type(*(ptr), void),			\
		      "pointer type mismatch in container_of()");	\
	((type *)(__mptr - offsetof(type, member))); })

static int proc_ipc_dointvec_minmax_orphans(struct ctl_table *table, int write,
		void *buffer, size_t *lenp, loff_t *ppos)
{
	struct ipc_namespace *ns =
		container_of(table->data, struct ipc_namespace, shm_rmid_forced);
	int err;

	err = proc_dointvec_minmax(table, write, buffer, lenp, ppos);

	if (err < 0)
		return err;
	if (ns->shm_rmid_forced)
		shm_destroy_orphaned(ns);
	return err;
}
```
## [3.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/3.c)

```c
# define A
# ifdef A // 123

# endif

struct x {
    int;
    int;
};

int f(struct x) {
    
}

```
## [4.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/4.c)

```c

int f(a,b) int a, b; {
    return 1;
}
```
## [5.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/5.c)

```c
void x86_numa_init(void)
{
    if (!numa_off) {
#ifdef CONFIG_ACPI_NUMA
        if (!numa_init(x86_acpi_numa_init))
            return;
#endif
#ifdef CONFIG_AMD_NUMA
        if (!numa_init(amd_numa_init))
            return;
#endif
    }
    numa_init(dummy_numa_init);
}
```
## [6.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/6.c)

```c
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

```
## [7.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/7.c)

```c
#include <stdio.h>
#include "stdio.h"

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

```
## [8.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/8.c)

```c
#include <stdio.h>

struct Point {
    int x;
    int y;
};

int main() {
    struct Point p;
    p.x = 10;
    p.y = 20;

    printf("x: %d, y: %d\n", p.x, p.y);
    for (int i = 0; i < 10; i++) {
        printf("%d\n", i);
    }
    return 0;
}

int f() {
    return 1;
}


```
## [9.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/9.c)

```c
#include <stdio.h>

enum Color {
    RED,
    GREEN,
    BLUE
};

int main() {
    enum Color c = BLUE;

    if (c == RED) {
        printf("The color is red\n");
    } else if (c == GREEN) {
        printf("The color is green\n");
    } else if (c == BLUE) {
        printf("The color is blue\n");
    }

    return 0;
}

```
## [10.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/10.c)

```c
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point start;
    Point end;
} Line;

typedef struct {
    char name[20];
    int age;
    Line address;
    void (*printInfo)(const char*, int);
} Person;

void printPersonInfo(const char* name, int age) {
    printf("Name: %s\n", name);
    printf("Age: %d\n", age);
}

int main() {
    // 嵌套结构体
    Line line;
    line.start.x = 0;
    line.start.y = 0;
    line.end.x = 10;
    line.end.y = 10;

    // 复杂结构体
    Person person;
    snprintf(person.name, sizeof(person.name), "John Doe");
    person.age = 30;
    person.address = line;
    person.printInfo = printPersonInfo;

    // 调用函数指针
    person.printInfo(person.name, person.age);

    return 0;
}

```
## [11.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/11.c)

```c
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

```
## [12.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/12.c)

```c
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    const Point start;
    const Point end;
} Line;

void printPersonInfo(const char* name, int age) {
    printf("Name: %s\n", name);
    printf("Age: %d\n", age);
}
```
## [13.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/13.c)

```c


#include <stdio.h>

// func(3)

    int x = 10;
    if (x) {
    printf("1");
} else {
    printf("2");
}



```
## [14.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/14.c)

```c

int x = 10;
x += 15;
```
## [15.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/15.c)

```c

#include <stdio.h>
#include <stdio.h>


int f1() {
  int value = 10;
  int *ptr = &value;
  int **ptr2 = &ptr;

  printf("Value: %d\n", **ptr2);
  return 0;
}

int f2() {
  int num1 = 10, num2 = 20, num3 = 30;
  int *arr[3] = {&num1, &num2, &num3};

  for (int i = 0; i < 3; i++) {
    printf("Value at index %d: %d\n", i, *arr[i]);
  }
  return 0;
}

void greet() { printf("Hello, world!\n"); }

int f() {
  void (*funcPtr)() = greet;
  funcPtr();

  return 0;
}

typedef struct {
  int x;
  int y;
} Point;

int f3() {
  Point point;
  Point *ptr = &point;

  ptr->x = 10;
  ptr->y = 20;

  printf("Coordinates: (%d, %d)\n", ptr->x, ptr->y);
  return 0;
}

int f4() {
  int size = 5;
  int *arr = (int *)malloc(size * sizeof(int));

  if (arr != NULL) {
    for (int i = 0; i < size; i++) {
      arr[i] = i + 1;
    }

    for (int i = 0; i < size; i++) {
      printf("Value at index %d: %d\n", i, arr[i]);
    }

    free(arr);
  }

  return 0;
}

```
## [16.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/16.c)

```c
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    char name[20];
    int age;
    Point* position;
} Person;

enum COLOR { RED, GREEN };

int 
main() 
{
    // 创建结构体数组
    Person people[3];

    // create pointer
    Person* ptr = people;
    char* str = "hello world\n + %d%d";

    // 创建动态分配的结构体指针数组
    Person** dynamicPtrArray = (Person**)malloc(2 * sizeof(Person*));
    for (int i = 0; i < 2; i++) {
        dynamicPtrArray[i] = (Person*)malloc(sizeof(Person));
    }

    // 设置结构体成员的值
    people[0].age = 20;
    people[1].age = 25;
    people[2].age = 30;

    strcpy(people[0].name, "Alice");
    strcpy(people[1].name, "Bob");
    strcpy(people[2].name, "Charlie");

    Point point1 = {10, 20};
    Point point2 = {30, 40};

    people[0].position = &point1;
    people[1].position = &point2;
    people[2].position = NULL;

    // 通过指针访问结构体成员的值
    printf("Name: %s, Age: %d\n", ptr->name, ptr->age);
    printf("Position: (%d, %d)\n", ptr->position->x, ptr->position->y);

    // 释放动态分配的内存
    for (int i = 0; i << 2; i++) {
        free(dynamicPtrArray[i]);
    }
    free(dynamicPtrArray);

    return 0;
}

```
## [17.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/17.c)

```c
#include <stdio.h>

#define MAX(a, b) ((a) > (b) ? (a) : (b))

void printf(const char *, ...);

#define PRINT_MULTILINE(str1, str2) \ 
    printf("%s \\\n%s\n", str1, str2)

#define ANOTHER_MAX(a,b) MAX(a,b)

int main() {
    PUTS(10,20);
    int num1 = 10;
    int num2 = 20;
    int max = MAX(num1, num2);

    printf("Max: %d\n", max);
    return 0;
}

int x() {
    PRINT_MULTILINE("This is a long",
                    "multiline string.");

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

```
## [18.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/18.c)

```c
#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    char name[20];
    int age;
    Point position;
} Person;

int main() {
    // 结构体初始化
    Point point = { 10, 20 };
    Person person = { "Alice", 25, { 30, 40 } };

    // 结构体指针初始化
    Person* ptr = &(Person) { "Bob", 30, { 50, 60 } };

    // 输出结构体成员的值
    printf("Point: (%d, %d)\n", point.x, point.y);
    printf("Person: Name=%s, Age=%d, Position=(%d, %d)\n",
           person.name, person.age, person.position.x, person.position.y);
    printf("Pointer: Name=%s, Age=%d, Position=(%d, %d)\n",
           ptr->name, ptr->age, ptr->position.x, ptr->position.y);

    return 0;
}

```
## [19.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/19.c)

```c
// typedef struct Point{
//     int x;
//     int y;
// } Point;

// typedef struct {
//     char name[20];
//     int age;
//     Point position;
// } Person;

// 函数返回指向结构体的指针
struct Point* createPoint(int x, int y);

// 结构体指针作为参数
void updatePersonInfo(Person* person);
void updatePersonInfo(Person);
void updatePersonInfo(Person*, int, char*, Student*);

// 函数返回函数指针
int (*getOperation(int choice))(int, int);

// 函数参数为数组指针和大小
void processArray(int* arr, int size);

// 函数参数为多个不同类型的指针
void processMultiplePointers(int* ptr1, float* ptr2, char* ptr3);

// 整数数组作为参数
void printIntArray(int arr[], int size);

// 字符串指针作为参数
void printString(const char* str);

// 函数指针作为参数
void performOperation(int (*operation)(int, int), int num1, int num2);


```
## [20.c](https://github.com/luzhixing12345/syntaxlight/tree/main/test/c/20.c)

```c
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

```
