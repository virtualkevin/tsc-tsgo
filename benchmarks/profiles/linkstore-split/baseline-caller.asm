
packages/tsc-go/dist/tsc-go-lazy:     file format elf64-x86-64


Disassembly of section .text:

00000000008003c0 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol>:
  8003c0:	49 3b 66 10          	cmp    0x10(%r14),%rsp
  8003c4:	0f 86 88 00 00 00    	jbe    800452 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x92>
  8003ca:	55                   	push   %rbp
  8003cb:	48 89 e5             	mov    %rsp,%rbp
  8003ce:	48 83 ec 28          	sub    $0x28,%rsp
  8003d2:	48 89 44 24 38       	mov    %rax,0x38(%rsp)
  8003d7:	84 00                	test   %al,(%rax)
  8003d9:	48 05 f8 08 00 00    	add    $0x8f8,%rax
  8003df:	48 89 d9             	mov    %rbx,%rcx
  8003e2:	48 8d 1d b7 d8 d3 00 	lea    0xd3d8b7(%rip),%rbx        # 153dca0 <github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks]>
  8003e9:	e8 12 39 10 00       	call   903d00 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get>
  8003ee:	48 83 38 00          	cmpq   $0x0,(%rax)
  8003f2:	75 55                	jne    800449 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x89>
  8003f4:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  8003f9:	48 8b 58 10          	mov    0x10(%rax),%rbx
  8003fd:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  800402:	e8 59 fe ff ff       	call   800260 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol>
  800407:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  80040c:	48 8b 49 18          	mov    0x18(%rcx),%rcx
  800410:	48 89 c3             	mov    %rax,%rbx
  800413:	31 ff                	xor    %edi,%edi
  800415:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
  80041a:	e8 01 3c 02 00       	call   824020 <github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias>
  80041f:	83 3d ea 20 6f 01 00 	cmpl   $0x0,0x16f20ea(%rip)        # 1ef2510 <runtime.writeBarrier>
  800426:	75 07                	jne    80042f <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x6f>
  800428:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  80042d:	eb 14                	jmp    800443 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol+0x83>
  80042f:	48 8b 4c 24 20       	mov    0x20(%rsp),%rcx
  800434:	48 8b 11             	mov    (%rcx),%rdx
  800437:	e8 c4 10 c9 ff       	call   491500 <runtime.gcWriteBarrier2>
  80043c:	49 89 03             	mov    %rax,(%r11)
  80043f:	49 89 53 08          	mov    %rdx,0x8(%r11)
  800443:	48 89 01             	mov    %rax,(%rcx)
  800446:	48 89 c8             	mov    %rcx,%rax
  800449:	48 8b 00             	mov    (%rax),%rax
  80044c:	48 83 c4 28          	add    $0x28,%rsp
  800450:	5d                   	pop    %rbp
  800451:	c3                   	ret
  800452:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  800457:	48 89 5c 24 10       	mov    %rbx,0x10(%rsp)
  80045c:	0f 1f 40 00          	nopl   0x0(%rax)
  800460:	e8 9b f5 c8 ff       	call   48fa00 <runtime.morestack_noctxt.abi0>
  800465:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  80046a:	48 8b 5c 24 10       	mov    0x10(%rsp),%rbx
  80046f:	e9 4c ff ff ff       	jmp    8003c0 <github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol>
