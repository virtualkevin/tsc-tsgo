TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfPropertyOfType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:18819			0x80e9c0		493b6610		CMPQ SP, 0x10(R14)																	
  checker.go:18819			0x80e9c4		0f860f010000		JBE 0x80ead9																		
  checker.go:18819			0x80e9ca		55			PUSHQ BP																		
  checker.go:18819			0x80e9cb		4889e5			MOVQ SP, BP																		
  checker.go:18819			0x80e9ce		4883ec28		SUBQ $0x28, SP																		
  checker.go:18819			0x80e9d2		48894c2448		MOVQ CX, 0x48(SP)																	
  fused_intersection_lookup.go:10	0x80e9d7		4889442438		MOVQ AX, 0x38(SP)																	
  fused_intersection_lookup.go:10	0x80e9dc		813b00000010		CMPL 0(BX), $0x10000000																	
  fused_intersection_lookup.go:10	0x80e9e2		7511			JNE 0x80e9f5																		
  fused_intersection_lookup.go:10	0x80e9e4		8b5304			MOVL 0x4(BX), DX																	
  fused_intersection_lookup.go:10	0x80e9e7		81e220000006		ANDL $0x6000020, DX																	
  fused_intersection_lookup.go:10	0x80e9ed		81fa00000002		CMPL DX, $0x2000000																	
  fused_intersection_lookup.go:10	0x80e9f3		7407			JE 0x80e9fc																		
  fused_intersection_lookup.go:10	0x80e9f5		31d2			XORL DX, DX																		
  checker.go:18820			0x80e9f7		e988000000		JMP 0x80ea84																		
  types.go:702				0x80e9fc		488b5328		MOVQ 0x28(BX), DX																	
  fused_intersection_lookup.go:13	0x80ea00		90			NOPL																			
  types.go:702				0x80ea01		4c8d0d3880d200		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.IntersectionType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), R9	
  types.go:702				0x80ea08		4c39ca			CMPQ DX, R9																		
  types.go:702				0x80ea0b		0f85b1000000		JNE 0x80eac2																		
  types.go:702				0x80ea11		488b5330		MOVQ 0x30(BX), DX																	
  fused_intersection_lookup.go:14	0x80ea15		48399ae8000000		CMPQ 0xe8(DX), BX																	
  fused_intersection_lookup.go:14	0x80ea1c		7404			JE 0x80ea22																		
  fused_intersection_lookup.go:14	0x80ea1e		31d2			XORL DX, DX																		
  checker.go:18820			0x80ea20		eb62			JMP 0x80ea84																		
  fused_intersection_lookup.go:10	0x80ea22		48895c2440		MOVQ BX, 0x40(SP)																	
  fused_intersection_lookup.go:10	0x80ea27		48894c2448		MOVQ CX, 0x48(SP)																	
  fused_intersection_lookup.go:10	0x80ea2c		48897c2450		MOVQ DI, 0x50(SP)																	
  fused_intersection_lookup.go:17	0x80ea31		488b9ac8000000		MOVQ 0xc8(DX), BX																	
  fused_intersection_lookup.go:17	0x80ea38		488d0521a55d00		LEAQ 0x5da521(IP), AX																	
  fused_intersection_lookup.go:17	0x80ea3f		90			NOPL																			
  fused_intersection_lookup.go:17	0x80ea40		e85b52c0ff		CALL runtime.mapaccess1_faststr(SB)															
  fused_intersection_lookup.go:17	0x80ea45		488b10			MOVQ 0(AX), DX																		
  fused_intersection_lookup.go:18	0x80ea48		4885d2			TESTQ DX, DX																		
  fused_intersection_lookup.go:18	0x80ea4b		7421			JE 0x80ea6e																		
  fused_intersection_lookup.go:18	0x80ea4d		448b4a04		MOVL 0x4(DX), R9																	
  fused_intersection_lookup.go:18	0x80ea51		410fbae104		BTL $0x4, R9																		
  fused_intersection_lookup.go:18	0x80ea56		7216			JB 0x80ea6e																		
  checker.go:18756			0x80ea58		488b442438		MOVQ 0x38(SP), AX																	
  checker.go:18756			0x80ea5d		488b4c2448		MOVQ 0x48(SP), CX																	
  checker.go:18756			0x80ea62		488b5c2440		MOVQ 0x40(SP), BX																	
  checker.go:18756			0x80ea67		488b7c2450		MOVQ 0x50(SP), DI																	
  checker.go:18820			0x80ea6c		eb16			JMP 0x80ea84																		
  checker.go:18756			0x80ea6e		488b442438		MOVQ 0x38(SP), AX																	
  checker.go:18756			0x80ea73		488b4c2448		MOVQ 0x48(SP), CX																	
  checker.go:18756			0x80ea78		488b5c2440		MOVQ 0x40(SP), BX																	
  checker.go:18756			0x80ea7d		488b7c2450		MOVQ 0x50(SP), DI																	
  checker.go:18756			0x80ea82		31d2			XORL DX, DX																		
  checker.go:18820			0x80ea84		4885d2			TESTQ DX, DX																		
  checker.go:18820			0x80ea87		752b			JNE 0x80eab4																		
  checker.go:18823			0x80ea89		90			NOPL																			
  checker.go:18756			0x80ea8a		31f6			XORL SI, SI																		
  checker.go:18756			0x80ea8c		4189f0			MOVL SI, R8																		
  checker.go:18756			0x80ea8f		e84cfcffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getPropertyOfTypeEx(SB)								
  checker.go:18824			0x80ea94		4885c0			TESTQ AX, AX																		
  checker.go:18824			0x80ea97		7413			JE 0x80eaac																		
  checker.go:18825			0x80ea99		4889c3			MOVQ AX, BX																		
  checker.go:18825			0x80ea9c		488b442438		MOVQ 0x38(SP), AX																	
  checker.go:18825			0x80eaa1		e8ba17ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)									
  checker.go:18825			0x80eaa6		4883c428		ADDQ $0x28, SP																		
  checker.go:18825			0x80eaaa		5d			POPQ BP																			
  checker.go:18825			0x80eaab		c3			RET																			
  checker.go:18827			0x80eaac		31c0			XORL AX, AX																		
  checker.go:18827			0x80eaae		4883c428		ADDQ $0x28, SP																		
  checker.go:18827			0x80eab2		5d			POPQ BP																			
  checker.go:18827			0x80eab3		c3			RET																			
  checker.go:18821			0x80eab4		4889d3			MOVQ DX, BX																		
  checker.go:18821			0x80eab7		e8a417ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)									
  checker.go:18821			0x80eabc		4883c428		ADDQ $0x28, SP																		
  checker.go:18821			0x80eac0		5d			POPQ BP																			
  checker.go:18821			0x80eac1		c3			RET																			
  types.go:702				0x80eac2		4889d0			MOVQ DX, AX																		
  types.go:702				0x80eac5		488d1d94196e00		LEAQ 0x6e1994(IP), BX																	
  types.go:702				0x80eacc		488d0ded526200		LEAQ 0x6252ed(IP), CX																	
  types.go:702				0x80ead3		e88814c1ff		CALL runtime.panicdottypeI(SB)																
  types.go:702				0x80ead8		90			NOPL																			
  checker.go:18819			0x80ead9		4889442408		MOVQ AX, 0x8(SP)																	
  checker.go:18819			0x80eade		48895c2410		MOVQ BX, 0x10(SP)																	
  checker.go:18819			0x80eae3		48894c2418		MOVQ CX, 0x18(SP)																	
  checker.go:18819			0x80eae8		48897c2420		MOVQ DI, 0x20(SP)																	
  checker.go:18819			0x80eaed		e80e0fc8ff		CALL runtime.morestack_noctxt.abi0(SB)															
  checker.go:18819			0x80eaf2		488b442408		MOVQ 0x8(SP), AX																	
  checker.go:18819			0x80eaf7		488b5c2410		MOVQ 0x10(SP), BX																	
  checker.go:18819			0x80eafc		488b4c2418		MOVQ 0x18(SP), CX																	
  checker.go:18819			0x80eb01		488b7c2420		MOVQ 0x20(SP), DI																	
  checker.go:18819			0x80eb06		e9b5feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfPropertyOfType(SB)								
