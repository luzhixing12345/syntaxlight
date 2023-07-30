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


int i;
char *s, *dest;
int src;
int *other_numbers;
argparse_option options[] = {
    XBOX_ARG_BOOLEAN(NULL, [-h][--help][help = "show help information"]),
    XBOX_ARG_BOOLEAN(NULL, [-v][--version][help = "show version"]),
    XBOX_ARG_INT(&i, [-i][--input][help = "input file"]),
    XBOX_ARG_STR(&s, [-s][--string]),
    XBOX_ARG_STR_GROUP(&dest, [name = dest][help = "destination"]),
    XBOX_ARG_INT_GROUP(&src, [name = src][help = "source"]),
    XBOX_ARG_INT_GROUPS(&other_numbers, [name = "other-number"][help = "catch the other number..."]),
    XBOX_ARG_END()
};