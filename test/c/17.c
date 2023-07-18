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
