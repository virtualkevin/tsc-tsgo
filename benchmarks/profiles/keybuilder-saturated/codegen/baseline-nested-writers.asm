TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17310	0x805020		493b6610		CMPQ SP, 0x10(R14)									
  checker.go:17310	0x805024		7658			JBE 0x80507e										
  checker.go:17310	0x805026		55			PUSHQ BP										
  checker.go:17310	0x805027		4889e5			MOVQ SP, BP										
  checker.go:17310	0x80502a		4883ec18		SUBQ $0x18, SP										
  checker.go:17312	0x80502e		4889442428		MOVQ AX, 0x28(SP)									
  checker.go:17312	0x805033		48894c2438		MOVQ CX, 0x38(SP)									
  checker.go:17312	0x805038		48895c2430		MOVQ BX, 0x30(SP)									
  checker.go:17311	0x80503d		90			NOPL											
  checker.go:17299	0x80503e		4889cb			MOVQ CX, BX										
  checker.go:17299	0x805041		e89a810900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64(SB)	
  checker.go:17299	0x805046		31c0			XORL AX, AX										
  checker.go:17312	0x805048		eb24			JMP 0x80506e										
  checker.go:17312	0x80504a		4889442410		MOVQ AX, 0x10(SP)									
  checker.go:17312	0x80504f		488b4c2430		MOVQ 0x30(SP), CX									
  checker.go:17312	0x805054		488b0cc1		MOVQ 0(CX)(AX*8), CX									
  checker.go:17307	0x805058		8b5908			MOVL 0x8(CX), BX									
  checker.go:17313	0x80505b		90			NOPL											
  checker.go:17307	0x80505c		488b442428		MOVQ 0x28(SP), AX									
  checker.go:17307	0x805061		e8fa800900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)	
  checker.go:17312	0x805066		488b442410		MOVQ 0x10(SP), AX									
  checker.go:17312	0x80506b		48ffc0			INCQ AX											
  checker.go:17312	0x80506e		488b4c2438		MOVQ 0x38(SP), CX									
  checker.go:17312	0x805073		4839c1			CMPQ CX, AX										
  checker.go:17312	0x805076		7fd2			JG 0x80504a										
  checker.go:17315	0x805078		4883c418		ADDQ $0x18, SP										
  checker.go:17315	0x80507c		5d			POPQ BP											
  checker.go:17315	0x80507d		c3			RET											
  checker.go:17310	0x80507e		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17310	0x805083		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17310	0x805088		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17310	0x80508d		48897c2420		MOVQ DI, 0x20(SP)									
  checker.go:17310	0x805092		e869a9c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17310	0x805097		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17310	0x80509c		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17310	0x8050a1		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17310	0x8050a6		488b7c2420		MOVQ 0x20(SP), DI									
  checker.go:17310	0x8050ab		e970ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17317	0x8050c0		493b6610		CMPQ SP, 0x10(R14)									
  checker.go:17317	0x8050c4		7665			JBE 0x80512b										
  checker.go:17317	0x8050c6		55			PUSHQ BP										
  checker.go:17317	0x8050c7		4889e5			MOVQ SP, BP										
  checker.go:17317	0x8050ca		4883ec20		SUBQ $0x20, SP										
  checker.go:17318	0x8050ce		4885db			TESTQ BX, BX										
  checker.go:17318	0x8050d1		7446			JE 0x805119										
  checker.go:17318	0x8050d3		4889442430		MOVQ AX, 0x30(SP)									
  checker.go:17318	0x8050d8		48895c2438		MOVQ BX, 0x38(SP)									
  checker.go:17319	0x8050dd		bb01000000		MOVL $0x1, BX										
  checker.go:17319	0x8050e2		e8f97f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)	
  checker.go:17320	0x8050e7		488b4c2438		MOVQ 0x38(SP), CX									
  checker.go:17320	0x8050ec		488b19			MOVQ 0(CX), BX										
  checker.go:17320	0x8050ef		488b442430		MOVQ 0x30(SP), AX									
  checker.go:17320	0x8050f4		e8a7feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeSymbol(SB)	
  checker.go:17321	0x8050f9		488b4c2438		MOVQ 0x38(SP), CX									
  checker.go:17321	0x8050fe		488b5908		MOVQ 0x8(CX), BX									
  checker.go:17321	0x805102		488b5110		MOVQ 0x10(CX), DX									
  checker.go:17321	0x805106		488b7918		MOVQ 0x18(CX), DI									
  checker.go:17321	0x80510a		488b442430		MOVQ 0x30(SP), AX									
  checker.go:17321	0x80510f		4889d1			MOVQ DX, CX										
  checker.go:17321	0x805112		e809ffffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17321	0x805117		eb0c			JMP 0x805125										
  checker.go:17323	0x805119		31db			XORL BX, BX										
  checker.go:17323	0x80511b		0f1f440000		NOPL 0(AX)(AX*1)									
  checker.go:17323	0x805120		e8bb7f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)	
  checker.go:17325	0x805125		4883c420		ADDQ $0x20, SP										
  checker.go:17325	0x805129		5d			POPQ BP											
  checker.go:17325	0x80512a		c3			RET											
  checker.go:17317	0x80512b		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17317	0x805130		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17317	0x805135		e8c6a8c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17317	0x80513a		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17317	0x80513f		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17317	0x805144		e977ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)	
