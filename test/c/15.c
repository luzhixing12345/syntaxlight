
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
