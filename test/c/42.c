
f(100, "100");


int pthread_create(pthread_t*, const pthread_attr_t*, void *(*)(void*), void *) __attribute__ ((weak));

extern "C" {
    int func(int);
    int var;
}

__attribute__((section("FOO"))) int global_foo_var = 42;

#pragma section("FOO", read, write)
#pragma once

#define container_of(ptr, type, member) ({})

