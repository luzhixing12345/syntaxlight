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

static void __init_refok rest_init(void) {
    int pid;

    rcu_scheduler_starting();
    smpboot_thread_init();
    /*
     * We need to spawn init first so that it obtains pid 1, however
     * the init task will end up wanting to create kthreads, which, if
     * we schedule it before we create kthreadd, will OOPS.
     */
    kernel_thread(kernel_init, NULL, CLONE_FS);
    numa_default_policy();
    pid = kernel_thread(kthreadd, NULL, CLONE_FS | CLONE_FILES);
    rcu_read_lock();
    kthreadd_task = find_task_by_pid_ns(pid, &init_pid_ns);
    rcu_read_unlock();
    complete(&kthreadd_done);

    /*
     * The boot idle thread must execute schedule()
     * at least once to get things moving:
     */
    init_idle_bootup_task(current);
    schedule_preempt_disabled();
    /* Call into cpu_idle with preempt disabled */
    cpu_startup_entry(CPUHP_ONLINE);
}