#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_LENGTH 1024

char *re2postfix(char *re, char *buf) {
    int pipe_number, token_number;
    char *dst;
    struct {
        int pipe_number;
        int token_number;
    } paren[100], *p;
    p = paren;
    dst = buf;
    pipe_number = 0;
    token_number = 0;
    if (strlen(re) >= MAX_LENGTH / 2) {
        printf("regexp too long\n");
        return NULL;
    }
    for (; *re; re++) {
        printf("[%c]: ", *re);
        switch (*re) {
            case '(':
                if (token_number > 1) {
                    --token_number;
                    *dst++ = '.';
                }
                if (p >= paren + 100)
                    return NULL;
                p->pipe_number = pipe_number;
                p->token_number = token_number;
                printf("token_number = [%d] pipe_number = [%d] -> p++\n", token_number, pipe_number);
                p++;
                pipe_number = 0;
                token_number = 0;
                break;
            case '|':
                printf("token_number = [%d] ", token_number);
                // | 前需要元素
                if (token_number == 0)
                    return NULL;
                while (--token_number > 0) *dst++ = '.';
                pipe_number++;
                printf("pipe_number = [%d]\n", pipe_number);
                break;
            case ')':
                // ) 不可以开头
                if (p == paren)
                    return NULL;
                // () 内部需要元素
                if (token_number == 0)
                    return NULL;
                printf("token_number = [%d] pipe_number = [%d]\n", token_number, pipe_number);
                while (--token_number > 0) *dst++ = '.';
                for (; pipe_number > 0; pipe_number--) *dst++ = '|';
                --p;
                pipe_number = p->pipe_number;
                token_number = p->token_number;
                token_number++;
                break;
            case '*':
            case '+':
            case '?':
                printf("\n");
                if (token_number == 0)
                    return NULL;
                *dst++ = *re;
                break;
            default:
                printf("token_number = [%d]", token_number);
                if (token_number > 1) {
                    --token_number;
                    *dst++ = '.';
                }
                *dst++ = *re;
                token_number++;
                printf(" token_number = [%d]\n", token_number);
                break;
        }
    }
    // 左右括号不匹配
    if (p != paren)
        return NULL;
    while (--token_number > 0) *dst++ = '.';
    for (; pipe_number > 0; pipe_number--) *dst++ = '|';
    *dst = 0;
    return buf;
}

int main(int argc, char **argv) {
    int i;
    char buf[MAX_LENGTH];
    if (!re2postfix(argv[1], buf)) {
        fprintf(stderr, "bad regexp %s\n", argv[1]);
        return 1;
    }
    printf("\npostfix = %s\n", buf);
    return 0;
}