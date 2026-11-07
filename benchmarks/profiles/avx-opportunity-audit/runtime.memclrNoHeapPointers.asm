
/home/dev/tssss/tsc-tsgo/packages/tsc-go/dist/tsc-go:     file format elf64-x86-64


Disassembly of section .text:

0000000000491940 <runtime.memclrNoHeapPointers>:
  491940:	48 89 c7             	mov    %rax,%rdi
  491943:	48 31 c0             	xor    %rax,%rax
  491946:	48 85 db             	test   %rbx,%rbx
  491949:	0f 84 f7 01 00 00    	je     491b46 <runtime.memclrNoHeapPointers+0x206>
  49194f:	48 83 fb 02          	cmp    $0x2,%rbx
  491953:	0f 86 e6 01 00 00    	jbe    491b3f <runtime.memclrNoHeapPointers+0x1ff>
  491959:	48 83 fb 04          	cmp    $0x4,%rbx
  49195d:	0f 86 e4 01 00 00    	jbe    491b47 <runtime.memclrNoHeapPointers+0x207>
  491963:	48 83 fb 08          	cmp    $0x8,%rbx
  491967:	0f 82 e3 01 00 00    	jb     491b50 <runtime.memclrNoHeapPointers+0x210>
  49196d:	0f 84 e4 01 00 00    	je     491b57 <runtime.memclrNoHeapPointers+0x217>
  491973:	48 83 fb 10          	cmp    $0x10,%rbx
  491977:	0f 86 de 01 00 00    	jbe    491b5b <runtime.memclrNoHeapPointers+0x21b>
  49197d:	48 83 fb 20          	cmp    $0x20,%rbx
  491981:	0f 86 dd 01 00 00    	jbe    491b64 <runtime.memclrNoHeapPointers+0x224>
  491987:	48 83 fb 40          	cmp    $0x40,%rbx
  49198b:	0f 86 e0 01 00 00    	jbe    491b71 <runtime.memclrNoHeapPointers+0x231>
  491991:	48 81 fb 80 00 00 00 	cmp    $0x80,%rbx
  491998:	0f 86 ed 01 00 00    	jbe    491b8b <runtime.memclrNoHeapPointers+0x24b>
  49199e:	48 81 fb 00 01 00 00 	cmp    $0x100,%rbx
  4919a5:	0f 86 14 02 00 00    	jbe    491bbf <runtime.memclrNoHeapPointers+0x27f>
  4919ab:	80 3d 23 95 d9 01 01 	cmpb   $0x1,0x1d99523(%rip)        # 222aed5 <internal/cpu.X86+0x55>
  4919b2:	75 0d                	jne    4919c1 <runtime.memclrNoHeapPointers+0x81>
  4919b4:	48 81 fb 00 08 00 00 	cmp    $0x800,%rbx
  4919bb:	0f 83 f7 00 00 00    	jae    491ab8 <runtime.memclrNoHeapPointers+0x178>
  4919c1:	80 3d fc 94 d9 01 01 	cmpb   $0x1,0x1d994fc(%rip)        # 222aec4 <internal/cpu.X86+0x44>
  4919c8:	0f 84 97 00 00 00    	je     491a65 <runtime.memclrNoHeapPointers+0x125>
  4919ce:	f3 44 0f 7f 3f       	movdqu %xmm15,(%rdi)
  4919d3:	f3 44 0f 7f 7f 10    	movdqu %xmm15,0x10(%rdi)
  4919d9:	f3 44 0f 7f 7f 20    	movdqu %xmm15,0x20(%rdi)
  4919df:	f3 44 0f 7f 7f 30    	movdqu %xmm15,0x30(%rdi)
  4919e5:	f3 44 0f 7f 7f 40    	movdqu %xmm15,0x40(%rdi)
  4919eb:	f3 44 0f 7f 7f 50    	movdqu %xmm15,0x50(%rdi)
  4919f1:	f3 44 0f 7f 7f 60    	movdqu %xmm15,0x60(%rdi)
  4919f7:	f3 44 0f 7f 7f 70    	movdqu %xmm15,0x70(%rdi)
  4919fd:	f3 44 0f 7f bf 80 00 	movdqu %xmm15,0x80(%rdi)
  491a04:	00 00 
  491a06:	f3 44 0f 7f bf 90 00 	movdqu %xmm15,0x90(%rdi)
  491a0d:	00 00 
  491a0f:	f3 44 0f 7f bf a0 00 	movdqu %xmm15,0xa0(%rdi)
  491a16:	00 00 
  491a18:	f3 44 0f 7f bf b0 00 	movdqu %xmm15,0xb0(%rdi)
  491a1f:	00 00 
  491a21:	f3 44 0f 7f bf c0 00 	movdqu %xmm15,0xc0(%rdi)
  491a28:	00 00 
  491a2a:	f3 44 0f 7f bf d0 00 	movdqu %xmm15,0xd0(%rdi)
  491a31:	00 00 
  491a33:	f3 44 0f 7f bf e0 00 	movdqu %xmm15,0xe0(%rdi)
  491a3a:	00 00 
  491a3c:	f3 44 0f 7f bf f0 00 	movdqu %xmm15,0xf0(%rdi)
  491a43:	00 00 
  491a45:	48 81 eb 00 01 00 00 	sub    $0x100,%rbx
  491a4c:	48 81 c7 00 01 00 00 	add    $0x100,%rdi
  491a53:	48 81 fb 00 01 00 00 	cmp    $0x100,%rbx
  491a5a:	0f 83 6e ff ff ff    	jae    4919ce <runtime.memclrNoHeapPointers+0x8e>
  491a60:	e9 e1 fe ff ff       	jmp    491946 <runtime.memclrNoHeapPointers+0x6>
  491a65:	c5 f9 ef c0          	vpxor  %xmm0,%xmm0,%xmm0
  491a69:	48 81 fb 00 00 00 02 	cmp    $0x2000000,%rbx
  491a70:	73 6f                	jae    491ae1 <runtime.memclrNoHeapPointers+0x1a1>
  491a72:	c5 fe 7f 07          	vmovdqu %ymm0,(%rdi)
  491a76:	c5 fe 7f 47 20       	vmovdqu %ymm0,0x20(%rdi)
  491a7b:	c5 fe 7f 47 40       	vmovdqu %ymm0,0x40(%rdi)
  491a80:	c5 fe 7f 47 60       	vmovdqu %ymm0,0x60(%rdi)
  491a85:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  491a8c:	48 81 c7 80 00 00 00 	add    $0x80,%rdi
  491a93:	48 81 fb 80 00 00 00 	cmp    $0x80,%rbx
  491a9a:	73 d6                	jae    491a72 <runtime.memclrNoHeapPointers+0x132>
  491a9c:	c5 fe 7f 44 1f e0    	vmovdqu %ymm0,-0x20(%rdi,%rbx,1)
  491aa2:	c5 fe 7f 44 1f c0    	vmovdqu %ymm0,-0x40(%rdi,%rbx,1)
  491aa8:	c5 fe 7f 44 1f a0    	vmovdqu %ymm0,-0x60(%rdi,%rbx,1)
  491aae:	c5 fe 7f 44 1f 80    	vmovdqu %ymm0,-0x80(%rdi,%rbx,1)
  491ab4:	c5 f8 77             	vzeroupper
  491ab7:	c3                   	ret
  491ab8:	80 3d 05 94 d9 01 01 	cmpb   $0x1,0x1d99405(%rip)        # 222aec4 <internal/cpu.X86+0x44>
  491abf:	75 0d                	jne    491ace <runtime.memclrNoHeapPointers+0x18e>
  491ac1:	c5 f9 ef c0          	vpxor  %xmm0,%xmm0,%xmm0
  491ac5:	48 81 fb 00 00 00 02 	cmp    $0x2000000,%rbx
  491acc:	73 13                	jae    491ae1 <runtime.memclrNoHeapPointers+0x1a1>
  491ace:	48 89 d9             	mov    %rbx,%rcx
  491ad1:	48 c1 e9 03          	shr    $0x3,%rcx
  491ad5:	48 83 e3 07          	and    $0x7,%rbx
  491ad9:	f3 48 ab             	rep stos %rax,%es:(%rdi)
  491adc:	e9 65 fe ff ff       	jmp    491946 <runtime.memclrNoHeapPointers+0x6>
  491ae1:	c5 fe 7f 07          	vmovdqu %ymm0,(%rdi)
  491ae5:	48 89 fe             	mov    %rdi,%rsi
  491ae8:	48 83 c7 20          	add    $0x20,%rdi
  491aec:	48 83 e7 e0          	and    $0xffffffffffffffe0,%rdi
  491af0:	48 29 fe             	sub    %rdi,%rsi
  491af3:	48 01 f3             	add    %rsi,%rbx
  491af6:	c5 fd e7 07          	vmovntdq %ymm0,(%rdi)
  491afa:	c5 fd e7 47 20       	vmovntdq %ymm0,0x20(%rdi)
  491aff:	c5 fd e7 47 40       	vmovntdq %ymm0,0x40(%rdi)
  491b04:	c5 fd e7 47 60       	vmovntdq %ymm0,0x60(%rdi)
  491b09:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  491b10:	48 81 c7 80 00 00 00 	add    $0x80,%rdi
  491b17:	48 81 fb 80 00 00 00 	cmp    $0x80,%rbx
  491b1e:	73 d6                	jae    491af6 <runtime.memclrNoHeapPointers+0x1b6>
  491b20:	0f ae f8             	sfence
  491b23:	c5 fe 7f 44 1f e0    	vmovdqu %ymm0,-0x20(%rdi,%rbx,1)
  491b29:	c5 fe 7f 44 1f c0    	vmovdqu %ymm0,-0x40(%rdi,%rbx,1)
  491b2f:	c5 fe 7f 44 1f a0    	vmovdqu %ymm0,-0x60(%rdi,%rbx,1)
  491b35:	c5 fe 7f 44 1f 80    	vmovdqu %ymm0,-0x80(%rdi,%rbx,1)
  491b3b:	c5 f8 77             	vzeroupper
  491b3e:	c3                   	ret
  491b3f:	88 07                	mov    %al,(%rdi)
  491b41:	88 44 1f ff          	mov    %al,-0x1(%rdi,%rbx,1)
  491b45:	c3                   	ret
  491b46:	c3                   	ret
  491b47:	66 89 07             	mov    %ax,(%rdi)
  491b4a:	66 89 44 1f fe       	mov    %ax,-0x2(%rdi,%rbx,1)
  491b4f:	c3                   	ret
  491b50:	89 07                	mov    %eax,(%rdi)
  491b52:	89 44 1f fc          	mov    %eax,-0x4(%rdi,%rbx,1)
  491b56:	c3                   	ret
  491b57:	48 89 07             	mov    %rax,(%rdi)
  491b5a:	c3                   	ret
  491b5b:	48 89 07             	mov    %rax,(%rdi)
  491b5e:	48 89 44 1f f8       	mov    %rax,-0x8(%rdi,%rbx,1)
  491b63:	c3                   	ret
  491b64:	f3 44 0f 7f 3f       	movdqu %xmm15,(%rdi)
  491b69:	f3 44 0f 7f 7c 1f f0 	movdqu %xmm15,-0x10(%rdi,%rbx,1)
  491b70:	c3                   	ret
  491b71:	f3 44 0f 7f 3f       	movdqu %xmm15,(%rdi)
  491b76:	f3 44 0f 7f 7f 10    	movdqu %xmm15,0x10(%rdi)
  491b7c:	f3 44 0f 7f 7c 1f e0 	movdqu %xmm15,-0x20(%rdi,%rbx,1)
  491b83:	f3 44 0f 7f 7c 1f f0 	movdqu %xmm15,-0x10(%rdi,%rbx,1)
  491b8a:	c3                   	ret
  491b8b:	f3 44 0f 7f 3f       	movdqu %xmm15,(%rdi)
  491b90:	f3 44 0f 7f 7f 10    	movdqu %xmm15,0x10(%rdi)
  491b96:	f3 44 0f 7f 7f 20    	movdqu %xmm15,0x20(%rdi)
  491b9c:	f3 44 0f 7f 7f 30    	movdqu %xmm15,0x30(%rdi)
  491ba2:	f3 44 0f 7f 7c 1f c0 	movdqu %xmm15,-0x40(%rdi,%rbx,1)
  491ba9:	f3 44 0f 7f 7c 1f d0 	movdqu %xmm15,-0x30(%rdi,%rbx,1)
  491bb0:	f3 44 0f 7f 7c 1f e0 	movdqu %xmm15,-0x20(%rdi,%rbx,1)
  491bb7:	f3 44 0f 7f 7c 1f f0 	movdqu %xmm15,-0x10(%rdi,%rbx,1)
  491bbe:	c3                   	ret
  491bbf:	f3 44 0f 7f 3f       	movdqu %xmm15,(%rdi)
  491bc4:	f3 44 0f 7f 7f 10    	movdqu %xmm15,0x10(%rdi)
  491bca:	f3 44 0f 7f 7f 20    	movdqu %xmm15,0x20(%rdi)
  491bd0:	f3 44 0f 7f 7f 30    	movdqu %xmm15,0x30(%rdi)
  491bd6:	f3 44 0f 7f 7f 40    	movdqu %xmm15,0x40(%rdi)
  491bdc:	f3 44 0f 7f 7f 50    	movdqu %xmm15,0x50(%rdi)
  491be2:	f3 44 0f 7f 7f 60    	movdqu %xmm15,0x60(%rdi)
  491be8:	f3 44 0f 7f 7f 70    	movdqu %xmm15,0x70(%rdi)
  491bee:	f3 44 0f 7f 7c 1f 80 	movdqu %xmm15,-0x80(%rdi,%rbx,1)
  491bf5:	f3 44 0f 7f 7c 1f 90 	movdqu %xmm15,-0x70(%rdi,%rbx,1)
  491bfc:	f3 44 0f 7f 7c 1f a0 	movdqu %xmm15,-0x60(%rdi,%rbx,1)
  491c03:	f3 44 0f 7f 7c 1f b0 	movdqu %xmm15,-0x50(%rdi,%rbx,1)
  491c0a:	f3 44 0f 7f 7c 1f c0 	movdqu %xmm15,-0x40(%rdi,%rbx,1)
  491c11:	f3 44 0f 7f 7c 1f d0 	movdqu %xmm15,-0x30(%rdi,%rbx,1)
  491c18:	f3 44 0f 7f 7c 1f e0 	movdqu %xmm15,-0x20(%rdi,%rbx,1)
  491c1f:	f3 44 0f 7f 7c 1f f0 	movdqu %xmm15,-0x10(%rdi,%rbx,1)
  491c26:	c3                   	ret

Disassembly of section .plt:
