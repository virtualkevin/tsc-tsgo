TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16409	0x800640		493b6610		CMPQ SP, 0x10(R14)												
  checker.go:16409	0x800644		0f86ce000000		JBE 0x800718													
  checker.go:16409	0x80064a		55			PUSHQ BP													
  checker.go:16409	0x80064b		4889e5			MOVQ SP, BP													
  checker.go:16409	0x80064e		4883ec10		SUBQ $0x10, SP													
  checker.go:16410	0x800652		8b4b04			MOVL 0x4(BX), CX												
  checker.go:16410	0x800655		0fbae110		BTL $0x10, CX													
  checker.go:16410	0x800659		0f82ae000000		JB 0x80070d													
  checker.go:16413	0x80065f		0fbae100		BTL $0x0, CX													
  checker.go:16413	0x800663		0f8299000000		JB 0x800702													
  checker.go:16416	0x800669		0fbae112		BTL $0x12, CX													
  checker.go:16416	0x80066d		0f8284000000		JB 0x8006f7													
  checker.go:16419	0x800673		0fbae10d		BTL $0xd, CX													
  checker.go:16419	0x800677		7273			JB 0x8006ec													
  checker.go:16422	0x800679		8b0b			MOVL 0(BX), CX													
  checker.go:16422	0x80067b		0f1f440000		NOPL 0(AX)(AX*1)												
  checker.go:16422	0x800680		f7c100800100		TESTL $0x18000, CX												
  checker.go:16422	0x800686		7559			JNE 0x8006e1													
  checker.go:16425	0x800688		f7c107000000		TESTL $0x7, CX													
  checker.go:16425	0x80068e		7546			JNE 0x8006d6													
  checker.go:16428	0x800690		f7c1b0230000		TESTL $0x23b0, CX												
  checker.go:16428	0x800696		7533			JNE 0x8006cb													
  checker.go:16431	0x800698		0fbae103		BTL $0x3, CX													
  checker.go:16431	0x80069c		7222			JB 0x8006c0													
  checker.go:16434	0x80069e		0fbae115		BTL $0x15, CX													
  checker.go:16434	0x8006a2		730b			JAE 0x8006af													
  checker.go:16435	0x8006a4		e8d7ce0000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAlias(SB)				
  checker.go:16435	0x8006a9		4883c410		ADDQ $0x10, SP													
  checker.go:16435	0x8006ad		5d			POPQ BP														
  checker.go:16435	0x8006ae		c3			RET														
  checker.go:16437	0x8006af		8400			TESTB AL, 0(AX)													
  checker.go:16437	0x8006b1		488b8068130000		MOVQ 0x1368(AX), AX												
  checker.go:16437	0x8006b8		4883c410		ADDQ $0x10, SP													
  checker.go:16437	0x8006bc		5d			POPQ BP														
  checker.go:16437	0x8006bd		c3			RET														
  checker.go:16437	0x8006be		6690			NOPW														
  checker.go:16432	0x8006c0		e8fbc20000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfEnumMember(SB)			
  checker.go:16432	0x8006c5		4883c410		ADDQ $0x10, SP													
  checker.go:16432	0x8006c9		5d			POPQ BP														
  checker.go:16432	0x8006ca		c3			RET														
  checker.go:16429	0x8006cb		e8b0220000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfFuncClassEnumModule(SB)		
  checker.go:16429	0x8006d0		4883c410		ADDQ $0x10, SP													
  checker.go:16429	0x8006d4		5d			POPQ BP														
  checker.go:16429	0x8006d5		c3			RET														
  checker.go:16426	0x8006d6		e885020000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfVariableOrParameterOrProperty(SB)	
  checker.go:16426	0x8006db		4883c410		ADDQ $0x10, SP													
  checker.go:16426	0x8006df		5d			POPQ BP														
  checker.go:16426	0x8006e0		c3			RET														
  checker.go:16423	0x8006e1		e89ac30000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAccessors(SB)			
  checker.go:16423	0x8006e6		4883c410		ADDQ $0x10, SP													
  checker.go:16423	0x8006ea		5d			POPQ BP														
  checker.go:16423	0x8006eb		c3			RET														
  checker.go:16420	0x8006ec		e8af110900		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfReverseMappedSymbol(SB)		
  checker.go:16420	0x8006f1		4883c410		ADDQ $0x10, SP													
  checker.go:16420	0x8006f5		5d			POPQ BP														
  checker.go:16420	0x8006f6		c3			RET														
  checker.go:16417	0x8006f7		e8e4c20100		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfMappedSymbol(SB)			
  checker.go:16417	0x8006fc		4883c410		ADDQ $0x10, SP													
  checker.go:16417	0x800700		5d			POPQ BP														
  checker.go:16417	0x800701		c3			RET														
  checker.go:16414	0x800702		e899000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)		
  checker.go:16414	0x800707		4883c410		ADDQ $0x10, SP													
  checker.go:16414	0x80070b		5d			POPQ BP														
  checker.go:16414	0x80070c		c3			RET														
  checker.go:16411	0x80070d		e86ef7ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbolWithDeferredType(SB)		
  checker.go:16411	0x800712		4883c410		ADDQ $0x10, SP													
  checker.go:16411	0x800716		5d			POPQ BP														
  checker.go:16411	0x800717		c3			RET														
  checker.go:16409	0x800718		4889442408		MOVQ AX, 0x8(SP)												
  checker.go:16409	0x80071d		48895c2410		MOVQ BX, 0x10(SP)												
  checker.go:16409	0x800722		e8d9f2c8ff		CALL runtime.morestack_noctxt.abi0(SB)										
  checker.go:16409	0x800727		488b442408		MOVQ 0x8(SP), AX												
  checker.go:16409	0x80072c		488b5c2410		MOVQ 0x10(SP), BX												
  checker.go:16409	0x800731		e90affffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)				
