
#include <stdio.h>

void f(double a[restrict static 3][5]);

int x(int a[static restrict 3]);

double maximum(int n, int m, double a[*][*]);

int main() {
    printf("__STDC_VERSION__ = %ld\n", __STDC_VERSION__);
    int y = sizeof(const int );
    int a[10][20];
    maximum(10, 20, a);
    return 0;
}

int value = 10;
int value2;
int (abc(int x)) {

}

int a, f(int x);

int x[3];
// 123
int main() {
    auto int x = 10; // 123
    printf("x = %d\n",x);
    return 0;
}

// include/linux/container_of.h

#define container_of(ptr, type, member) ({				\
	void *__mptr = (void *)(ptr);					\
	static_assert(__same_type(*(ptr), ((type *)0)->member) ||	\
		      __same_type(*(ptr), void),			\
		      "pointer type mismatch in container_of()");	\
	((type *)(__mptr - offsetof(type, member))); })

static int proc_ipc_dointvec_minmax_orphans(struct ctl_table *table, int write,
		void *buffer, size_t *lenp, loff_t *ppos)
{
	struct ipc_namespace *ns =
		container_of(table->data, struct ipc_namespace, shm_rmid_forced);
	int err;

	err = proc_dointvec_minmax(table, write, buffer, lenp, ppos);

	if (err < 0)
		return err;
	if (ns->shm_rmid_forced)
		shm_destroy_orphaned(ns);
	return err;
}

