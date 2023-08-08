void my_function() __attribute__((noreturn));
int my_printf(const char *format, ...) __attribute__((format(printf, 1, 2)));

int my_variable __attribute__((aligned(16)));
struct packed_struct {
    int a;
    char b;
} __attribute__((packed));

typedef int my_int __attribute__((aligned(4)));

typedef int my_int __attribute__((aligned(4)));

static inline uint64
r_fp()
{
  uint64 x;
  asm volatile("mv %0, s0" : "=r" (x) );
  return x;
}