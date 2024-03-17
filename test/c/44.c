static __always_inline struct task_struct *get_current(void) {
    return this_cpu_read_stable(current_task);
}

#define current get_current()

void __init start_kernel(void)
{
	char *command_line;
	char *after_dashes;

	set_task_stack_end_magic(&init_task);
    // 一大堆 init
    rest_init();
}