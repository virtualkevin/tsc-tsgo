TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16444	0x8007a0		493b6610		CMPQ SP, 0x10(R14)																												
  checker.go:16444	0x8007a4		0f869b000000		JBE 0x800845																													
  checker.go:16444	0x8007aa		55			PUSHQ BP																													
  checker.go:16444	0x8007ab		4889e5			MOVQ SP, BP																													
  checker.go:16444	0x8007ae		4883ec28		SUBQ $0x28, SP																													
  checker.go:16445	0x8007b2		8400			TESTB AL, 0(AX)																													
  symbol_links.go:12	0x8007b4		4885db			TESTQ BX, BX																													
  symbol_links.go:12	0x8007b7		7405			JE 0x8007be																													
  symbol_links.go:15	0x8007b9		8b5360			MOVL 0x60(BX), DX																												
  symbol_links.go:18	0x8007bc		eb02			JMP 0x8007c0																													
  symbol_links.go:18	0x8007be		31d2			XORL DX, DX																													
  symbol_links.go:12	0x8007c0		4889442438		MOVQ AX, 0x38(SP)																												
  symbol_links.go:18	0x8007c5		480500090000		ADDQ $0x900, AX																													
  symbol_links.go:18	0x8007cb		488d35eee5d400		LEAQ github.com/microsoft/typescript-go/internal/core..dict.IndexedPointerLinkStore[github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), SI			
  symbol_links.go:18	0x8007d2		4889d9			MOVQ BX, CX																													
  symbol_links.go:18	0x8007d5		89d7			MOVL DX, DI																													
  symbol_links.go:18	0x8007d7		4889f3			MOVQ SI, BX																													
  symbol_links.go:18	0x8007da		e801511000		CALL github.com/microsoft/typescript-go/internal/core.(*IndexedPointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)	
  checker.go:16446	0x8007df		48833800		CMPQ 0(AX), $0x0																												
  checker.go:16446	0x8007e3		7557			JNE 0x80083c																													
  symbol_links.go:18	0x8007e5		4889442420		MOVQ AX, 0x20(SP)																												
  checker.go:16447	0x8007ea		488b5810		MOVQ 0x10(AX), BX																												
  checker.go:16447	0x8007ee		488b442438		MOVQ 0x38(SP), AX																												
  checker.go:16447	0x8007f3		e848feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)																				
  checker.go:16447	0x8007f8		488b4c2420		MOVQ 0x20(SP), CX																												
  checker.go:16447	0x8007fd		488b4918		MOVQ 0x18(CX), CX																												
  checker.go:21998	0x800801		4889c3			MOVQ AX, BX																													
  checker.go:21998	0x800804		31ff			XORL DI, DI																													
  checker.go:21998	0x800806		488b442438		MOVQ 0x38(SP), AX																												
  checker.go:21998	0x80080b		e870450200		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB)																		
  checker.go:16447	0x800810		833df98c6f0100		CMPL runtime.writeBarrier(SB), $0x0																										
  checker.go:16447	0x800817		7509			JNE 0x800822																													
  checker.go:16447	0x800819		488b4c2420		MOVQ 0x20(SP), CX																												
  checker.go:16447	0x80081e		6690			NOPW																														
  checker.go:16447	0x800820		eb14			JMP 0x800836																													
  checker.go:16447	0x800822		488b4c2420		MOVQ 0x20(SP), CX																												
  checker.go:16447	0x800827		488b11			MOVQ 0(CX), DX																													
  checker.go:16447	0x80082a		e8d10cc9ff		CALL runtime.gcWriteBarrier2(SB)																										
  checker.go:16447	0x80082f		498903			MOVQ AX, 0(R11)																													
  checker.go:16447	0x800832		49895308		MOVQ DX, 0x8(R11)																												
  checker.go:16447	0x800836		488901			MOVQ AX, 0(CX)																													
  checker.go:16449	0x800839		4889c8			MOVQ CX, AX																													
  checker.go:16449	0x80083c		488b00			MOVQ 0(AX), AX																													
  checker.go:16449	0x80083f		4883c428		ADDQ $0x28, SP																													
  checker.go:16449	0x800843		5d			POPQ BP																														
  checker.go:16449	0x800844		c3			RET																														
  checker.go:16444	0x800845		4889442408		MOVQ AX, 0x8(SP)																												
  checker.go:16444	0x80084a		48895c2410		MOVQ BX, 0x10(SP)																												
  checker.go:16444	0x80084f		e8acf1c8ff		CALL runtime.morestack_noctxt.abi0(SB)																										
  checker.go:16444	0x800854		488b442408		MOVQ 0x8(SP), AX																												
  checker.go:16444	0x800859		488b5c2410		MOVQ 0x10(SP), BX																												
  checker.go:16444	0x80085e		6690			NOPW																														
  checker.go:16444	0x800860		e93bffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)																		
