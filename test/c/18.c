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
