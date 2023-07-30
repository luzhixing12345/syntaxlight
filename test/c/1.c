static int __init dummy_numa_init(void)
{
    printk(KERN_INFO "%s\n",
           numa_off ? "NUMA turned off" : "No NUMA configuration found");
    /* max_pfn是e820探测到的最大物理内存页,其初始化是max_pfn = e820__end_of_ram_pfn() */
    // printk(KERN_INFO "Faking a node at [mem %#018Lx-%#018Lx]\n",
    //        0LLU, PFN_PHYS(max_pfn) - 1);
    /* 一个nodemask_t是 位图, 最多支持MAX_NUMNODES个node
     * 这里将node 0置位
     */
    node_set(0, numa_nodes_parsed);
}

char *x = "asdjkl" "asdjkl""asdjkl" "asdjkl""asdjkl" "asdjkl";
