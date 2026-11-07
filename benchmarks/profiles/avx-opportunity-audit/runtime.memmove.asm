
/home/dev/tssss/tsc-tsgo/packages/tsc-go/dist/tsc-go:     file format elf64-x86-64


Disassembly of section .text:

0000000000491c40 <runtime.memmove>:
  491c40:	48 89 c7             	mov    %rax,%rdi
  491c43:	48 89 de             	mov    %rbx,%rsi
  491c46:	48 89 cb             	mov    %rcx,%rbx
  491c49:	48 85 db             	test   %rbx,%rbx
  491c4c:	0f 84 1b 01 00 00    	je     491d6d <runtime.memmove+0x12d>
  491c52:	48 83 fb 02          	cmp    $0x2,%rbx
  491c56:	0f 86 04 01 00 00    	jbe    491d60 <runtime.memmove+0x120>
  491c5c:	48 83 fb 04          	cmp    $0x4,%rbx
  491c60:	0f 82 0d 01 00 00    	jb     491d73 <runtime.memmove+0x133>
  491c66:	0f 86 02 01 00 00    	jbe    491d6e <runtime.memmove+0x12e>
  491c6c:	48 83 fb 08          	cmp    $0x8,%rbx
  491c70:	0f 82 0a 01 00 00    	jb     491d80 <runtime.memmove+0x140>
  491c76:	0f 84 11 01 00 00    	je     491d8d <runtime.memmove+0x14d>
  491c7c:	48 83 fb 10          	cmp    $0x10,%rbx
  491c80:	0f 86 0e 01 00 00    	jbe    491d94 <runtime.memmove+0x154>
  491c86:	48 83 fb 20          	cmp    $0x20,%rbx
  491c8a:	0f 86 15 01 00 00    	jbe    491da5 <runtime.memmove+0x165>
  491c90:	48 83 fb 40          	cmp    $0x40,%rbx
  491c94:	0f 86 20 01 00 00    	jbe    491dba <runtime.memmove+0x17a>
  491c9a:	48 81 fb 80 00 00 00 	cmp    $0x80,%rbx
  491ca1:	0f 86 3e 01 00 00    	jbe    491de5 <runtime.memmove+0x1a5>
  491ca7:	48 81 fb 00 01 00 00 	cmp    $0x100,%rbx
  491cae:	0f 86 88 01 00 00    	jbe    491e3c <runtime.memmove+0x1fc>
  491cb4:	8a 05 9a 86 d9 01    	mov    0x1d9869a(%rip),%al        # 222a354 <runtime.memmoveBits>
  491cba:	3c 01                	cmp    $0x1,%al
  491cbc:	0f 84 48 03 00 00    	je     49200a <runtime.memmove+0x3ca>
  491cc2:	48 39 fe             	cmp    %rdi,%rsi
  491cc5:	76 55                	jbe    491d1c <runtime.memmove+0xdc>
  491cc7:	48 81 fb 00 08 00 00 	cmp    $0x800,%rbx
  491cce:	7c 0d                	jl     491cdd <runtime.memmove+0x9d>
  491cd0:	48 f7 c7 0f 00 00 00 	test   $0xf,%rdi
  491cd7:	75 04                	jne    491cdd <runtime.memmove+0x9d>
  491cd9:	a8 02                	test   $0x2,%al
  491cdb:	75 26                	jne    491d03 <runtime.memmove+0xc3>
  491cdd:	a8 01                	test   $0x1,%al
  491cdf:	0f 85 25 03 00 00    	jne    49200a <runtime.memmove+0x3ca>
  491ce5:	48 81 fb 00 08 00 00 	cmp    $0x800,%rbx
  491cec:	0f 86 0e 02 00 00    	jbe    491f00 <runtime.memmove+0x2c0>
  491cf2:	89 f0                	mov    %esi,%eax
  491cf4:	09 f8                	or     %edi,%eax
  491cf6:	a9 07 00 00 00       	test   $0x7,%eax
  491cfb:	74 06                	je     491d03 <runtime.memmove+0xc3>
  491cfd:	48 89 d9             	mov    %rbx,%rcx
  491d00:	f3 a4                	rep movsb %ds:(%rsi),%es:(%rdi)
  491d02:	c3                   	ret
  491d03:	48 8b 44 1e f8       	mov    -0x8(%rsi,%rbx,1),%rax
  491d08:	48 8d 54 1f f8       	lea    -0x8(%rdi,%rbx,1),%rdx
  491d0d:	48 8d 4b ff          	lea    -0x1(%rbx),%rcx
  491d11:	48 c1 e9 03          	shr    $0x3,%rcx
  491d15:	f3 48 a5             	rep movsq %ds:(%rsi),%es:(%rdi)
  491d18:	48 89 02             	mov    %rax,(%rdx)
  491d1b:	c3                   	ret
  491d1c:	48 89 f1             	mov    %rsi,%rcx
  491d1f:	48 01 d9             	add    %rbx,%rcx
  491d22:	48 39 f9             	cmp    %rdi,%rcx
  491d25:	76 a0                	jbe    491cc7 <runtime.memmove+0x87>
  491d27:	a8 01                	test   $0x1,%al
  491d29:	0f 85 db 02 00 00    	jne    49200a <runtime.memmove+0x3ca>
  491d2f:	48 01 df             	add    %rbx,%rdi
  491d32:	48 01 de             	add    %rbx,%rsi
  491d35:	fd                   	std
  491d36:	48 89 d9             	mov    %rbx,%rcx
  491d39:	48 c1 e9 03          	shr    $0x3,%rcx
  491d3d:	48 83 e3 07          	and    $0x7,%rbx
  491d41:	48 83 ef 08          	sub    $0x8,%rdi
  491d45:	48 83 ee 08          	sub    $0x8,%rsi
  491d49:	f3 48 a5             	rep movsq %ds:(%rsi),%es:(%rdi)
  491d4c:	fc                   	cld
  491d4d:	48 83 c7 08          	add    $0x8,%rdi
  491d51:	48 83 c6 08          	add    $0x8,%rsi
  491d55:	48 29 df             	sub    %rbx,%rdi
  491d58:	48 29 de             	sub    %rbx,%rsi
  491d5b:	e9 e9 fe ff ff       	jmp    491c49 <runtime.memmove+0x9>
  491d60:	8a 06                	mov    (%rsi),%al
  491d62:	8a 4c 1e ff          	mov    -0x1(%rsi,%rbx,1),%cl
  491d66:	88 07                	mov    %al,(%rdi)
  491d68:	88 4c 1f ff          	mov    %cl,-0x1(%rdi,%rbx,1)
  491d6c:	c3                   	ret
  491d6d:	c3                   	ret
  491d6e:	8b 06                	mov    (%rsi),%eax
  491d70:	89 07                	mov    %eax,(%rdi)
  491d72:	c3                   	ret
  491d73:	66 8b 06             	mov    (%rsi),%ax
  491d76:	8a 4e 02             	mov    0x2(%rsi),%cl
  491d79:	66 89 07             	mov    %ax,(%rdi)
  491d7c:	88 4f 02             	mov    %cl,0x2(%rdi)
  491d7f:	c3                   	ret
  491d80:	8b 06                	mov    (%rsi),%eax
  491d82:	8b 4c 1e fc          	mov    -0x4(%rsi,%rbx,1),%ecx
  491d86:	89 07                	mov    %eax,(%rdi)
  491d88:	89 4c 1f fc          	mov    %ecx,-0x4(%rdi,%rbx,1)
  491d8c:	c3                   	ret
  491d8d:	48 8b 06             	mov    (%rsi),%rax
  491d90:	48 89 07             	mov    %rax,(%rdi)
  491d93:	c3                   	ret
  491d94:	48 8b 06             	mov    (%rsi),%rax
  491d97:	48 8b 4c 1e f8       	mov    -0x8(%rsi,%rbx,1),%rcx
  491d9c:	48 89 07             	mov    %rax,(%rdi)
  491d9f:	48 89 4c 1f f8       	mov    %rcx,-0x8(%rdi,%rbx,1)
  491da4:	c3                   	ret
  491da5:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  491da9:	f3 0f 6f 4c 1e f0    	movdqu -0x10(%rsi,%rbx,1),%xmm1
  491daf:	f3 0f 7f 07          	movdqu %xmm0,(%rdi)
  491db3:	f3 0f 7f 4c 1f f0    	movdqu %xmm1,-0x10(%rdi,%rbx,1)
  491db9:	c3                   	ret
  491dba:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  491dbe:	f3 0f 6f 4e 10       	movdqu 0x10(%rsi),%xmm1
  491dc3:	f3 0f 6f 54 1e e0    	movdqu -0x20(%rsi,%rbx,1),%xmm2
  491dc9:	f3 0f 6f 5c 1e f0    	movdqu -0x10(%rsi,%rbx,1),%xmm3
  491dcf:	f3 0f 7f 07          	movdqu %xmm0,(%rdi)
  491dd3:	f3 0f 7f 4f 10       	movdqu %xmm1,0x10(%rdi)
  491dd8:	f3 0f 7f 54 1f e0    	movdqu %xmm2,-0x20(%rdi,%rbx,1)
  491dde:	f3 0f 7f 5c 1f f0    	movdqu %xmm3,-0x10(%rdi,%rbx,1)
  491de4:	c3                   	ret
  491de5:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  491de9:	f3 0f 6f 4e 10       	movdqu 0x10(%rsi),%xmm1
  491dee:	f3 0f 6f 56 20       	movdqu 0x20(%rsi),%xmm2
  491df3:	f3 0f 6f 5e 30       	movdqu 0x30(%rsi),%xmm3
  491df8:	f3 0f 6f 64 1e c0    	movdqu -0x40(%rsi,%rbx,1),%xmm4
  491dfe:	f3 0f 6f 6c 1e d0    	movdqu -0x30(%rsi,%rbx,1),%xmm5
  491e04:	f3 0f 6f 74 1e e0    	movdqu -0x20(%rsi,%rbx,1),%xmm6
  491e0a:	f3 0f 6f 7c 1e f0    	movdqu -0x10(%rsi,%rbx,1),%xmm7
  491e10:	f3 0f 7f 07          	movdqu %xmm0,(%rdi)
  491e14:	f3 0f 7f 4f 10       	movdqu %xmm1,0x10(%rdi)
  491e19:	f3 0f 7f 57 20       	movdqu %xmm2,0x20(%rdi)
  491e1e:	f3 0f 7f 5f 30       	movdqu %xmm3,0x30(%rdi)
  491e23:	f3 0f 7f 64 1f c0    	movdqu %xmm4,-0x40(%rdi,%rbx,1)
  491e29:	f3 0f 7f 6c 1f d0    	movdqu %xmm5,-0x30(%rdi,%rbx,1)
  491e2f:	f3 0f 7f 74 1f e0    	movdqu %xmm6,-0x20(%rdi,%rbx,1)
  491e35:	f3 0f 7f 7c 1f f0    	movdqu %xmm7,-0x10(%rdi,%rbx,1)
  491e3b:	c3                   	ret
  491e3c:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  491e40:	f3 0f 6f 4e 10       	movdqu 0x10(%rsi),%xmm1
  491e45:	f3 0f 6f 56 20       	movdqu 0x20(%rsi),%xmm2
  491e4a:	f3 0f 6f 5e 30       	movdqu 0x30(%rsi),%xmm3
  491e4f:	f3 0f 6f 66 40       	movdqu 0x40(%rsi),%xmm4
  491e54:	f3 0f 6f 6e 50       	movdqu 0x50(%rsi),%xmm5
  491e59:	f3 0f 6f 76 60       	movdqu 0x60(%rsi),%xmm6
  491e5e:	f3 0f 6f 7e 70       	movdqu 0x70(%rsi),%xmm7
  491e63:	f3 44 0f 6f 44 1e 80 	movdqu -0x80(%rsi,%rbx,1),%xmm8
  491e6a:	f3 44 0f 6f 4c 1e 90 	movdqu -0x70(%rsi,%rbx,1),%xmm9
  491e71:	f3 44 0f 6f 54 1e a0 	movdqu -0x60(%rsi,%rbx,1),%xmm10
  491e78:	f3 44 0f 6f 5c 1e b0 	movdqu -0x50(%rsi,%rbx,1),%xmm11
  491e7f:	f3 44 0f 6f 64 1e c0 	movdqu -0x40(%rsi,%rbx,1),%xmm12
  491e86:	f3 44 0f 6f 6c 1e d0 	movdqu -0x30(%rsi,%rbx,1),%xmm13
  491e8d:	f3 44 0f 6f 74 1e e0 	movdqu -0x20(%rsi,%rbx,1),%xmm14
  491e94:	f3 44 0f 6f 7c 1e f0 	movdqu -0x10(%rsi,%rbx,1),%xmm15
  491e9b:	f3 0f 7f 07          	movdqu %xmm0,(%rdi)
  491e9f:	f3 0f 7f 4f 10       	movdqu %xmm1,0x10(%rdi)
  491ea4:	f3 0f 7f 57 20       	movdqu %xmm2,0x20(%rdi)
  491ea9:	f3 0f 7f 5f 30       	movdqu %xmm3,0x30(%rdi)
  491eae:	f3 0f 7f 67 40       	movdqu %xmm4,0x40(%rdi)
  491eb3:	f3 0f 7f 6f 50       	movdqu %xmm5,0x50(%rdi)
  491eb8:	f3 0f 7f 77 60       	movdqu %xmm6,0x60(%rdi)
  491ebd:	f3 0f 7f 7f 70       	movdqu %xmm7,0x70(%rdi)
  491ec2:	f3 44 0f 7f 44 1f 80 	movdqu %xmm8,-0x80(%rdi,%rbx,1)
  491ec9:	f3 44 0f 7f 4c 1f 90 	movdqu %xmm9,-0x70(%rdi,%rbx,1)
  491ed0:	f3 44 0f 7f 54 1f a0 	movdqu %xmm10,-0x60(%rdi,%rbx,1)
  491ed7:	f3 44 0f 7f 5c 1f b0 	movdqu %xmm11,-0x50(%rdi,%rbx,1)
  491ede:	f3 44 0f 7f 64 1f c0 	movdqu %xmm12,-0x40(%rdi,%rbx,1)
  491ee5:	f3 44 0f 7f 6c 1f d0 	movdqu %xmm13,-0x30(%rdi,%rbx,1)
  491eec:	f3 44 0f 7f 74 1f e0 	movdqu %xmm14,-0x20(%rdi,%rbx,1)
  491ef3:	f3 44 0f 7f 7c 1f f0 	movdqu %xmm15,-0x10(%rdi,%rbx,1)
  491efa:	66 45 0f ef ff       	pxor   %xmm15,%xmm15
  491eff:	c3                   	ret
  491f00:	48 81 eb 00 01 00 00 	sub    $0x100,%rbx
  491f07:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  491f0b:	f3 0f 6f 4e 10       	movdqu 0x10(%rsi),%xmm1
  491f10:	f3 0f 6f 56 20       	movdqu 0x20(%rsi),%xmm2
  491f15:	f3 0f 6f 5e 30       	movdqu 0x30(%rsi),%xmm3
  491f1a:	f3 0f 6f 66 40       	movdqu 0x40(%rsi),%xmm4
  491f1f:	f3 0f 6f 6e 50       	movdqu 0x50(%rsi),%xmm5
  491f24:	f3 0f 6f 76 60       	movdqu 0x60(%rsi),%xmm6
  491f29:	f3 0f 6f 7e 70       	movdqu 0x70(%rsi),%xmm7
  491f2e:	f3 44 0f 6f 86 80 00 	movdqu 0x80(%rsi),%xmm8
  491f35:	00 00 
  491f37:	f3 44 0f 6f 8e 90 00 	movdqu 0x90(%rsi),%xmm9
  491f3e:	00 00 
  491f40:	f3 44 0f 6f 96 a0 00 	movdqu 0xa0(%rsi),%xmm10
  491f47:	00 00 
  491f49:	f3 44 0f 6f 9e b0 00 	movdqu 0xb0(%rsi),%xmm11
  491f50:	00 00 
  491f52:	f3 44 0f 6f a6 c0 00 	movdqu 0xc0(%rsi),%xmm12
  491f59:	00 00 
  491f5b:	f3 44 0f 6f ae d0 00 	movdqu 0xd0(%rsi),%xmm13
  491f62:	00 00 
  491f64:	f3 44 0f 6f b6 e0 00 	movdqu 0xe0(%rsi),%xmm14
  491f6b:	00 00 
  491f6d:	f3 44 0f 6f be f0 00 	movdqu 0xf0(%rsi),%xmm15
  491f74:	00 00 
  491f76:	f3 0f 7f 07          	movdqu %xmm0,(%rdi)
  491f7a:	f3 0f 7f 4f 10       	movdqu %xmm1,0x10(%rdi)
  491f7f:	f3 0f 7f 57 20       	movdqu %xmm2,0x20(%rdi)
  491f84:	f3 0f 7f 5f 30       	movdqu %xmm3,0x30(%rdi)
  491f89:	f3 0f 7f 67 40       	movdqu %xmm4,0x40(%rdi)
  491f8e:	f3 0f 7f 6f 50       	movdqu %xmm5,0x50(%rdi)
  491f93:	f3 0f 7f 77 60       	movdqu %xmm6,0x60(%rdi)
  491f98:	f3 0f 7f 7f 70       	movdqu %xmm7,0x70(%rdi)
  491f9d:	f3 44 0f 7f 87 80 00 	movdqu %xmm8,0x80(%rdi)
  491fa4:	00 00 
  491fa6:	f3 44 0f 7f 8f 90 00 	movdqu %xmm9,0x90(%rdi)
  491fad:	00 00 
  491faf:	f3 44 0f 7f 97 a0 00 	movdqu %xmm10,0xa0(%rdi)
  491fb6:	00 00 
  491fb8:	f3 44 0f 7f 9f b0 00 	movdqu %xmm11,0xb0(%rdi)
  491fbf:	00 00 
  491fc1:	f3 44 0f 7f a7 c0 00 	movdqu %xmm12,0xc0(%rdi)
  491fc8:	00 00 
  491fca:	f3 44 0f 7f af d0 00 	movdqu %xmm13,0xd0(%rdi)
  491fd1:	00 00 
  491fd3:	f3 44 0f 7f b7 e0 00 	movdqu %xmm14,0xe0(%rdi)
  491fda:	00 00 
  491fdc:	f3 44 0f 7f bf f0 00 	movdqu %xmm15,0xf0(%rdi)
  491fe3:	00 00 
  491fe5:	48 81 fb 00 01 00 00 	cmp    $0x100,%rbx
  491fec:	48 8d b6 00 01 00 00 	lea    0x100(%rsi),%rsi
  491ff3:	48 8d bf 00 01 00 00 	lea    0x100(%rdi),%rdi
  491ffa:	0f 8d 00 ff ff ff    	jge    491f00 <runtime.memmove+0x2c0>
  492000:	66 45 0f ef ff       	pxor   %xmm15,%xmm15
  492005:	e9 3f fc ff ff       	jmp    491c49 <runtime.memmove+0x9>
  49200a:	48 89 f9             	mov    %rdi,%rcx
  49200d:	48 29 f1             	sub    %rsi,%rcx
  492010:	48 39 d9             	cmp    %rbx,%rcx
  492013:	0f 82 ac 01 00 00    	jb     4921c5 <runtime.memmove+0x585>
  492019:	48 81 fb 00 00 10 00 	cmp    $0x100000,%rbx
  492020:	0f 83 c3 00 00 00    	jae    4920e9 <runtime.memmove+0x4a9>
  492026:	48 8d 0c 1e          	lea    (%rsi,%rbx,1),%rcx
  49202a:	49 89 fa             	mov    %rdi,%r10
  49202d:	f3 0f 6f 69 80       	movdqu -0x80(%rcx),%xmm5
  492032:	f3 0f 6f 71 90       	movdqu -0x70(%rcx),%xmm6
  492037:	48 c7 c0 80 00 00 00 	mov    $0x80,%rax
  49203e:	48 83 e7 e0          	and    $0xffffffffffffffe0,%rdi
  492042:	48 83 c7 20          	add    $0x20,%rdi
  492046:	f3 0f 6f 79 a0       	movdqu -0x60(%rcx),%xmm7
  49204b:	f3 44 0f 6f 41 b0    	movdqu -0x50(%rcx),%xmm8
  492051:	49 89 fb             	mov    %rdi,%r11
  492054:	4d 29 d3             	sub    %r10,%r11
  492057:	f3 44 0f 6f 49 c0    	movdqu -0x40(%rcx),%xmm9
  49205d:	f3 44 0f 6f 51 d0    	movdqu -0x30(%rcx),%xmm10
  492063:	4c 29 db             	sub    %r11,%rbx
  492066:	f3 44 0f 6f 59 e0    	movdqu -0x20(%rcx),%xmm11
  49206c:	f3 44 0f 6f 61 f0    	movdqu -0x10(%rcx),%xmm12
  492072:	c5 fe 6f 26          	vmovdqu (%rsi),%ymm4
  492076:	4c 01 de             	add    %r11,%rsi
  492079:	48 29 c3             	sub    %rax,%rbx
  49207c:	c5 fe 6f 06          	vmovdqu (%rsi),%ymm0
  492080:	c5 fe 6f 4e 20       	vmovdqu 0x20(%rsi),%ymm1
  492085:	c5 fe 6f 56 40       	vmovdqu 0x40(%rsi),%ymm2
  49208a:	c5 fe 6f 5e 60       	vmovdqu 0x60(%rsi),%ymm3
  49208f:	48 01 c6             	add    %rax,%rsi
  492092:	c5 fd 7f 07          	vmovdqa %ymm0,(%rdi)
  492096:	c5 fd 7f 4f 20       	vmovdqa %ymm1,0x20(%rdi)
  49209b:	c5 fd 7f 57 40       	vmovdqa %ymm2,0x40(%rdi)
  4920a0:	c5 fd 7f 5f 60       	vmovdqa %ymm3,0x60(%rdi)
  4920a5:	48 01 c7             	add    %rax,%rdi
  4920a8:	48 29 c3             	sub    %rax,%rbx
  4920ab:	77 cf                	ja     49207c <runtime.memmove+0x43c>
  4920ad:	48 01 c3             	add    %rax,%rbx
  4920b0:	48 01 fb             	add    %rdi,%rbx
  4920b3:	c4 c1 7e 7f 22       	vmovdqu %ymm4,(%r10)
  4920b8:	c5 f8 77             	vzeroupper
  4920bb:	f3 0f 7f 6b 80       	movdqu %xmm5,-0x80(%rbx)
  4920c0:	f3 0f 7f 73 90       	movdqu %xmm6,-0x70(%rbx)
  4920c5:	f3 0f 7f 7b a0       	movdqu %xmm7,-0x60(%rbx)
  4920ca:	f3 44 0f 7f 43 b0    	movdqu %xmm8,-0x50(%rbx)
  4920d0:	f3 44 0f 7f 4b c0    	movdqu %xmm9,-0x40(%rbx)
  4920d6:	f3 44 0f 7f 53 d0    	movdqu %xmm10,-0x30(%rbx)
  4920dc:	f3 44 0f 7f 5b e0    	movdqu %xmm11,-0x20(%rbx)
  4920e2:	f3 44 0f 7f 63 f0    	movdqu %xmm12,-0x10(%rbx)
  4920e8:	c3                   	ret
  4920e9:	48 8d 0c 1e          	lea    (%rsi,%rbx,1),%rcx
  4920ed:	f3 0f 6f 6c 1e 80    	movdqu -0x80(%rsi,%rbx,1),%xmm5
  4920f3:	f3 0f 6f 71 90       	movdqu -0x70(%rcx),%xmm6
  4920f8:	f3 0f 6f 79 a0       	movdqu -0x60(%rcx),%xmm7
  4920fd:	f3 44 0f 6f 41 b0    	movdqu -0x50(%rcx),%xmm8
  492103:	f3 44 0f 6f 49 c0    	movdqu -0x40(%rcx),%xmm9
  492109:	f3 44 0f 6f 51 d0    	movdqu -0x30(%rcx),%xmm10
  49210f:	f3 44 0f 6f 59 e0    	movdqu -0x20(%rcx),%xmm11
  492115:	f3 44 0f 6f 61 f0    	movdqu -0x10(%rcx),%xmm12
  49211b:	c5 fe 6f 26          	vmovdqu (%rsi),%ymm4
  49211f:	49 89 f8             	mov    %rdi,%r8
  492122:	48 83 e7 e0          	and    $0xffffffffffffffe0,%rdi
  492126:	48 83 c7 20          	add    $0x20,%rdi
  49212a:	49 89 fa             	mov    %rdi,%r10
  49212d:	4d 29 c2             	sub    %r8,%r10
  492130:	4c 29 d3             	sub    %r10,%rbx
  492133:	4c 01 d6             	add    %r10,%rsi
  492136:	48 8d 0c 1f          	lea    (%rdi,%rbx,1),%rcx
  49213a:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  492141:	0f 18 86 c0 01 00 00 	prefetchnta 0x1c0(%rsi)
  492148:	0f 18 86 80 02 00 00 	prefetchnta 0x280(%rsi)
  49214f:	c5 fe 6f 06          	vmovdqu (%rsi),%ymm0
  492153:	c5 fe 6f 4e 20       	vmovdqu 0x20(%rsi),%ymm1
  492158:	c5 fe 6f 56 40       	vmovdqu 0x40(%rsi),%ymm2
  49215d:	c5 fe 6f 5e 60       	vmovdqu 0x60(%rsi),%ymm3
  492162:	48 81 c6 80 00 00 00 	add    $0x80,%rsi
  492169:	c5 fd e7 07          	vmovntdq %ymm0,(%rdi)
  49216d:	c5 fd e7 4f 20       	vmovntdq %ymm1,0x20(%rdi)
  492172:	c5 fd e7 57 40       	vmovntdq %ymm2,0x40(%rdi)
  492177:	c5 fd e7 5f 60       	vmovntdq %ymm3,0x60(%rdi)
  49217c:	48 81 c7 80 00 00 00 	add    $0x80,%rdi
  492183:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  49218a:	77 b5                	ja     492141 <runtime.memmove+0x501>
  49218c:	0f ae f8             	sfence
  49218f:	c4 c1 7e 7f 20       	vmovdqu %ymm4,(%r8)
  492194:	c5 f8 77             	vzeroupper
  492197:	f3 0f 7f 69 80       	movdqu %xmm5,-0x80(%rcx)
  49219c:	f3 0f 7f 71 90       	movdqu %xmm6,-0x70(%rcx)
  4921a1:	f3 0f 7f 79 a0       	movdqu %xmm7,-0x60(%rcx)
  4921a6:	f3 44 0f 7f 41 b0    	movdqu %xmm8,-0x50(%rcx)
  4921ac:	f3 44 0f 7f 49 c0    	movdqu %xmm9,-0x40(%rcx)
  4921b2:	f3 44 0f 7f 51 d0    	movdqu %xmm10,-0x30(%rcx)
  4921b8:	f3 44 0f 7f 59 e0    	movdqu %xmm11,-0x20(%rcx)
  4921be:	f3 44 0f 7f 61 f0    	movdqu %xmm12,-0x10(%rcx)
  4921c4:	c3                   	ret
  4921c5:	48 89 f8             	mov    %rdi,%rax
  4921c8:	f3 0f 6f 2e          	movdqu (%rsi),%xmm5
  4921cc:	f3 0f 6f 76 10       	movdqu 0x10(%rsi),%xmm6
  4921d1:	48 01 df             	add    %rbx,%rdi
  4921d4:	f3 0f 6f 7e 20       	movdqu 0x20(%rsi),%xmm7
  4921d9:	f3 44 0f 6f 46 30    	movdqu 0x30(%rsi),%xmm8
  4921df:	4c 8d 57 e0          	lea    -0x20(%rdi),%r10
  4921e3:	49 89 fb             	mov    %rdi,%r11
  4921e6:	f3 44 0f 6f 4e 40    	movdqu 0x40(%rsi),%xmm9
  4921ec:	f3 44 0f 6f 56 50    	movdqu 0x50(%rsi),%xmm10
  4921f2:	49 83 e3 1f          	and    $0x1f,%r11
  4921f6:	f3 44 0f 6f 5e 60    	movdqu 0x60(%rsi),%xmm11
  4921fc:	f3 44 0f 6f 66 70    	movdqu 0x70(%rsi),%xmm12
  492202:	4c 31 df             	xor    %r11,%rdi
  492205:	48 01 de             	add    %rbx,%rsi
  492208:	c5 fe 6f 66 e0       	vmovdqu -0x20(%rsi),%ymm4
  49220d:	4c 29 de             	sub    %r11,%rsi
  492210:	4c 29 db             	sub    %r11,%rbx
  492213:	48 81 fb 00 00 10 00 	cmp    $0x100000,%rbx
  49221a:	77 7b                	ja     492297 <runtime.memmove+0x657>
  49221c:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  492223:	c5 fe 6f 46 e0       	vmovdqu -0x20(%rsi),%ymm0
  492228:	c5 fe 6f 4e c0       	vmovdqu -0x40(%rsi),%ymm1
  49222d:	c5 fe 6f 56 a0       	vmovdqu -0x60(%rsi),%ymm2
  492232:	c5 fe 6f 5e 80       	vmovdqu -0x80(%rsi),%ymm3
  492237:	48 81 ee 80 00 00 00 	sub    $0x80,%rsi
  49223e:	c5 fd 7f 47 e0       	vmovdqa %ymm0,-0x20(%rdi)
  492243:	c5 fd 7f 4f c0       	vmovdqa %ymm1,-0x40(%rdi)
  492248:	c5 fd 7f 57 a0       	vmovdqa %ymm2,-0x60(%rdi)
  49224d:	c5 fd 7f 5f 80       	vmovdqa %ymm3,-0x80(%rdi)
  492252:	48 81 ef 80 00 00 00 	sub    $0x80,%rdi
  492259:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  492260:	77 c1                	ja     492223 <runtime.memmove+0x5e3>
  492262:	c4 c1 7e 7f 22       	vmovdqu %ymm4,(%r10)
  492267:	c5 f8 77             	vzeroupper
  49226a:	f3 0f 7f 28          	movdqu %xmm5,(%rax)
  49226e:	f3 0f 7f 70 10       	movdqu %xmm6,0x10(%rax)
  492273:	f3 0f 7f 78 20       	movdqu %xmm7,0x20(%rax)
  492278:	f3 44 0f 7f 40 30    	movdqu %xmm8,0x30(%rax)
  49227e:	f3 44 0f 7f 48 40    	movdqu %xmm9,0x40(%rax)
  492284:	f3 44 0f 7f 50 50    	movdqu %xmm10,0x50(%rax)
  49228a:	f3 44 0f 7f 58 60    	movdqu %xmm11,0x60(%rax)
  492290:	f3 44 0f 7f 60 70    	movdqu %xmm12,0x70(%rax)
  492296:	c3                   	ret
  492297:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  49229e:	0f 18 86 40 fe ff ff 	prefetchnta -0x1c0(%rsi)
  4922a5:	0f 18 86 80 fd ff ff 	prefetchnta -0x280(%rsi)
  4922ac:	c5 fe 6f 46 e0       	vmovdqu -0x20(%rsi),%ymm0
  4922b1:	c5 fe 6f 4e c0       	vmovdqu -0x40(%rsi),%ymm1
  4922b6:	c5 fe 6f 56 a0       	vmovdqu -0x60(%rsi),%ymm2
  4922bb:	c5 fe 6f 5e 80       	vmovdqu -0x80(%rsi),%ymm3
  4922c0:	48 81 ee 80 00 00 00 	sub    $0x80,%rsi
  4922c7:	c5 fd e7 47 e0       	vmovntdq %ymm0,-0x20(%rdi)
  4922cc:	c5 fd e7 4f c0       	vmovntdq %ymm1,-0x40(%rdi)
  4922d1:	c5 fd e7 57 a0       	vmovntdq %ymm2,-0x60(%rdi)
  4922d6:	c5 fd e7 5f 80       	vmovntdq %ymm3,-0x80(%rdi)
  4922db:	48 81 ef 80 00 00 00 	sub    $0x80,%rdi
  4922e2:	48 81 eb 80 00 00 00 	sub    $0x80,%rbx
  4922e9:	77 b3                	ja     49229e <runtime.memmove+0x65e>
  4922eb:	0f ae f8             	sfence
  4922ee:	c4 c1 7e 7f 22       	vmovdqu %ymm4,(%r10)
  4922f3:	c5 f8 77             	vzeroupper
  4922f6:	f3 0f 7f 28          	movdqu %xmm5,(%rax)
  4922fa:	f3 0f 7f 70 10       	movdqu %xmm6,0x10(%rax)
  4922ff:	f3 0f 7f 78 20       	movdqu %xmm7,0x20(%rax)
  492304:	f3 44 0f 7f 40 30    	movdqu %xmm8,0x30(%rax)
  49230a:	f3 44 0f 7f 48 40    	movdqu %xmm9,0x40(%rax)
  492310:	f3 44 0f 7f 50 50    	movdqu %xmm10,0x50(%rax)
  492316:	f3 44 0f 7f 58 60    	movdqu %xmm11,0x60(%rax)
  49231c:	f3 44 0f 7f 60 70    	movdqu %xmm12,0x70(%rax)
  492322:	c3                   	ret

Disassembly of section .plt:
