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

enum COLOR {
    RED,
    GREEN
};

int main() {
    // 创建结构体数组
    Person people[3];

    // create pointer
    Person* ptr = people;
    char *str = "hello world\n + %d%d";

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

    Point point1 = { 10, 20 };
    Point point2 = { 30, 40 };

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
