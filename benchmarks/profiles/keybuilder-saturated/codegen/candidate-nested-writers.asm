TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17310	0x805060		493b6610		CMPQ SP, 0x10(R14)										
  checker.go:17310	0x805064		0f86d3000000		JBE 0x80513d											
  checker.go:17310	0x80506a		55			PUSHQ BP											
  checker.go:17310	0x80506b		4889e5			MOVQ SP, BP											
  checker.go:17310	0x80506e		4883ec18		SUBQ $0x18, SP											
  keybuilder.go:70	0x805072		4889442428		MOVQ AX, 0x28(SP)										
  keybuilder.go:70	0x805077		48894c2438		MOVQ CX, 0x38(SP)										
  keybuilder.go:70	0x80507c		48895c2430		MOVQ BX, 0x30(SP)										
  keybuilder.go:70	0x805081		488b9080000000		MOVQ 0x80(AX), DX										
  checker.go:17311	0x805088		90			NOPL												
  keybuilder.go:70	0x805089		4883fa78		CMPQ DX, $0x78											
  keybuilder.go:70	0x80508d		7f1b			JG 0x8050aa											
  keybuilder.go:71	0x80508f		4881fa80000000		CMPQ DX, $0x80											
  keybuilder.go:71	0x805096		0f8794000000		JA 0x805130											
  binary.go:124		0x80509c		48890c10		MOVQ CX, 0(AX)(DX*1)										
  keybuilder.go:72	0x8050a0		4883808000000008	ADDQ $0x8, 0x80(AX)										
  keybuilder.go:72	0x8050a8		eb17			JMP 0x8050c1											
  keybuilder.go:74	0x8050aa		4889cb			MOVQ CX, BX											
  keybuilder.go:74	0x8050ad		e80e8d0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB)	
  keybuilder.go:61	0x8050b2		488b442428		MOVQ 0x28(SP), AX										
  checker.go:17312	0x8050b7		488b4c2438		MOVQ 0x38(SP), CX										
  checker.go:17312	0x8050bc		488b5c2430		MOVQ 0x30(SP), BX										
  checker.go:17299	0x8050c1		31d2			XORL DX, DX											
  checker.go:17312	0x8050c3		eb03			JMP 0x8050c8											
  checker.go:17312	0x8050c5		48ffc2			INCQ DX												
  checker.go:17312	0x8050c8		4839d1			CMPQ CX, DX											
  checker.go:17312	0x8050cb		7e51			JLE 0x80511e											
  checker.go:17312	0x8050cd		488b34d3		MOVQ 0(BX)(DX*8), SI										
  keybuilder.go:61	0x8050d1		488bb880000000		MOVQ 0x80(AX), DI										
  checker.go:17313	0x8050d8		90			NOPL												
  checker.go:17307	0x8050d9		8b7608			MOVL 0x8(SI), SI										
  checker.go:17307	0x8050dc		0f1f4000		NOPL 0(AX)											
  keybuilder.go:61	0x8050e0		4883ff7c		CMPQ DI, $0x7c											
  keybuilder.go:61	0x8050e4		7f16			JG 0x8050fc											
  keybuilder.go:62	0x8050e6		4881ff80000000		CMPQ DI, $0x80											
  keybuilder.go:62	0x8050ed		7735			JA 0x805124											
  binary.go:98		0x8050ef		893438			MOVL SI, 0(AX)(DI*1)										
  keybuilder.go:63	0x8050f2		4883808000000004	ADDQ $0x4, 0x80(AX)										
  keybuilder.go:63	0x8050fa		ebc9			JMP 0x8050c5											
  checker.go:17312	0x8050fc		4889542410		MOVQ DX, 0x10(SP)										
  keybuilder.go:65	0x805101		89f3			MOVL SI, BX											
  keybuilder.go:65	0x805103		e8588c0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)	
  keybuilder.go:61	0x805108		488b442428		MOVQ 0x28(SP), AX										
  checker.go:17312	0x80510d		488b4c2438		MOVQ 0x38(SP), CX										
  checker.go:17312	0x805112		488b542410		MOVQ 0x10(SP), DX										
  checker.go:17312	0x805117		488b5c2430		MOVQ 0x30(SP), BX										
  keybuilder.go:65	0x80511c		eba7			JMP 0x8050c5											
  checker.go:17315	0x80511e		4883c418		ADDQ $0x18, SP											
  checker.go:17315	0x805122		5d			POPQ BP												
  checker.go:17315	0x805123		c3			RET												
  keybuilder.go:62	0x805124		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:62	0x80512b		e870c7c8ff		CALL runtime.panicBounds(SB)									
  keybuilder.go:71	0x805130		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:71	0x805137		e864c7c8ff		CALL runtime.panicBounds(SB)									
  keybuilder.go:71	0x80513c		90			NOPL												
  checker.go:17310	0x80513d		4889442408		MOVQ AX, 0x8(SP)										
  checker.go:17310	0x805142		48895c2410		MOVQ BX, 0x10(SP)										
  checker.go:17310	0x805147		48894c2418		MOVQ CX, 0x18(SP)										
  checker.go:17310	0x80514c		48897c2420		MOVQ DI, 0x20(SP)										
  checker.go:17310	0x805151		e8aaa8c8ff		CALL runtime.morestack_noctxt.abi0(SB)								
  checker.go:17310	0x805156		488b442408		MOVQ 0x8(SP), AX										
  checker.go:17310	0x80515b		488b5c2410		MOVQ 0x10(SP), BX										
  checker.go:17310	0x805160		488b4c2418		MOVQ 0x18(SP), CX										
  checker.go:17310	0x805165		488b7c2420		MOVQ 0x20(SP), DI										
  checker.go:17310	0x80516a		e9f1feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17317	0x805180		493b6610		CMPQ SP, 0x10(R14)										
  checker.go:17317	0x805184		0f86c8000000		JBE 0x805252											
  checker.go:17317	0x80518a		55			PUSHQ BP											
  checker.go:17317	0x80518b		4889e5			MOVQ SP, BP											
  checker.go:17317	0x80518e		4883ec20		SUBQ $0x20, SP											
  checker.go:17318	0x805192		4885db			TESTQ BX, BX											
  checker.go:17318	0x805195		7470			JE 0x805207											
  checker.go:17318	0x805197		4889442430		MOVQ AX, 0x30(SP)										
  checker.go:17318	0x80519c		48895c2438		MOVQ BX, 0x38(SP)										
  keybuilder.go:52	0x8051a1		488b8880000000		MOVQ 0x80(AX), CX										
  checker.go:17319	0x8051a8		90			NOPL												
  keybuilder.go:52	0x8051a9		4883f97f		CMPQ CX, $0x7f											
  keybuilder.go:52	0x8051ad		7f1a			JG 0x8051c9											
  keybuilder.go:53	0x8051af		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:53	0x8051b6		0f8389000000		JAE 0x805245											
  keybuilder.go:53	0x8051bc		c6040801		MOVB $0x1, 0(AX)(CX*1)										
  keybuilder.go:54	0x8051c0		48ff8080000000		INCQ 0x80(AX)											
  keybuilder.go:54	0x8051c7		eb14			JMP 0x8051dd											
  keybuilder.go:56	0x8051c9		bb01000000		MOVL $0x1, BX											
  keybuilder.go:56	0x8051ce		e82d8b0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	
  checker.go:17320	0x8051d3		488b442430		MOVQ 0x30(SP), AX										
  checker.go:17320	0x8051d8		488b5c2438		MOVQ 0x38(SP), BX										
  checker.go:17320	0x8051dd		488b1b			MOVQ 0(BX), BX											
  checker.go:17320	0x8051e0		e8bbfdffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeSymbol(SB)		
  checker.go:17321	0x8051e5		488b4c2438		MOVQ 0x38(SP), CX										
  checker.go:17321	0x8051ea		488b5908		MOVQ 0x8(CX), BX										
  checker.go:17321	0x8051ee		488b5110		MOVQ 0x10(CX), DX										
  checker.go:17321	0x8051f2		488b7918		MOVQ 0x18(CX), DI										
  checker.go:17321	0x8051f6		488b442430		MOVQ 0x30(SP), AX										
  checker.go:17321	0x8051fb		4889d1			MOVQ DX, CX											
  checker.go:17321	0x8051fe		6690			NOPW												
  checker.go:17321	0x805200		e85bfeffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)		
  checker.go:17321	0x805205		eb2b			JMP 0x805232											
  keybuilder.go:52	0x805207		488b8880000000		MOVQ 0x80(AX), CX										
  checker.go:17323	0x80520e		90			NOPL												
  keybuilder.go:52	0x80520f		4883f97f		CMPQ CX, $0x7f											
  keybuilder.go:52	0x805213		7f16			JG 0x80522b											
  keybuilder.go:53	0x805215		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:53	0x80521c		731a			JAE 0x805238											
  keybuilder.go:53	0x80521e		c6040800		MOVB $0x0, 0(AX)(CX*1)										
  keybuilder.go:54	0x805222		48ff8080000000		INCQ 0x80(AX)											
  keybuilder.go:54	0x805229		eb07			JMP 0x805232											
  keybuilder.go:56	0x80522b		31db			XORL BX, BX											
  keybuilder.go:56	0x80522d		e8ce8a0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	
  checker.go:17325	0x805232		4883c420		ADDQ $0x20, SP											
  checker.go:17325	0x805236		5d			POPQ BP												
  checker.go:17325	0x805237		c3			RET												
  keybuilder.go:53	0x805238		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:53	0x80523f		90			NOPL												
  keybuilder.go:53	0x805240		e85bc6c8ff		CALL runtime.panicBounds(SB)									
  keybuilder.go:53	0x805245		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:53	0x80524c		e84fc6c8ff		CALL runtime.panicBounds(SB)									
  keybuilder.go:53	0x805251		90			NOPL												
  checker.go:17317	0x805252		4889442408		MOVQ AX, 0x8(SP)										
  checker.go:17317	0x805257		48895c2410		MOVQ BX, 0x10(SP)										
  checker.go:17317	0x80525c		0f1f4000		NOPL 0(AX)											
  checker.go:17317	0x805260		e89ba7c8ff		CALL runtime.morestack_noctxt.abi0(SB)								
  checker.go:17317	0x805265		488b442408		MOVQ 0x8(SP), AX										
  checker.go:17317	0x80526a		488b5c2410		MOVQ 0x10(SP), BX										
  checker.go:17317	0x80526f		e90cffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)		
