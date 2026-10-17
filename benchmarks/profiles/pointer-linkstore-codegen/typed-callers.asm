TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:13999	0x7f18c0		493b6610		CMPQ SP, 0x10(R14)																	
  checker.go:13999	0x7f18c4		766f			JBE 0x7f1935																		
  checker.go:13999	0x7f18c6		55			PUSHQ BP																		
  checker.go:13999	0x7f18c7		4889e5			MOVQ SP, BP																		
  checker.go:13999	0x7f18ca		4883ec10		SUBQ $0x10, SP																		
  checker.go:14004	0x7f18ce		48897c2438		MOVQ DI, 0x38(SP)																	
  checker.go:14004	0x7f18d3		895c2428		MOVL BX, 0x28(SP)																	
  checker.go:14004	0x7f18d7		48894c2430		MOVQ CX, 0x30(SP)																	
  checker.go:14000	0x7f18dc		ff405c			INCL 0x5c(AX)																		
  checker.go:14001	0x7f18df		4805c0020000		ADDQ $0x2c0, AX																		
  checker.go:14001	0x7f18e5		488d1d14a1d400		LEAQ github.com/microsoft/typescript-go/internal/core..dict.Arena[github.com/microsoft/typescript-go/internal/ast.Symbol](SB), BX			
  checker.go:14001	0x7f18ec		e88f97eaff		CALL github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0]).New(SB)	
  checker.go:14002	0x7f18f1		8b4c2428		MOVL 0x28(SP), CX																	
  checker.go:14002	0x7f18f5		81c900000002		ORL $0x2000000, CX																	
  checker.go:14002	0x7f18fb		8908			MOVL CX, 0(AX)																		
  checker.go:14003	0x7f18fd		488b4c2438		MOVQ 0x38(SP), CX																	
  checker.go:14003	0x7f1902		48894810		MOVQ CX, 0x10(AX)																	
  checker.go:14003	0x7f1906		833d032c700100		CMPL runtime.writeBarrier(SB), $0x0															
  checker.go:14003	0x7f190d		7507			JNE 0x7f1916																		
  checker.go:14003	0x7f190f		488b542430		MOVQ 0x30(SP), DX																	
  checker.go:14003	0x7f1914		eb15			JMP 0x7f192b																		
  checker.go:14003	0x7f1916		488b4808		MOVQ 0x8(AX), CX																	
  checker.go:14003	0x7f191a		e8e1fbc9ff		CALL runtime.gcWriteBarrier2(SB)															
  checker.go:14003	0x7f191f		488b542430		MOVQ 0x30(SP), DX																	
  checker.go:14003	0x7f1924		498913			MOVQ DX, 0(R11)																		
  checker.go:14003	0x7f1927		49894b08		MOVQ CX, 0x8(R11)																	
  checker.go:14003	0x7f192b		48895008		MOVQ DX, 0x8(AX)																	
  checker.go:14004	0x7f192f		4883c410		ADDQ $0x10, SP																		
  checker.go:14004	0x7f1933		5d			POPQ BP																			
  checker.go:14004	0x7f1934		c3			RET																			
  checker.go:13999	0x7f1935		4889442408		MOVQ AX, 0x8(SP)																	
  checker.go:13999	0x7f193a		895c2410		MOVL BX, 0x10(SP)																	
  checker.go:13999	0x7f193e		48894c2418		MOVQ CX, 0x18(SP)																	
  checker.go:13999	0x7f1943		48897c2420		MOVQ DI, 0x20(SP)																	
  checker.go:13999	0x7f1948		e8b3e0c9ff		CALL runtime.morestack_noctxt.abi0(SB)															
  checker.go:13999	0x7f194d		488b442408		MOVQ 0x8(SP), AX																	
  checker.go:13999	0x7f1952		8b5c2410		MOVL 0x10(SP), BX																	
  checker.go:13999	0x7f1956		488b4c2418		MOVQ 0x18(SP), CX																	
  checker.go:13999	0x7f195b		488b7c2420		MOVQ 0x20(SP), DI																	
  checker.go:13999	0x7f1960		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newSymbol(SB)									

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16444	0x8003c0		493b6610		CMPQ SP, 0x10(R14)																											
  checker.go:16444	0x8003c4		0f8688000000		JBE 0x800452																												
  checker.go:16444	0x8003ca		55			PUSHQ BP																												
  checker.go:16444	0x8003cb		4889e5			MOVQ SP, BP																												
  checker.go:16444	0x8003ce		4883ec28		SUBQ $0x28, SP																												
  checker.go:16446	0x8003d2		4889442438		MOVQ AX, 0x38(SP)																											
  checker.go:16445	0x8003d7		8400			TESTB AL, 0(AX)																												
  checker.go:16445	0x8003d9		4805f8080000		ADDQ $0x8f8, AX																												
  checker.go:16445	0x8003df		4889d9			MOVQ BX, CX																												
  checker.go:16445	0x8003e2		488d1d579dd400		LEAQ github.com/microsoft/typescript-go/internal/core..dict.PointerLinkStore[github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX			
  checker.go:16445	0x8003e9		e8b23a1000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)	
  checker.go:16446	0x8003ee		48833800		CMPQ 0(AX), $0x0																											
  checker.go:16446	0x8003f2		7555			JNE 0x800449																												
  checker.go:16445	0x8003f4		4889442420		MOVQ AX, 0x20(SP)																											
  checker.go:16447	0x8003f9		488b5810		MOVQ 0x10(AX), BX																											
  checker.go:16447	0x8003fd		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:16447	0x800402		e859feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)																			
  checker.go:16447	0x800407		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x80040c		488b4918		MOVQ 0x18(CX), CX																											
  checker.go:22038	0x800410		4889c3			MOVQ AX, BX																												
  checker.go:22038	0x800413		31ff			XORL DI, DI																												
  checker.go:22038	0x800415		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:22038	0x80041a		e8013c0200		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB)																	
  checker.go:16447	0x80041f		833dea406f0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:16447	0x800426		7507			JNE 0x80042f																												
  checker.go:16447	0x800428		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x80042d		eb14			JMP 0x800443																												
  checker.go:16447	0x80042f		488b4c2420		MOVQ 0x20(SP), CX																											
  checker.go:16447	0x800434		488b11			MOVQ 0(CX), DX																												
  checker.go:16447	0x800437		e8c410c9ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:16447	0x80043c		498903			MOVQ AX, 0(R11)																												
  checker.go:16447	0x80043f		49895308		MOVQ DX, 0x8(R11)																											
  checker.go:16447	0x800443		488901			MOVQ AX, 0(CX)																												
  checker.go:16449	0x800446		4889c8			MOVQ CX, AX																												
  checker.go:16449	0x800449		488b00			MOVQ 0(AX), AX																												
  checker.go:16449	0x80044c		4883c428		ADDQ $0x28, SP																												
  checker.go:16449	0x800450		5d			POPQ BP																													
  checker.go:16449	0x800451		c3			RET																													
  checker.go:16444	0x800452		4889442408		MOVQ AX, 0x8(SP)																											
  checker.go:16444	0x800457		48895c2410		MOVQ BX, 0x10(SP)																											
  checker.go:16444	0x80045c		0f1f4000		NOPL 0(AX)																												
  checker.go:16444	0x800460		e89bf5c8ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  checker.go:16444	0x800465		488b442408		MOVQ 0x8(SP), AX																											
  checker.go:16444	0x80046a		488b5c2410		MOVQ 0x10(SP), BX																											
  checker.go:16444	0x80046f		e94cffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)																	

