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