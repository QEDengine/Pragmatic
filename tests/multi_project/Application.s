	.text
	.def	@feat.00;
	.scl	3;
	.type	0;
	.endef
	.globl	@feat.00
.set @feat.00, 0
	.file	"Application.cpp"
	.def	main;
	.scl	2;
	.type	32;
	.endef
	.globl	main                            # -- Begin function main
	.p2align	4, 0x90
main:                                   # @main
.seh_proc main
# %bb.0:
	pushq	%rax
	.seh_stackalloc 8
	.seh_endprologue
	movl	$0, 4(%rsp)
	xorl	%eax, %eax
	popq	%rcx
	retq
	.seh_endproc
                                        # -- End function
	.addrsig
