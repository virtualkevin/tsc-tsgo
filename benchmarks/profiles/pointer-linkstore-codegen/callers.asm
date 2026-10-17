TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:16409	0x800260		493b6610		CMPQ SP, 0x10(R14)												
  checker.go:16409	0x800264		0f86ce000000		JBE 0x800338													
  checker.go:16409	0x80026a		55			PUSHQ BP													
  checker.go:16409	0x80026b		4889e5			MOVQ SP, BP													
  checker.go:16409	0x80026e		4883ec10		SUBQ $0x10, SP													
  checker.go:16410	0x800272		8b4b04			MOVL 0x4(BX), CX												
  checker.go:16410	0x800275		0fbae110		BTL $0x10, CX													
  checker.go:16410	0x800279		0f82ae000000		JB 0x80032d													
  checker.go:16413	0x80027f		0fbae100		BTL $0x0, CX													
  checker.go:16413	0x800283		0f8299000000		JB 0x800322													
  checker.go:16416	0x800289		0fbae112		BTL $0x12, CX													
  checker.go:16416	0x80028d		0f8284000000		JB 0x800317													
  checker.go:16419	0x800293		0fbae10d		BTL $0xd, CX													
  checker.go:16419	0x800297		7273			JB 0x80030c													
  checker.go:16422	0x800299		8b0b			MOVL 0(BX), CX													
  checker.go:16422	0x80029b		0f1f440000		NOPL 0(AX)(AX*1)												
  checker.go:16422	0x8002a0		f7c100800100		TESTL $0x18000, CX												
  checker.go:16422	0x8002a6		7559			JNE 0x800301													
  checker.go:16425	0x8002a8		f7c107000000		TESTL $0x7, CX													
  checker.go:16425	0x8002ae		7546			JNE 0x8002f6													
  checker.go:16428	0x8002b0		f7c1b0230000		TESTL $0x23b0, CX												
  checker.go:16428	0x8002b6		7533			JNE 0x8002eb													
  checker.go:16431	0x8002b8		0fbae103		BTL $0x3, CX													
  checker.go:16431	0x8002bc		7222			JB 0x8002e0													
  checker.go:16434	0x8002be		0fbae115		BTL $0x15, CX													
  checker.go:16434	0x8002c2		730b			JAE 0x8002cf													
  checker.go:16435	0x8002c4		e877c60000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAlias(SB)				
  checker.go:16435	0x8002c9		4883c410		ADDQ $0x10, SP													
  checker.go:16435	0x8002cd		5d			POPQ BP														
  checker.go:16435	0x8002ce		c3			RET														
  checker.go:16437	0x8002cf		488b80480b0000		MOVQ 0xb48(AX), AX												
  checker.go:16437	0x8002d6		4883c410		ADDQ $0x10, SP													
  checker.go:16437	0x8002da		5d			POPQ BP														
  checker.go:16437	0x8002db		c3			RET														
  checker.go:16437	0x8002dc		0f1f4000		NOPL 0(AX)													
  checker.go:16432	0x8002e0		e8dbba0000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfEnumMember(SB)			
  checker.go:16432	0x8002e5		4883c410		ADDQ $0x10, SP													
  checker.go:16432	0x8002e9		5d			POPQ BP														
  checker.go:16432	0x8002ea		c3			RET														
  checker.go:16429	0x8002eb		e850220000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfFuncClassEnumModule(SB)		
  checker.go:16429	0x8002f0		4883c410		ADDQ $0x10, SP													
  checker.go:16429	0x8002f4		5d			POPQ BP														
  checker.go:16429	0x8002f5		c3			RET														
  checker.go:16426	0x8002f6		e845020000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfVariableOrParameterOrProperty(SB)	
  checker.go:16426	0x8002fb		4883c410		ADDQ $0x10, SP													
  checker.go:16426	0x8002ff		5d			POPQ BP														
  checker.go:16426	0x800300		c3			RET														
  checker.go:16423	0x800301		e85abb0000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfAccessors(SB)			
  checker.go:16423	0x800306		4883c410		ADDQ $0x10, SP													
  checker.go:16423	0x80030a		5d			POPQ BP														
  checker.go:16423	0x80030b		c3			RET														
  checker.go:16420	0x80030c		e86f020900		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfReverseMappedSymbol(SB)		
  checker.go:16420	0x800311		4883c410		ADDQ $0x10, SP													
  checker.go:16420	0x800315		5d			POPQ BP														
  checker.go:16420	0x800316		c3			RET														
  checker.go:16417	0x800317		e8a4b90100		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfMappedSymbol(SB)			
  checker.go:16417	0x80031c		4883c410		ADDQ $0x10, SP													
  checker.go:16417	0x800320		5d			POPQ BP														
  checker.go:16417	0x800321		c3			RET														
  checker.go:16414	0x800322		e899000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfInstantiatedSymbol(SB)		
  checker.go:16414	0x800327		4883c410		ADDQ $0x10, SP													
  checker.go:16414	0x80032b		5d			POPQ BP														
  checker.go:16414	0x80032c		c3			RET														
  checker.go:16411	0x80032d		e88ef7ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbolWithDeferredType(SB)		
  checker.go:16411	0x800332		4883c410		ADDQ $0x10, SP													
  checker.go:16411	0x800336		5d			POPQ BP														
  checker.go:16411	0x800337		c3			RET														
  checker.go:16409	0x800338		4889442408		MOVQ AX, 0x8(SP)												
  checker.go:16409	0x80033d		48895c2410		MOVQ BX, 0x10(SP)												
  checker.go:16409	0x800342		e8b9f6c8ff		CALL runtime.morestack_noctxt.abi0(SB)										
  checker.go:16409	0x800347		488b442408		MOVQ 0x8(SP), AX												
  checker.go:16409	0x80034c		488b5c2410		MOVQ 0x10(SP), BX												
  checker.go:16409	0x800351		e90affffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)				

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateSymbol(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:20669	0x81a160		493b6610		CMPQ SP, 0x10(R14)																											
  checker.go:20669	0x81a164		0f8689000000		JBE 0x81a1f3																												
  checker.go:20669	0x81a16a		55			PUSHQ BP																												
  checker.go:20669	0x81a16b		4889e5			MOVQ SP, BP																												
  checker.go:20669	0x81a16e		4883ec28		SUBQ $0x28, SP																												
  checker.go:20670	0x81a172		4885db			TESTQ BX, BX																												
  checker.go:20670	0x81a175		7474			JE 0x81a1eb																												
  checker.go:20670	0x81a177		4889442438		MOVQ AX, 0x38(SP)																											
  checker.go:20670	0x81a17c		48895c2440		MOVQ BX, 0x40(SP)																											
  checker.go:20670	0x81a181		48894c2448		MOVQ CX, 0x48(SP)																											
  checker.go:20673	0x81a186		8400			TESTB AL, 0(AX)																												
  checker.go:20673	0x81a188		4805f8080000		ADDQ $0x8f8, AX																												
  checker.go:20673	0x81a18e		4889d9			MOVQ BX, CX																												
  checker.go:20673	0x81a191		488d1da8ffd200		LEAQ github.com/microsoft/typescript-go/internal/core..dict.PointerLinkStore[github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX			
  checker.go:20673	0x81a198		e8039d0e00		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)	
  checker.go:20673	0x81a19d		4889442420		MOVQ AX, 0x20(SP)																											
  checker.go:20674	0x81a1a2		488b5c2440		MOVQ 0x40(SP), BX																											
  checker.go:20674	0x81a1a7		488b4c2448		MOVQ 0x48(SP), CX																											
  checker.go:20674	0x81a1ac		4889c7			MOVQ AX, DI																												
  checker.go:20674	0x81a1af		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:20674	0x81a1b4		e8e7000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).keepsSymbolLinksUnderInstantiation(SB)																
  checker.go:20674	0x81a1b9		84c0			TESTL AL, AL																												
  checker.go:20674	0x81a1bb		740b			JE 0x81a1c8																												
  checker.go:20675	0x81a1bd		488b442440		MOVQ 0x40(SP), AX																											
  checker.go:20675	0x81a1c2		4883c428		ADDQ $0x28, SP																												
  checker.go:20675	0x81a1c6		5d			POPQ BP																													
  checker.go:20675	0x81a1c7		c3			RET																													
  checker.go:20677	0x81a1c8		488b442438		MOVQ 0x38(SP), AX																											
  checker.go:20677	0x81a1cd		488b5c2440		MOVQ 0x40(SP), BX																											
  checker.go:20677	0x81a1d2		488b4c2448		MOVQ 0x48(SP), CX																											
  checker.go:20677	0x81a1d7		488b7c2420		MOVQ 0x20(SP), DI																											
  checker.go:20677	0x81a1dc		0f1f4000		NOPL 0(AX)																												
  checker.go:20677	0x81a1e0		e85b020000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).newInstantiatedSymbolWithLinks(SB)																	
  checker.go:20677	0x81a1e5		4883c428		ADDQ $0x28, SP																												
  checker.go:20677	0x81a1e9		5d			POPQ BP																													
  checker.go:20677	0x81a1ea		c3			RET																													
  checker.go:20671	0x81a1eb		31c0			XORL AX, AX																												
  checker.go:20671	0x81a1ed		4883c428		ADDQ $0x28, SP																												
  checker.go:20671	0x81a1f1		5d			POPQ BP																													
  checker.go:20671	0x81a1f2		c3			RET																													
  checker.go:20669	0x81a1f3		4889442408		MOVQ AX, 0x8(SP)																											
  checker.go:20669	0x81a1f8		48895c2410		MOVQ BX, 0x10(SP)																											
  checker.go:20669	0x81a1fd		48894c2418		MOVQ CX, 0x18(SP)																											
  checker.go:20669	0x81a202		e8f957c7ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  checker.go:20669	0x81a207		488b442408		MOVQ 0x8(SP), AX																											
  checker.go:20669	0x81a20c		488b5c2410		MOVQ 0x10(SP), BX																											
  checker.go:20669	0x81a211		488b4c2418		MOVQ 0x18(SP), CX																											
  checker.go:20669	0x81a216		e945ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateSymbol(SB)																		

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newInstantiatedSymbolWithLinks(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:20706	0x81a440		493b6610		CMPQ SP, 0x10(R14)																											
  checker.go:20706	0x81a444		0f86f3010000		JBE 0x81a63d																												
  checker.go:20706	0x81a44a		55			PUSHQ BP																												
  checker.go:20706	0x81a44b		4889e5			MOVQ SP, BP																												
  checker.go:20706	0x81a44e		4883ec40		SUBQ $0x40, SP																												
  checker.go:20707	0x81a452		4889442450		MOVQ AX, 0x50(SP)																											
  checker.go:20707	0x81a457		48897c2468		MOVQ DI, 0x68(SP)																											
  checker.go:20707	0x81a45c		8b5304			MOVL 0x4(BX), DX																											
  checker.go:20707	0x81a45f		0fbae200		BTL $0x0, DX																												
  checker.go:20707	0x81a463		0f8396000000		JAE 0x81a4ff																												
  checker.go:20711	0x81a469		488b5718		MOVQ 0x18(DI), DX																											
  checker.go:20711	0x81a46d		488b7710		MOVQ 0x10(DI), SI																											
  mapper.go:48		0x81a471		4885d2			TESTQ DX, DX																												
  mapper.go:48		0x81a474		0f8488000000		JE 0x81a502																												
  checker.go:20707	0x81a47a		48894c2460		MOVQ CX, 0x60(SP)																											
  checker.go:20711	0x81a47f		4889742438		MOVQ SI, 0x38(SP)																											
  checker.go:20711	0x81a484		4889542428		MOVQ DX, 0x28(SP)																											
  mapper.go:49		0x81a489		90			NOPL																													
  mapper.go:267		0x81a48a		488d054f006500		LEAQ 0x65004f(IP), AX																											
  mapper.go:267		0x81a491		e8aa9ac0ff		CALL runtime.newobject(SB)																										
  mapper.go:268		0x81a496		488d0d2330d100		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.CompositeTypeMapper,github.com/microsoft/typescript-go/internal/checker.TypeMapperData(SB), CX									
  mapper.go:268		0x81a49d		488908			MOVQ CX, 0(AX)																												
  mapper.go:268		0x81a4a0		833d69a06d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  mapper.go:268		0x81a4a7		7511			JNE 0x81a4ba																												
  mapper.go:269		0x81a4a9		488b542450		MOVQ 0x50(SP), DX																											
  mapper.go:270		0x81a4ae		488b742428		MOVQ 0x28(SP), SI																											
  mapper.go:271		0x81a4b3		4c8b442460		MOVQ 0x60(SP), R8																											
  mapper.go:268		0x81a4b8		eb23			JMP 0x81a4dd																												
  mapper.go:268		0x81a4ba		e88170c7ff		CALL runtime.gcWriteBarrier4(SB)																									
  mapper.go:268		0x81a4bf		498903			MOVQ AX, 0(R11)																												
  mapper.go:269		0x81a4c2		488b542450		MOVQ 0x50(SP), DX																											
  mapper.go:269		0x81a4c7		49895308		MOVQ DX, 0x8(R11)																											
  mapper.go:270		0x81a4cb		488b742428		MOVQ 0x28(SP), SI																											
  mapper.go:270		0x81a4d0		49897310		MOVQ SI, 0x10(R11)																											
  mapper.go:271		0x81a4d4		4c8b442460		MOVQ 0x60(SP), R8																											
  mapper.go:271		0x81a4d9		4d894318		MOVQ R8, 0x18(R11)																											
  mapper.go:268		0x81a4dd		48894008		MOVQ AX, 0x8(AX)																											
  mapper.go:269		0x81a4e1		48895010		MOVQ DX, 0x10(AX)																											
  mapper.go:270		0x81a4e5		48897018		MOVQ SI, 0x18(AX)																											
  mapper.go:271		0x81a4e9		4c894020		MOVQ R8, 0x20(AX)																											
  checker.go:20716	0x81a4ed		488b742438		MOVQ 0x38(SP), SI																											
  checker.go:20726	0x81a4f2		488b7c2468		MOVQ 0x68(SP), DI																											
  checker.go:20712	0x81a4f7		4889c1			MOVQ AX, CX																												
  checker.go:20716	0x81a4fa		4889d0			MOVQ DX, AX																												
  checker.go:20712	0x81a4fd		eb03			JMP 0x81a502																												
  checker.go:20716	0x81a4ff		4889de			MOVQ BX, SI																												
  checker.go:20716	0x81a502		4889742438		MOVQ SI, 0x38(SP)																											
  checker.go:20716	0x81a507		48894c2430		MOVQ CX, 0x30(SP)																											
  checker.go:20716	0x81a50c		8b1e			MOVL 0(SI), BX																												
  checker.go:20716	0x81a50e		488b4e08		MOVQ 0x8(SI), CX																											
  checker.go:20716	0x81a512		488b7e10		MOVQ 0x10(SI), DI																											
  checker.go:20716	0x81a516		e8a573fdff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).newSymbol(SB)																			
  checker.go:20717	0x81a51b		488b542438		MOVQ 0x38(SP), DX																											
  checker.go:20717	0x81a520		8b7204			MOVL 0x4(DX), SI																											
  checker.go:20717	0x81a523		81e608d00000		ANDL $0xd008, SI																											
  checker.go:20717	0x81a529		83ce01			ORL $0x1, SI																												
  checker.go:20717	0x81a52c		897004			MOVL SI, 0x4(AX)																											
  checker.go:20718	0x81a52f		488b7220		MOVQ 0x20(DX), SI																											
  checker.go:20718	0x81a533		4c8b4228		MOVQ 0x28(DX), R8																											
  checker.go:20718	0x81a537		4c8b4a18		MOVQ 0x18(DX), R9																											
  checker.go:20718	0x81a53b		48897020		MOVQ SI, 0x20(AX)																											
  checker.go:20718	0x81a53f		4c894028		MOVQ R8, 0x28(AX)																											
  checker.go:20718	0x81a543		833dc69f6d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:20718	0x81a54a		7410			JE 0x81a55c																												
  checker.go:20718	0x81a54c		488b7018		MOVQ 0x18(AX), SI																											
  checker.go:20718	0x81a550		e8ab6fc7ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:20718	0x81a555		4d890b			MOVQ R9, 0(R11)																												
  checker.go:20718	0x81a558		49897308		MOVQ SI, 0x8(R11)																											
  checker.go:20718	0x81a55c		4c894818		MOVQ R9, 0x18(AX)																											
  checker.go:20719	0x81a560		488b7250		MOVQ 0x50(DX), SI																											
  checker.go:20719	0x81a564		833da59f6d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:20719	0x81a56b		7410			JE 0x81a57d																												
  checker.go:20719	0x81a56d		488b7850		MOVQ 0x50(AX), DI																											
  checker.go:20719	0x81a571		e88a6fc7ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:20719	0x81a576		498933			MOVQ SI, 0(R11)																												
  checker.go:20719	0x81a579		49897b08		MOVQ DI, 0x8(R11)																											
  checker.go:20719	0x81a57d		48897050		MOVQ SI, 0x50(AX)																											
  checker.go:20720	0x81a581		488b7230		MOVQ 0x30(DX), SI																											
  checker.go:20720	0x81a585		833d849f6d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:20720	0x81a58c		7410			JE 0x81a59e																												
  checker.go:20720	0x81a58e		488b7830		MOVQ 0x30(AX), DI																											
  checker.go:20720	0x81a592		e8696fc7ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:20720	0x81a597		498933			MOVQ SI, 0(R11)																												
  checker.go:20720	0x81a59a		49897b08		MOVQ DI, 0x8(R11)																											
  checker.go:20716	0x81a59e		4889442420		MOVQ AX, 0x20(SP)																											
  checker.go:20720	0x81a5a3		48897030		MOVQ SI, 0x30(AX)																											
  checker.go:20723	0x81a5a7		488b542450		MOVQ 0x50(SP), DX																											
  checker.go:20723	0x81a5ac		8402			TESTB AL, 0(DX)																												
  checker.go:20723	0x81a5ae		4881c2f8080000		ADDQ $0x8f8, DX																												
  checker.go:20723	0x81a5b5		488d1d84fbd200		LEAQ github.com/microsoft/typescript-go/internal/core..dict.PointerLinkStore[github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX			
  checker.go:20723	0x81a5bc		4889c1			MOVQ AX, CX																												
  checker.go:20723	0x81a5bf		4889d0			MOVQ DX, AX																												
  checker.go:20723	0x81a5c2		e859980e00		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB)	
  checker.go:20724	0x81a5c7		8400			TESTB AL, 0(AX)																												
  checker.go:20724	0x81a5c9		833d409f6d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:20724	0x81a5d0		750c			JNE 0x81a5de																												
  checker.go:20725	0x81a5d2		488b4c2430		MOVQ 0x30(SP), CX																											
  checker.go:20724	0x81a5d7		488b5c2438		MOVQ 0x38(SP), BX																											
  checker.go:20724	0x81a5dc		eb26			JMP 0x81a604																												
  checker.go:20724	0x81a5de		488b4810		MOVQ 0x10(AX), CX																											
  checker.go:20725	0x81a5e2		488b5018		MOVQ 0x18(AX), DX																											
  checker.go:20724	0x81a5e6		e8556fc7ff		CALL runtime.gcWriteBarrier4(SB)																									
  checker.go:20724	0x81a5eb		488b5c2438		MOVQ 0x38(SP), BX																											
  checker.go:20724	0x81a5f0		49891b			MOVQ BX, 0(R11)																												
  checker.go:20724	0x81a5f3		49894b08		MOVQ CX, 0x8(R11)																											
  checker.go:20725	0x81a5f7		488b4c2430		MOVQ 0x30(SP), CX																											
  checker.go:20725	0x81a5fc		49894b10		MOVQ CX, 0x10(R11)																											
  checker.go:20725	0x81a600		49895318		MOVQ DX, 0x18(R11)																											
  checker.go:20724	0x81a604		48895810		MOVQ BX, 0x10(AX)																											
  checker.go:20725	0x81a608		48894818		MOVQ CX, 0x18(AX)																											
  checker.go:20726	0x81a60c		488b4c2468		MOVQ 0x68(SP), CX																											
  checker.go:20726	0x81a611		488b4920		MOVQ 0x20(CX), CX																											
  checker.go:20726	0x81a615		833df49e6d0100		CMPL runtime.writeBarrier(SB), $0x0																									
  checker.go:20726	0x81a61c		7410			JE 0x81a62e																												
  checker.go:20726	0x81a61e		488b5020		MOVQ 0x20(AX), DX																											
  checker.go:20726	0x81a622		e8d96ec7ff		CALL runtime.gcWriteBarrier2(SB)																									
  checker.go:20726	0x81a627		49890b			MOVQ CX, 0(R11)																												
  checker.go:20726	0x81a62a		49895308		MOVQ DX, 0x8(R11)																											
  checker.go:20726	0x81a62e		48894820		MOVQ CX, 0x20(AX)																											
  checker.go:20727	0x81a632		488b442420		MOVQ 0x20(SP), AX																											
  checker.go:20727	0x81a637		4883c440		ADDQ $0x40, SP																												
  checker.go:20727	0x81a63b		5d			POPQ BP																													
  checker.go:20727	0x81a63c		c3			RET																													
  checker.go:20706	0x81a63d		4889442408		MOVQ AX, 0x8(SP)																											
  checker.go:20706	0x81a642		48895c2410		MOVQ BX, 0x10(SP)																											
  checker.go:20706	0x81a647		48894c2418		MOVQ CX, 0x18(SP)																											
  checker.go:20706	0x81a64c		48897c2420		MOVQ DI, 0x20(SP)																											
  checker.go:20706	0x81a651		e8aa53c7ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  checker.go:20706	0x81a656		488b442408		MOVQ 0x8(SP), AX																											
  checker.go:20706	0x81a65b		488b5c2410		MOVQ 0x10(SP), BX																											
  checker.go:20706	0x81a660		488b4c2418		MOVQ 0x18(SP), CX																											
  checker.go:20706	0x81a665		488b7c2420		MOVQ 0x20(SP), DI																											
  checker.go:20706	0x81a66a		e9d1fdffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newInstantiatedSymbolWithLinks(SB)																	
