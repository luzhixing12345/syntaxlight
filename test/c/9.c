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
