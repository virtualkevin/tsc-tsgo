
/home/dev/tssss/tsc-tsgo/packages/tsc-go/dist/tsc-go:     file format elf64-x86-64


Disassembly of section .text:

0000000000404a20 <indexbytebody>:
  404a20:	66 48 0f 6e c0       	movq   %rax,%xmm0
  404a25:	66 0f 60 c0          	punpcklbw %xmm0,%xmm0
  404a29:	66 0f 60 c0          	punpcklbw %xmm0,%xmm0
  404a2d:	66 0f 70 c0 00       	pshufd $0x0,%xmm0,%xmm0
  404a32:	48 83 fb 10          	cmp    $0x10,%rbx
  404a36:	7c 58                	jl     404a90 <indexbytebody+0x70>
  404a38:	48 89 f7             	mov    %rsi,%rdi
  404a3b:	48 83 fb 20          	cmp    $0x20,%rbx
  404a3f:	0f 87 91 00 00 00    	ja     404ad6 <indexbytebody+0xb6>
  404a45:	48 8d 44 1e f0       	lea    -0x10(%rsi,%rbx,1),%rax
  404a4a:	eb 19                	jmp    404a65 <indexbytebody+0x45>
  404a4c:	0f 1f 40 00          	nopl   0x0(%rax)
  404a50:	f3 0f 6f 0f          	movdqu (%rdi),%xmm1
  404a54:	66 0f 74 c8          	pcmpeqb %xmm0,%xmm1
  404a58:	66 0f d7 d1          	pmovmskb %xmm1,%edx
  404a5c:	0f bc d2             	bsf    %edx,%edx
  404a5f:	75 25                	jne    404a86 <indexbytebody+0x66>
  404a61:	48 83 c7 10          	add    $0x10,%rdi
  404a65:	48 39 c7             	cmp    %rax,%rdi
  404a68:	72 e6                	jb     404a50 <indexbytebody+0x30>
  404a6a:	48 89 c7             	mov    %rax,%rdi
  404a6d:	f3 0f 6f 08          	movdqu (%rax),%xmm1
  404a71:	66 0f 74 c8          	pcmpeqb %xmm0,%xmm1
  404a75:	66 0f d7 d1          	pmovmskb %xmm1,%edx
  404a79:	0f bc d2             	bsf    %edx,%edx
  404a7c:	75 08                	jne    404a86 <indexbytebody+0x66>
  404a7e:	49 c7 00 ff ff ff ff 	movq   $0xffffffffffffffff,(%r8)
  404a85:	c3                   	ret
  404a86:	48 29 f7             	sub    %rsi,%rdi
  404a89:	48 01 d7             	add    %rdx,%rdi
  404a8c:	49 89 38             	mov    %rdi,(%r8)
  404a8f:	c3                   	ret
  404a90:	48 85 db             	test   %rbx,%rbx
  404a93:	74 e9                	je     404a7e <indexbytebody+0x5e>
  404a95:	48 8d 46 10          	lea    0x10(%rsi),%rax
  404a99:	66 a9 f0 0f          	test   $0xff0,%ax
  404a9d:	74 19                	je     404ab8 <indexbytebody+0x98>
  404a9f:	f3 0f 6f 0e          	movdqu (%rsi),%xmm1
  404aa3:	66 0f 74 c8          	pcmpeqb %xmm0,%xmm1
  404aa7:	66 0f d7 d1          	pmovmskb %xmm1,%edx
  404aab:	0f bc d2             	bsf    %edx,%edx
  404aae:	74 ce                	je     404a7e <indexbytebody+0x5e>
  404ab0:	39 da                	cmp    %ebx,%edx
  404ab2:	73 ca                	jae    404a7e <indexbytebody+0x5e>
  404ab4:	49 89 10             	mov    %rdx,(%r8)
  404ab7:	c3                   	ret
  404ab8:	f3 0f 6f 4c 1e f0    	movdqu -0x10(%rsi,%rbx,1),%xmm1
  404abe:	66 0f 74 c8          	pcmpeqb %xmm0,%xmm1
  404ac2:	66 0f d7 d1          	pmovmskb %xmm1,%edx
  404ac6:	89 d9                	mov    %ebx,%ecx
  404ac8:	d3 e2                	shl    %cl,%edx
  404aca:	c1 ea 10             	shr    $0x10,%edx
  404acd:	0f bc d2             	bsf    %edx,%edx
  404ad0:	74 ac                	je     404a7e <indexbytebody+0x5e>
  404ad2:	49 89 10             	mov    %rdx,(%r8)
  404ad5:	c3                   	ret
  404ad6:	80 3d e7 63 e2 01 01 	cmpb   $0x1,0x1e263e7(%rip)        # 222aec4 <internal/cpu.X86+0x44>
  404add:	0f 85 62 ff ff ff    	jne    404a45 <indexbytebody+0x25>
  404ae3:	66 48 0f 6e c0       	movq   %rax,%xmm0
  404ae8:	4c 8d 5c 1e e0       	lea    -0x20(%rsi,%rbx,1),%r11
  404aed:	c4 e2 7d 78 c8       	vpbroadcastb %xmm0,%ymm1
  404af2:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  404af9:	00 00 
  404afb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  404b00:	c5 fe 6f 17          	vmovdqu (%rdi),%ymm2
  404b04:	c5 ed 74 d9          	vpcmpeqb %ymm1,%ymm2,%ymm3
  404b08:	c4 e2 7d 17 db       	vptest %ymm3,%ymm3
  404b0d:	75 26                	jne    404b35 <indexbytebody+0x115>
  404b0f:	48 83 c7 20          	add    $0x20,%rdi
  404b13:	4c 39 df             	cmp    %r11,%rdi
  404b16:	7c e8                	jl     404b00 <indexbytebody+0xe0>
  404b18:	4c 89 df             	mov    %r11,%rdi
  404b1b:	c5 fe 6f 17          	vmovdqu (%rdi),%ymm2
  404b1f:	c5 ed 74 d9          	vpcmpeqb %ymm1,%ymm2,%ymm3
  404b23:	c4 e2 7d 17 db       	vptest %ymm3,%ymm3
  404b28:	75 0b                	jne    404b35 <indexbytebody+0x115>
  404b2a:	c5 f8 77             	vzeroupper
  404b2d:	49 c7 00 ff ff ff ff 	movq   $0xffffffffffffffff,(%r8)
  404b34:	c3                   	ret
  404b35:	c5 fd d7 d3          	vpmovmskb %ymm3,%edx
  404b39:	0f bc d2             	bsf    %edx,%edx
  404b3c:	48 29 f7             	sub    %rsi,%rdi
  404b3f:	48 01 fa             	add    %rdi,%rdx
  404b42:	49 89 10             	mov    %rdx,(%r8)
  404b45:	c5 f8 77             	vzeroupper
  404b48:	c3                   	ret

Disassembly of section .plt:
