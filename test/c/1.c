#include <stdio.h>
#if 123
#endif	/* comment*/

#define FUNC(a,b) (a+b)

typedef struct MyStruct{
    int name[20];
    struct MyStruct* ptr;
    int a;
} MyStruct;

int main(int argc, const char**argv) {
    printf("hello world\n");
    int x = 10; // comment
    
    if (x > 10) {
        MyStruct a;
    } else {
        switch (x) {
            case 1:
                return 1;
        }
    }
    return 0;
}