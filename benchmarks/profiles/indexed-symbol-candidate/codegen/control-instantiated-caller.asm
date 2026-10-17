TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16444	0x800660		493b6610		CMPQ SP, 0x10(R14)																											
  checker.go:16444	0x800664		0f8688000000		JBE 0x8006f2																												
  checker.go:16444	0x80066a		55			PUSHQ BP																												
  checker.go:16444	0x80066b		4889e5			MOVQ SP, BP																												
  checker.go:16444	0x80066e		4883ec28		SUBQ $0x28, SP																												
  checker.go:16446	0x800672		4889442438		MOVQ AX, 0x38(SP)																											
  checker.go:16445	0x800677		8400			TESTB AL, 0(AX)																												
  checker.go:16445	0x800679		480500090000		ADDQ $0x900, AX																												
  checker.go:16445	0x80067f		4889d9			MOVQ BX, CX																												
  checker.go:16445	0x800682		488d1d37a0d400		LEAQ github.com/microsoft/typescript-go/internal/core..dict.PointerLinkStore[github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX			
  checker.go:16445	0x800689		e852471000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)	
  checker.go:16446	0x80068e		48833800		CMPQ 0(AX), $0x0																											
  checker.go:16446	0x800692		7555			JNE 0x8006e9																												
  checker.go:16445	0x800694		4889442420		MOVQ AX, 0x20(SP)																											
  checker.go:16447	0x800699		488b5810		MOVQ 0x10(AX), BX																											
  checker.go:16447	0x80069d		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:16447	0x8006a2		e859feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)																			
  checker.go:16447	0x8006a7		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x8006ac		488b4918		MOVQ 0x18(CX), CX																											
  checker.go:21998	0x8006b0		4889c3			MOVQ AX, BX																												
  checker.go:21998	0x8006b3		31ff			XORL DI, DI																												
  checker.go:21998	0x8006b5		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:21998	0x8006ba		e861430200		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB)																	
  checker.go:16447	0x8006bf		833d4a4e6f0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:16447	0x8006c6		7507			JNE 0x8006cf																												
  checker.go:16447	0x8006c8		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x8006cd		eb14			JMP 0x8006e3																												
  checker.go:16447	0x8006cf		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x8006d4		488b11			MOVQ 0(CX), DX																												
  checker.go:16447	0x8006d7		e8240ec9ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:16447	0x8006dc		498903			MOVQ AX, 0(R11)																												
  checker.go:16447	0x8006df		49895308		MOVQ DX, 0x8(R11)																											
  checker.go:16447	0x8006e3		488901			MOVQ AX, 0(CX)																												
  checker.go:16449	0x8006e6		4889c8			MOVQ CX, AX																												
  checker.go:16449	0x8006e9		488b00			MOVQ 0(AX), AX																												
  checker.go:16449	0x8006ec		4883c428		ADDQ $0x28, SP																												
  checker.go:16449	0x8006f0		5d			POPQ BP																													
  checker.go:16449	0x8006f1		c3			RET																													
  checker.go:16444	0x8006f2		4889442408		MOVQ AX, 0x8(SP)																											
  checker.go:16444	0x8006f7		48895c2410		MOVQ BX, 0x10(SP)																											
  checker.go:16444	0x8006fc		0f1f4000		NOPL 0(AX)																												
  checker.go:16444	0x800700		e8fbf2c8ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  checker.go:16444	0x800705		488b442408		MOVQ 0x8(SP), AX																											
  checker.go:16444	0x80070a		488b5c2410		MOVQ 0x10(SP), BX																											
  checker.go:16444	0x80070f		e94cffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)																	
