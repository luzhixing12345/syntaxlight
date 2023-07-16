void x86_numa_init(void)
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