TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16409	0x800500		493b6610		CMPQ SP, 0x10(R14)												
  checker.go:16409	0x800504		0f86ce000000		JBE 0x8005d8													
  checker.go:16409	0x80050a		55			PUSHQ BP													
  checker.go:16409	0x80050b		4889e5			MOVQ SP, BP													
  checker.go:16409	0x80050e		4883ec10		SUBQ $0x10, SP													
  checker.go:16410	0x800512		8b4b04			MOVL 0x4(BX), CX												
  checker.go:16410	0x800515		0fbae110		BTL $0x10, CX													
  checker.go:16410	0x800519		0f82ae000000		JB 0x8005cd													
  checker.go:16413	0x80051f		0fbae100		BTL $0x0, CX													
  checker.go:16413	0x800523		0f8299000000		JB 0x8005c2													
  checker.go:16416	0x800529		0fbae112		BTL $0x12, CX													
  checker.go:16416	0x80052d		0f8284000000		JB 0x8005b7													
  checker.go:16419	0x800533		0fbae10d		BTL $0xd, CX													
  checker.go:16419	0x800537		7273			JB 0x8005ac													
  checker.go:16422	0x800539		8b0b			MOVL 0(BX), CX													
  checker.go:16422	0x80053b		0f1f440000		NOPL 0(AX)(AX*1)												
  checker.go:16422	0x800540		f7c100800100		TESTL $0x18000, CX												
  checker.go:16422	0x800546		7559			JNE 0x8005a1													
  checker.go:16425	0x800548		f7c107000000		TESTL $0x7, CX													
  checker.go:16425	0x80054e		7546			JNE 0x800596													
  checker.go:16428	0x800550		f7c1b0230000		TESTL $0x23b0, CX												
  checker.go:16428	0x800556		7533			JNE 0x80058b													
  checker.go:16431	0x800558		0fbae103		BTL $0x3, CX													
  checker.go:16431	0x80055c		7222			JB 0x800580													
  checker.go:16434	0x80055e		0fbae115		BTL $0x15, CX													
  checker.go:16434	0x800562		730b			JAE 0x80056f													
  checker.go:16435	0x800564		e8d7cd0000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAlias(SB)				
  checker.go:16435	0x800569		4883c410		ADDQ $0x10, SP													
  checker.go:16435	0x80056d		5d			POPQ BP														
  checker.go:16435	0x80056e		c3			RET														
  checker.go:16437	0x80056f		488b80500b0000		MOVQ 0xb50(AX), AX												
  checker.go:16437	0x800576		4883c410		ADDQ $0x10, SP													
  checker.go:16437	0x80057a		5d			POPQ BP														
  checker.go:16437	0x80057b		c3			RET														
  checker.go:16437	0x80057c		0f1f4000		NOPL 0(AX)													
  checker.go:16432	0x800580		e83bc20000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfEnumMember(SB)			
  checker.go:16432	0x800585		4883c410		ADDQ $0x10, SP													
  checker.go:16432	0x800589		5d			POPQ BP														
  checker.go:16432	0x80058a		c3			RET														
  checker.go:16429	0x80058b		e850220000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfFuncClassEnumModule(SB)		
  checker.go:16429	0x800590		4883c410		ADDQ $0x10, SP													
  checker.go:16429	0x800594		5d			POPQ BP														
  checker.go:16429	0x800595		c3			RET														
  checker.go:16426	0x800596		e845020000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfVariableOrParameterOrProperty(SB)	
  checker.go:16426	0x80059b		4883c410		ADDQ $0x10, SP													
  checker.go:16426	0x80059f		5d			POPQ BP														
  checker.go:16426	0x8005a0		c3			RET														
  checker.go:16423	0x8005a1		e8bac20000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAccessors(SB)			
  checker.go:16423	0x8005a6		4883c410		ADDQ $0x10, SP													
  checker.go:16423	0x8005aa		5d			POPQ BP														
  checker.go:16423	0x8005ab		c3			RET														
  checker.go:16420	0x8005ac		e8cf0b0900		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfReverseMappedSymbol(SB)		
  checker.go:16420	0x8005b1		4883c410		ADDQ $0x10, SP													
  checker.go:16420	0x8005b5		5d			POPQ BP														
  checker.go:16420	0x8005b6		c3			RET														
  checker.go:16417	0x8005b7		e804c10100		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfMappedSymbol(SB)			
  checker.go:16417	0x8005bc		4883c410		ADDQ $0x10, SP													
  checker.go:16417	0x8005c0		5d			POPQ BP														
  checker.go:16417	0x8005c1		c3			RET														
  checker.go:16414	0x8005c2		e899000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)		
  checker.go:16414	0x8005c7		4883c410		ADDQ $0x10, SP													
  checker.go:16414	0x8005cb		5d			POPQ BP														
  checker.go:16414	0x8005cc		c3			RET														
  checker.go:16411	0x8005cd		e88ef7ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbolWithDeferredType(SB)		
  checker.go:16411	0x8005d2		4883c410		ADDQ $0x10, SP													
  checker.go:16411	0x8005d6		5d			POPQ BP														
  checker.go:16411	0x8005d7		c3			RET														
  checker.go:16409	0x8005d8		4889442408		MOVQ AX, 0x8(SP)												
  checker.go:16409	0x8005dd		48895c2410		MOVQ BX, 0x10(SP)												
  checker.go:16409	0x8005e2		e819f4c8ff		CALL runtime.morestack_noctxt.abi0(SB)										
  checker.go:16409	0x8005e7		488b442408		MOVQ 0x8(SP), AX												
  checker.go:16409	0x8005ec		488b5c2410		MOVQ 0x10(SP), BX												
  checker.go:16409	0x8005f1		e90affffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)				
