void DoCheck(uint32_t dwSomeValue)
{
   uint32_t dwRes;

   // Assumes dwSomeValue is not zero.
   __asm__ ("bsfl %1,%0"
     : "=r" (dwRes)
     : "r" (dwSomeValue)
     : "cc");

   assert(dwRes > 3);
}

uint64_t msr;

__asm__ volatile ( "rdtsc\n\t"    // Returns the time in EDX:EAX.
        "shl $32, %%rdx\n\t"  // Shift the upper bits left.
        "or %%rdx, %0"        // 'Or' in the lower bits.
        : "=a" (msr)
        : 
        : "rdx");

printf("msr: %llx\n", msr);

// Do other work...

// Reprint the timestamp
__asm__ volatile ( "rdtsc\n\t"    // Returns the time in EDX:EAX.
        "shl $32, %%rdx\n\t"  // Shift the upper bits left.
        "or %%rdx, %0"        // 'Or' in the lower bits.
        : "=a" (msr)
        : 
        : "rdx");

printf("msr: %llx\n", msr);

void print() {
    asm("movq $13, %%rdx \n\t"
        "movq %0, %%rcx \n\t"
        "movq $0, %%rbx \n\t"
        "movq $4, %%rax \n\t"
        "int $0x80 \n\t" ::"r"(str)
        : "rdx", "rcx", "rbx");
}