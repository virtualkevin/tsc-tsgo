
packages/tsc-go/dist/tsc-go-lazy:     file format elf64-x86-64


Disassembly of section .text:

0000000000903d00 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get>:
  903d00:	49 3b 66 10          	cmp    0x10(%r14),%rsp
  903d04:	0f 86 e0 00 00 00    	jbe    903dea <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0xea>
  903d0a:	55                   	push   %rbp
  903d0b:	48 89 e5             	mov    %rsp,%rbp
  903d0e:	48 83 ec 20          	sub    $0x20,%rsp
  903d12:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  903d17:	48 89 5c 24 38       	mov    %rbx,0x38(%rsp)
  903d1c:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  903d21:	48 8b 10             	mov    (%rax),%rdx
  903d24:	48 89 ce             	mov    %rcx,%rsi
  903d27:	48 8b 43 30          	mov    0x30(%rbx),%rax
  903d2b:	48 89 d3             	mov    %rdx,%rbx
  903d2e:	48 89 f1             	mov    %rsi,%rcx
  903d31:	e8 aa f3 b0 ff       	call   4130e0 <runtime.mapaccess1_fast64>
  903d36:	48 8b 00             	mov    (%rax),%rax
  903d39:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  903d40:	48 85 c0             	test   %rax,%rax
  903d43:	0f 85 9b 00 00 00    	jne    903de4 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0xe4>
  903d49:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
  903d4e:	48 83 38 00          	cmpq   $0x0,(%rax)
  903d52:	75 2f                	jne    903d83 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0x83>
  903d54:	e8 67 3f b8 ff       	call   487cc0 <runtime.makemap_small>
  903d59:	83 3d b0 e7 5e 01 00 	cmpl   $0x0,0x15ee7b0(%rip)        # 1ef2510 <runtime.writeBarrier>
  903d60:	75 07                	jne    903d69 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0x69>
  903d62:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  903d67:	eb 14                	jmp    903d7d <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0x7d>
  903d69:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  903d6e:	48 8b 11             	mov    (%rcx),%rdx
  903d71:	e8 8a d7 b8 ff       	call   491500 <runtime.gcWriteBarrier2>
  903d76:	49 89 03             	mov    %rax,(%r11)
  903d79:	49 89 53 08          	mov    %rdx,0x8(%r11)
  903d7d:	48 89 01             	mov    %rax,(%rcx)
  903d80:	48 89 c8             	mov    %rcx,%rax
  903d83:	48 83 c0 08          	add    $0x8,%rax
  903d87:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  903d8c:	48 8b 19             	mov    (%rcx),%rbx
  903d8f:	e8 8c 00 00 00       	call   903e20 <github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New>
  903d94:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
  903d99:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  903d9e:	48 8b 19             	mov    (%rcx),%rbx
  903da1:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  903da6:	48 8b 41 30          	mov    0x30(%rcx),%rax
  903daa:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
  903daf:	e8 ec fa b0 ff       	call   4138a0 <runtime.mapassign_fast64ptr>
  903db4:	83 3d 55 e7 5e 01 00 	cmpl   $0x0,0x15ee755(%rip)        # 1ef2510 <runtime.writeBarrier>
  903dbb:	75 07                	jne    903dc4 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0xc4>
  903dbd:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  903dc2:	eb 14                	jmp    903dd8 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get+0xd8>
  903dc4:	48 8b 08             	mov    (%rax),%rcx
  903dc7:	e8 34 d7 b8 ff       	call   491500 <runtime.gcWriteBarrier2>
  903dcc:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  903dd1:	49 89 13             	mov    %rdx,(%r11)
  903dd4:	49 89 4b 08          	mov    %rcx,0x8(%r11)
  903dd8:	48 89 10             	mov    %rdx,(%rax)
  903ddb:	48 89 d0             	mov    %rdx,%rax
  903dde:	48 83 c4 20          	add    $0x20,%rsp
  903de2:	5d                   	pop    %rbp
  903de3:	c3                   	ret
  903de4:	48 83 c4 20          	add    $0x20,%rsp
  903de8:	5d                   	pop    %rbp
  903de9:	c3                   	ret
  903dea:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  903def:	48 89 5c 24 10       	mov    %rbx,0x10(%rsp)
  903df4:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  903df9:	e8 02 bc b8 ff       	call   48fa00 <runtime.morestack_noctxt.abi0>
  903dfe:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  903e03:	48 8b 5c 24 10       	mov    0x10(%rsp),%rbx
  903e08:	48 8b 4c 24 18       	mov    0x18(%rsp),%rcx
  903e0d:	e9 ee fe ff ff       	jmp    903d00 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get>
