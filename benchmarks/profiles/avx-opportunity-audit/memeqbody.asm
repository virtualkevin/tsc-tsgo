
/home/dev/tssss/tsc-tsgo/packages/tsc-go/dist/tsc-go:     file format elf64-x86-64


Disassembly of section .text:

00000000004044e0 <memeqbody>:
  4044e0:	48 83 fb 08          	cmp    $0x8,%rbx
  4044e4:	0f 82 08 01 00 00    	jb     4045f2 <memeqbody+0x112>
  4044ea:	48 83 fb 40          	cmp    $0x40,%rbx
  4044ee:	0f 82 cc 00 00 00    	jb     4045c0 <memeqbody+0xe0>
  4044f4:	80 3d c9 69 e2 01 01 	cmpb   $0x1,0x1e269c9(%rip)        # 222aec4 <internal/cpu.X86+0x44>
  4044fb:	74 73                	je     404570 <memeqbody+0x90>
  4044fd:	0f 1f 00             	nopl   (%rax)
  404500:	48 83 fb 40          	cmp    $0x40,%rbx
  404504:	0f 82 b6 00 00 00    	jb     4045c0 <memeqbody+0xe0>
  40450a:	f3 0f 6f 06          	movdqu (%rsi),%xmm0
  40450e:	f3 0f 6f 0f          	movdqu (%rdi),%xmm1
  404512:	f3 0f 6f 56 10       	movdqu 0x10(%rsi),%xmm2
  404517:	f3 0f 6f 5f 10       	movdqu 0x10(%rdi),%xmm3
  40451c:	f3 0f 6f 66 20       	movdqu 0x20(%rsi),%xmm4
  404521:	f3 0f 6f 6f 20       	movdqu 0x20(%rdi),%xmm5
  404526:	f3 0f 6f 76 30       	movdqu 0x30(%rsi),%xmm6
  40452b:	f3 0f 6f 7f 30       	movdqu 0x30(%rdi),%xmm7
  404530:	66 0f 74 c1          	pcmpeqb %xmm1,%xmm0
  404534:	66 0f 74 d3          	pcmpeqb %xmm3,%xmm2
  404538:	66 0f 74 e5          	pcmpeqb %xmm5,%xmm4
  40453c:	66 0f 74 f7          	pcmpeqb %xmm7,%xmm6
  404540:	66 0f db c2          	pand   %xmm2,%xmm0
  404544:	66 0f db e6          	pand   %xmm6,%xmm4
  404548:	66 0f db c4          	pand   %xmm4,%xmm0
  40454c:	66 0f d7 d0          	pmovmskb %xmm0,%edx
  404550:	48 83 c6 40          	add    $0x40,%rsi
  404554:	48 83 c7 40          	add    $0x40,%rdi
  404558:	48 83 eb 40          	sub    $0x40,%rbx
  40455c:	81 fa ff ff 00 00    	cmp    $0xffff,%edx
  404562:	74 9c                	je     404500 <memeqbody+0x20>
  404564:	48 31 c0             	xor    %rax,%rax
  404567:	c3                   	ret
  404568:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  40456f:	00 
  404570:	48 83 fb 40          	cmp    $0x40,%rbx
  404574:	72 3d                	jb     4045b3 <memeqbody+0xd3>
  404576:	c5 fe 6f 06          	vmovdqu (%rsi),%ymm0
  40457a:	c5 fe 6f 0f          	vmovdqu (%rdi),%ymm1
  40457e:	c5 fe 6f 56 20       	vmovdqu 0x20(%rsi),%ymm2
  404583:	c5 fe 6f 5f 20       	vmovdqu 0x20(%rdi),%ymm3
  404588:	c5 fd 74 e1          	vpcmpeqb %ymm1,%ymm0,%ymm4
  40458c:	c5 e5 74 ea          	vpcmpeqb %ymm2,%ymm3,%ymm5
  404590:	c5 d5 db f4          	vpand  %ymm4,%ymm5,%ymm6
  404594:	c5 fd d7 d6          	vpmovmskb %ymm6,%edx
  404598:	48 83 c6 40          	add    $0x40,%rsi
  40459c:	48 83 c7 40          	add    $0x40,%rdi
  4045a0:	48 83 eb 40          	sub    $0x40,%rbx
  4045a4:	81 fa ff ff ff ff    	cmp    $0xffffffff,%edx
  4045aa:	74 c4                	je     404570 <memeqbody+0x90>
  4045ac:	c5 f8 77             	vzeroupper
  4045af:	48 31 c0             	xor    %rax,%rax
  4045b2:	c3                   	ret
  4045b3:	c5 f8 77             	vzeroupper
  4045b6:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  4045bd:	00 00 
  4045bf:	90                   	nop
  4045c0:	48 83 fb 08          	cmp    $0x8,%rbx
  4045c4:	76 1b                	jbe    4045e1 <memeqbody+0x101>
  4045c6:	48 8b 0e             	mov    (%rsi),%rcx
  4045c9:	48 8b 17             	mov    (%rdi),%rdx
  4045cc:	48 83 c6 08          	add    $0x8,%rsi
  4045d0:	48 83 c7 08          	add    $0x8,%rdi
  4045d4:	48 83 eb 08          	sub    $0x8,%rbx
  4045d8:	48 39 d1             	cmp    %rdx,%rcx
  4045db:	74 e3                	je     4045c0 <memeqbody+0xe0>
  4045dd:	48 31 c0             	xor    %rax,%rax
  4045e0:	c3                   	ret
  4045e1:	48 8b 4c 1e f8       	mov    -0x8(%rsi,%rbx,1),%rcx
  4045e6:	48 8b 54 1f f8       	mov    -0x8(%rdi,%rbx,1),%rdx
  4045eb:	48 39 d1             	cmp    %rdx,%rcx
  4045ee:	0f 94 c0             	sete   %al
  4045f1:	c3                   	ret
  4045f2:	48 83 fb 00          	cmp    $0x0,%rbx
  4045f6:	74 37                	je     40462f <memeqbody+0x14f>
  4045f8:	48 8d 0c dd 00 00 00 	lea    0x0(,%rbx,8),%rcx
  4045ff:	00 
  404600:	48 f7 d9             	neg    %rcx
  404603:	40 80 fe f8          	cmp    $0xf8,%sil
  404607:	77 05                	ja     40460e <memeqbody+0x12e>
  404609:	48 8b 36             	mov    (%rsi),%rsi
  40460c:	eb 08                	jmp    404616 <memeqbody+0x136>
  40460e:	48 8b 74 1e f8       	mov    -0x8(%rsi,%rbx,1),%rsi
  404613:	48 d3 ee             	shr    %cl,%rsi
  404616:	40 80 ff f8          	cmp    $0xf8,%dil
  40461a:	77 05                	ja     404621 <memeqbody+0x141>
  40461c:	48 8b 3f             	mov    (%rdi),%rdi
  40461f:	eb 08                	jmp    404629 <memeqbody+0x149>
  404621:	48 8b 7c 1f f8       	mov    -0x8(%rdi,%rbx,1),%rdi
  404626:	48 d3 ef             	shr    %cl,%rdi
  404629:	48 29 f7             	sub    %rsi,%rdi
  40462c:	48 d3 e7             	shl    %cl,%rdi
  40462f:	0f 94 c0             	sete   %al
  404632:	c3                   	ret

Disassembly of section .plt:
