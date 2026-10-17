
/tmp/tsc-go-linkstore-split:     file format elf64-x86-64


Disassembly of section .text:

00000000008019e0 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol>:
  8019e0:	49 3b 66 10          	cmp    0x10(%r14),%rsp
  8019e4:	0f 86 b7 00 00 00    	jbe    801aa1 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0xc1>
  8019ea:	55                   	push   %rbp
  8019eb:	48 89 e5             	mov    %rsp,%rbp
  8019ee:	48 83 ec 28          	sub    $0x28,%rsp
  8019f2:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  8019f7:	48 89 5c 24 40       	mov    %rbx,0x40(%rsp)
  8019fc:	48 8b 90 f8 08 00 00 	mov    0x8f8(%rax),%rdx
  801a03:	48 89 d9             	mov    %rbx,%rcx
  801a06:	48 8d 05 d3 30 5c 00 	lea    0x5c30d3(%rip),%rax        # dc4ae0 <type:*+0x108ae0>
  801a0d:	48 89 d3             	mov    %rdx,%rbx
  801a10:	e8 cb 16 c1 ff       	call   4130e0 <runtime.mapaccess1_fast64>
  801a15:	48 8b 10             	mov    (%rax),%rdx
  801a18:	48 85 d2             	test   %rdx,%rdx
  801a1b:	75 1f                	jne    801a3c <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x5c>
  801a1d:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  801a22:	48 05 f8 08 00 00    	add    $0x8f8,%rax
  801a28:	48 8d 1d d1 b3 d3 00 	lea    0xd3b3d1(%rip),%rbx        # 153ce00 <github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks]>
  801a2f:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
  801a34:	e8 87 53 10 00       	call   906dc0 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New>
  801a39:	48 89 c2             	mov    %rax,%rdx
  801a3c:	48 83 3a 00          	cmpq   $0x0,(%rdx)
  801a40:	75 55                	jne    801a97 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0xb7>
  801a42:	48 89 54 24 20       	mov    %rdx,0x20(%rsp)
  801a47:	48 8b 5a 10          	mov    0x10(%rdx),%rbx
  801a4b:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  801a50:	e8 2b fe ff ff       	call   801880 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol>
  801a55:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  801a5a:	48 8b 49 18          	mov    0x18(%rcx),%rcx
  801a5e:	48 89 c3             	mov    %rax,%rbx
  801a61:	31 ff                	xor    %edi,%edi
  801a63:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  801a68:	e8 33 43 02 00       	call   825da0 <github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias>
  801a6d:	83 3d 1c 7a 6f 01 00 	cmpl   $0x0,0x16f7a1c(%rip)        # 1ef9490 <runtime.writeBarrier>
  801a74:	75 07                	jne    801a7d <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x9d>
  801a76:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  801a7b:	eb 14                	jmp    801a91 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0xb1>
  801a7d:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  801a82:	48 8b 11             	mov    (%rcx),%rdx
  801a85:	e8 76 fa c8 ff       	call   491500 <runtime.gcWriteBarrier2>
  801a8a:	49 89 03             	mov    %rax,(%r11)
  801a8d:	49 89 53 08          	mov    %rdx,0x8(%r11)
  801a91:	48 89 01             	mov    %rax,(%rcx)
  801a94:	48 89 ca             	mov    %rcx,%rdx
  801a97:	48 8b 02             	mov    (%rdx),%rax
  801a9a:	48 83 c4 28          	add    $0x28,%rsp
  801a9e:	5d                   	pop    %rbp
  801a9f:	90                   	nop
  801aa0:	c3                   	ret
  801aa1:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  801aa6:	48 89 5c 24 10       	mov    %rbx,0x10(%rsp)
  801aab:	e8 50 df c8 ff       	call   48fa00 <runtime.morestack_noctxt.abi0>
  801ab0:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  801ab5:	48 8b 5c 24 10       	mov    0x10(%rsp),%rbx
  801aba:	e9 21 ff ff ff       	jmp    8019e0 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol>
