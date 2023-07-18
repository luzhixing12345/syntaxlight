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

