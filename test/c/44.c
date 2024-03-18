static __always_inline struct task_struct *get_current(void) {
    return this_cpu_read_stable(current_task);
}

#define current get_current()

void __init start_kernel(void) {
    char *command_line;
    char *after_dashes;

    set_task_stack_end_magic(&init_task);
    // 一大堆 init
    rest_init();
}

static int run_init_process(const char *init_filename)
{
	argv_init[0] = init_filename;
	return do_execve(getname_kernel(init_filename),
		(const char __user *const __user *)argv_init,
		(const char __user *const __user *)envp_init);
}