_%: %.o $(ULIB)
	$(LD) $(LDFLAGS) -T $U/user.ld -o $@ $^
	$(OBJDUMP) -S $@ > $*.asm
	$(OBJDUMP) -t $@ | sed '1,/SYMBOL TABLE/d; s/ .* / /; /^$$/d' > $*.sym

KBUILD_CPPFLAGS-$(CONFIG_WERROR) += -Werror
KBUILD_CPPFLAGS += $(KBUILD_CPPFLAGS-y)
KBUILD_CFLAGS-$(CONFIG_CC_NO_ARRAY_BOUNDS) += -Wno-array-bounds

KBUILD_RUSTFLAGS-$(CONFIG_WERROR) += -Dwarnings
KBUILD_RUSTFLAGS += $(KBUILD_RUSTFLAGS-y)