TEXT github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB) github.com/microsoft/typescript-go/internal/core/arena.go
  arena.go:13		0x9043a0		493b6610		CMPQ SP, 0x10(R14)																	
  arena.go:13		0x9043a4		0f86c1000000		JBE 0x90446b																		
  arena.go:13		0x9043aa		55			PUSHQ BP																		
  arena.go:13		0x9043ab		4889e5			MOVQ SP, BP																		
  arena.go:13		0x9043ae		4883ec28		SUBQ $0x28, SP																		
  arena.go:14		0x9043b2		488b5008		MOVQ 0x8(AX), DX																	
  arena.go:14		0x9043b6		48395010		CMPQ 0x10(AX), DX																	
  arena.go:14		0x9043ba		7578			JNE 0x904434																		
  arena.go:63		0x9043bc		4885d2			TESTQ DX, DX																		
  arena.go:64		0x9043bf		41b801000000		MOVL $0x1, R8																		
  arena.go:64		0x9043c5		490f44d0		CMOVE R8, DX																		
  arena.go:64		0x9043c9		488d3c12		LEAQ 0(DX)(DX*1), DI																	
  arena.go:64		0x9043cd		4881ff00010000		CMPQ DI, $0x100																		
  arena.go:15		0x9043d4		ba00010000		MOVL $0x100, DX																		
  arena.go:15		0x9043d9		480f4ffa		CMOVG DX, DI																		
  arena.go:15		0x9043dd		0f1f00			NOPL 0(AX)																		
  slices.go:424		0x9043e0		4885ff			TESTQ DI, DI																		
  slices.go:424		0x9043e3		7f06			JG 0x9043eb																		
  slices.go:424		0x9043e5		31c9			XORL CX, CX																		
  slices.go:424		0x9043e7		31d2			XORL DX, DX																		
  slices.go:424		0x9043e9		eb22			JMP 0x90440d																		
  arena.go:14		0x9043eb		4889442438		MOVQ AX, 0x38(SP)																	
  slices.go:426		0x9043f0		31c0			XORL AX, AX																		
  slices.go:426		0x9043f2		4889fb			MOVQ DI, BX																		
  slices.go:426		0x9043f5		31c9			XORL CX, CX																		
  slices.go:426		0x9043f7		488d35c2fb5900		LEAQ 0x59fbc2(IP), SI																	
  slices.go:426		0x9043fe		6690			NOPW																			
  slices.go:426		0x904400		e85b7db8ff		CALL runtime.growslice(SB)																
  arena.go:17		0x904405		4889c2			MOVQ AX, DX																		
  arena.go:17		0x904408		488b442438		MOVQ 0x38(SP), AX																	
  arena.go:17		0x90440d		48c7400800000000	MOVQ $0x0, 0x8(AX)																	
  arena.go:17		0x904415		48894810		MOVQ CX, 0x10(AX)																	
  arena.go:17		0x904419		833df0005f0100		CMPL runtime.writeBarrier(SB), $0x0															
  arena.go:17		0x904420		740f			JE 0x904431																		
  arena.go:17		0x904422		488b08			MOVQ 0(AX), CX																		
  arena.go:17		0x904425		e8d6d0b8ff		CALL runtime.gcWriteBarrier2(SB)															
  arena.go:17		0x90442a		498913			MOVQ DX, 0(R11)																		
  arena.go:17		0x90442d		49894b08		MOVQ CX, 0x8(R11)																	
  arena.go:17		0x904431		488910			MOVQ DX, 0(AX)																		
  arena.go:19		0x904434		488b4808		MOVQ 0x8(AX), CX																	
  arena.go:19		0x904438		488b5010		MOVQ 0x10(AX), DX																	
  arena.go:20		0x90443c		488d5901		LEAQ 0x1(CX), BX																	
  arena.go:20		0x904440		4839da			CMPQ DX, BX																		
  arena.go:20		0x904443		7220			JB 0x904465																		
  arena.go:20		0x904445		48895808		MOVQ BX, 0x8(AX)																	
  arena.go:21		0x904449		4839d9			CMPQ CX, BX																		
  arena.go:21		0x90444c		7311			JAE 0x90445f																		
  arena.go:21		0x90444e		488b10			MOVQ 0(AX), DX																		
  arena.go:21		0x904451		486bc938		IMULQ $0x38, CX, CX																	
  arena.go:21		0x904455		488d040a		LEAQ 0(DX)(CX*1), AX																	
  arena.go:21		0x904459		4883c428		ADDQ $0x28, SP																		
  arena.go:21		0x90445d		5d			POPQ BP																			
  arena.go:21		0x90445e		c3			RET																			
  arena.go:21		0x90445f		90			NOPL																			
  arena.go:21		0x904460		e83bd4b8ff		CALL runtime.panicBounds(SB)																
  arena.go:20		0x904465		e836d4b8ff		CALL runtime.panicBounds(SB)																
  arena.go:20		0x90446a		90			NOPL																			
  arena.go:13		0x90446b		4889442408		MOVQ AX, 0x8(SP)																	
  arena.go:13		0x904470		48895c2410		MOVQ BX, 0x10(SP)																	
  arena.go:13		0x904475		e886b5b8ff		CALL runtime.morestack_noctxt.abi0(SB)															
  arena.go:13		0x90447a		488b442408		MOVQ 0x8(SP), AX																	
  arena.go:13		0x90447f		488b5c2410		MOVQ 0x10(SP), BX																	
  arena.go:13		0x904484		e917ffffff		JMP github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB)	
