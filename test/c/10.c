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
