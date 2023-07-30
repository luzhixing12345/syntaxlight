int setup(void* BIOS) {
    long __res;
    __asm__ volatile("int $0x80" : "=a"(__res) : "0"(0), "b"((long)(BIOS)));
    if (__res >= 0) return (int)__res;
    errno = -__res;
    return -1;
}

static int __init dummy_numa_init(void)
{
	printk(KERN_INFO "%s\n",
	       numa_off ? "NUMA turned off" : "No NUMA configuration found");
    /* max_pfn是e820探测到的最大物理内存页,其初始化是max_pfn = e820__end_of_ram_pfn() */
	printk(KERN_INFO "Faking a node at [mem %#018Lx-%#018Lx]\n",
	       0LLU, PFN_PHYS(max_pfn) - 1);
    /* 一个nodemask_t是 位图, 最多支持MAX_NUMNODES个node
     * 这里将node 0置位
     */
	node_set(0, numa_nodes_parsed);
    /* 将node 0的起始和结束地址记录起来 */
	numa_add_memblk(0, 0, PFN_PHYS(max_pfn));

	return 0;
}

int __init numa_add_memblk(int nid, u64 start, u64 end)
{
	return numa_add_memblk_to(nid, start, end, &numa_meminfo);
}

// arch/x86/mm/numa_internal.h
struct numa_meminfo {
	int			nr_blks;
	struct numa_memblk	blk[NR_NODE_MEMBLKS];
};

struct numa_memblk {
	u64			start;
	u64			end;
	int			nid;
};

static int __init numa_add_memblk_to(int nid, u64 start, u64 end,
				     struct numa_meminfo *mi)
{
	/* ignore zero length blks */
	if (start == end)
		return 0;

	/* whine about and ignore invalid blks */
	if (start > end || nid < 0 || nid >= MAX_NUMNODES) {
		pr_warn("Warning: invalid memblk node %d [mem %#010Lx-%#010Lx]\n",
			nid, start, end - 1);
		return 0;
	}

	if (mi->nr_blks >= NR_NODE_MEMBLKS) {
		pr_err("too many memblk ranges\n");
		return -EINVAL;
	}

	mi->blk[mi->nr_blks].start = start;
	mi->blk[mi->nr_blks].end = end;
	mi->blk[mi->nr_blks].nid = nid;
	mi->nr_blks++;
	return 0;
}

// arch/x86/kernel/setup.c | setup_arch
// arch/x86/mm/numa_64.c   | initmem_init
// arch/x86/mm/numa.c      | x86_numa_init
// arch/x86/mm/numa.c      | numa_init

void __init x86_numa_init(void)
{
	if (!numa_off) {
#ifdef CONFIG_ACPI_NUMA
		if (!numa_init(x86_acpi_numa_init))
			return;
#endif
#ifdef CONFIG_AMD_NUMA
		if (!numa_init(amd_numa_init))
			return;
#endif
	}
	numa_init(dummy_numa_init);
}