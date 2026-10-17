
/tmp/tsc-go-linkstore-split:     file format elf64-x86-64


Disassembly of section .text:

0000000000906dc0 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New>:
  906dc0:	49 3b 66 10          	cmp    0x10(%r14),%rsp
  906dc4:	0f 86 b3 00 00 00    	jbe    906e7d <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0xbd>
  906dca:	55                   	push   %rbp
  906dcb:	48 89 e5             	mov    %rsp,%rbp
  906dce:	48 83 ec 20          	sub    $0x20,%rsp
  906dd2:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  906dd7:	48 89 5c 24 38       	mov    %rbx,0x38(%rsp)
  906ddc:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  906de1:	48 83 38 00          	cmpq   $0x0,(%rax)
  906de5:	75 34                	jne    906e1b <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0x5b>
  906de7:	e8 d4 0e b8 ff       	call   487cc0 <runtime.makemap_small>
  906dec:	83 3d 9d 26 5f 01 00 	cmpl   $0x0,0x15f269d(%rip)        # 1ef9490 <runtime.writeBarrier>
  906df3:	75 07                	jne    906dfc <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0x3c>
  906df5:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  906dfa:	eb 14                	jmp    906e10 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0x50>
  906dfc:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  906e01:	48 8b 11             	mov    (%rcx),%rdx
  906e04:	e8 f7 a6 b8 ff       	call   491500 <runtime.gcWriteBarrier2>
  906e09:	49 89 03             	mov    %rax,(%r11)
  906e0c:	49 89 53 08          	mov    %rdx,0x8(%r11)
  906e10:	48 89 01             	mov    %rax,(%rcx)
  906e13:	48 89 c8             	mov    %rcx,%rax
  906e16:	48 8b 5c 24 38       	mov    0x38(%rsp),%rbx
  906e1b:	48 83 c0 08          	add    $0x8,%rax
  906e1f:	48 8b 5b 08          	mov    0x8(%rbx),%rbx
  906e23:	e8 98 00 00 00       	call   906ec0 <github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New>
  906e28:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
  906e2d:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
  906e32:	48 8b 19             	mov    (%rcx),%rbx
  906e35:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
  906e3a:	48 8b 41 60          	mov    0x60(%rcx),%rax
  906e3e:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
  906e43:	e8 58 ca b0 ff       	call   4138a0 <runtime.mapassign_fast64ptr>
  906e48:	83 3d 41 26 5f 01 00 	cmpl   $0x0,0x15f2641(%rip)        # 1ef9490 <runtime.writeBarrier>
  906e4f:	75 07                	jne    906e58 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0x98>
  906e51:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  906e56:	eb 19                	jmp    906e71 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New+0xb1>
  906e58:	48 8b 08             	mov    (%rax),%rcx
  906e5b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  906e60:	e8 9b a6 b8 ff       	call   491500 <runtime.gcWriteBarrier2>
  906e65:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  906e6a:	49 89 13             	mov    %rdx,(%r11)
  906e6d:	49 89 4b 08          	mov    %rcx,0x8(%r11)
  906e71:	48 89 10             	mov    %rdx,(%rax)
  906e74:	48 89 d0             	mov    %rdx,%rax
  906e77:	48 83 c4 20          	add    $0x20,%rsp
  906e7b:	5d                   	pop    %rbp
  906e7c:	c3                   	ret
  906e7d:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  906e82:	48 89 5c 24 10       	mov    %rbx,0x10(%rsp)
  906e87:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
  906e8c:	e8 6f 8b b8 ff       	call   48fa00 <runtime.morestack_noctxt.abi0>
  906e91:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  906e96:	48 8b 5c 24 10       	mov    0x10(%rsp),%rbx
  906e9b:	48 8b 4c 24 18       	mov    0x18(%rsp),%rcx
  906ea0:	e9 1b ff ff ff       	jmp    906dc0 <github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New>
