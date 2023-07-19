#include <stdio.h>

int main() {
    int x = 10;
    int *p = &x;
    int **pp = &p;

    printf("Value of x: %d\n", **pp);

    return 0;
}

#include <stdio.h>

int f() {
    int arr[2][3] = {{1, 2, 3}, {4, 5, 6}};
    int (*p)[3] = arr;

    printf("Value of arr[0][0]: %d\n", **p);

    return 0;
}

#include <stdio.h>

typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    Point p1;
    Point p2;
} Rectangle;

int main() {
    Point p = {10, 20};
    Point *ptr1 = &p;
    Rectangle r = {*ptr1, p};
    Rectangle *ptr2 = &r;

    printf("Value of p.x: %d\n", (*ptr2).p1.x);
    printf("Value of p.y: %d\n", ptr2->p2.y);

    return 0;
}
