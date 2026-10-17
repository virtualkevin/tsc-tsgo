TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17540	0x8062c0		493b6610		CMPQ SP, 0x10(R14)											
  checker.go:17540	0x8062c4		0f86f3000000		JBE 0x8063bd												
  checker.go:17540	0x8062ca		55			PUSHQ BP												
  checker.go:17540	0x8062cb		4889e5			MOVQ SP, BP												
  checker.go:17540	0x8062ce		4883ec30		SUBQ $0x30, SP												
  checker.go:17541	0x8062d2		4889442440		MOVQ AX, 0x40(SP)											
  checker.go:17541	0x8062d7		897c2458		MOVL DI, 0x58(SP)											
  checker.go:17541	0x8062db		448844245d		MOVB R8, 0x5d(SP)											
  checker.go:17541	0x8062e0		4084f6			TESTL SI, SI												
  checker.go:17541	0x8062e3		7413			JE 0x8062f8												
  checker.go:17541	0x8062e5		8b5308			MOVL 0x8(BX), DX											
  checker.go:17541	0x8062e8		395108			CMPL 0x8(CX), DX											
  checker.go:17541	0x8062eb		7214			JB 0x806301												
  checker.go:17546	0x8062ed		4889ca			MOVQ CX, DX												
  checker.go:17546	0x8062f0		4889d9			MOVQ BX, CX												
  checker.go:17546	0x8062f3		4889d3			MOVQ DX, BX												
  checker.go:17541	0x8062f6		eb09			JMP 0x806301												
  checker.go:17546	0x8062f8		4889ca			MOVQ CX, DX												
  checker.go:17546	0x8062fb		4889d9			MOVQ BX, CX												
  checker.go:17546	0x8062fe		4889d3			MOVQ DX, BX												
  checker.go:17546	0x806301		48894c2428		MOVQ CX, 0x28(SP)											
  checker.go:17546	0x806306		48895c2420		MOVQ BX, 0x20(SP)											
  checker.go:17546	0x80630b		4889c8			MOVQ CX, AX												
  checker.go:17546	0x80630e		e8ad030000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17546	0x806313		84c0			TESTL AL, AL												
  checker.go:17546	0x806315		7504			JNE 0x80631b												
  checker.go:17546	0x806317		31c0			XORL AX, AX												
  checker.go:17546	0x806319		eb0a			JMP 0x806325												
  checker.go:17546	0x80631b		488b442420		MOVQ 0x20(SP), AX											
  checker.go:17546	0x806320		e89b030000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17546	0x806325		84c0			TESTL AL, AL												
  checker.go:17547	0x806327		7410			JE 0x806339												
  checker.go:17550	0x806329		488b4c2420		MOVQ 0x20(SP), CX											
  checker.go:17550	0x80632e		488b5c2428		MOVQ 0x28(SP), BX											
  checker.go:17550	0x806333		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17547	0x806337		eb6c			JMP 0x8063a5												
  checker.go:17547	0x806339		488b5c2428		MOVQ 0x28(SP), BX											
  checker.go:17547	0x80633e		8b5308			MOVL 0x8(BX), DX											
  checker.go:17547	0x806341		85d2			TESTL DX, DX												
  checker.go:17547	0x806343		7457			JE 0x80639c												
  checker.go:17547	0x806345		488b4c2420		MOVQ 0x20(SP), CX											
  checker.go:17547	0x80634a		448b4908		MOVL 0x8(CX), R9											
  checker.go:17547	0x80634e		4585c9			TESTL R9, R9												
  checker.go:17547	0x806351		7443			JE 0x806396												
  checker.go:17547	0x806353		81fa00000040		CMPL DX, $0x40000000											
  checker.go:17547	0x806359		7335			JAE 0x806390												
  checker.go:17547	0x80635b		0f1f440000		NOPL 0(AX)(AX*1)											
  checker.go:17547	0x806360		4181f900000040		CMPL R9, $0x40000000											
  checker.go:17547	0x806367		7321			JAE 0x80638a												
  checker.go:17547	0x806369		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17547	0x80636d		83ff03			CMPL DI, $0x3												
  checker.go:17547	0x806370		7733			JA 0x8063a5												
  checker.go:17548	0x806372		48c1e220		SHLQ $0x20, DX												
  checker.go:17548	0x806376		49c1e102		SHLQ $0x2, R9												
  checker.go:17548	0x80637a		4909d1			ORQ DX, R9												
  checker.go:17548	0x80637d		89f8			MOVL DI, AX												
  checker.go:17548	0x80637f		4c09c8			ORQ R9, AX												
  checker.go:17548	0x806382		31db			XORL BX, BX												
  checker.go:17548	0x806384		4883c430		ADDQ $0x30, SP												
  checker.go:17548	0x806388		5d			POPQ BP													
  checker.go:17548	0x806389		c3			RET													
  checker.go:17550	0x80638a		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17547	0x80638e		eb15			JMP 0x8063a5												
  checker.go:17550	0x806390		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17547	0x806394		eb0f			JMP 0x8063a5												
  checker.go:17550	0x806396		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17547	0x80639a		eb09			JMP 0x8063a5												
  checker.go:17550	0x80639c		488b4c2420		MOVQ 0x20(SP), CX											
  checker.go:17550	0x8063a1		8b7c2458		MOVL 0x58(SP), DI											
  checker.go:17550	0x8063a5		89c6			MOVL AX, SI												
  checker.go:17550	0x8063a7		440fb644245d		MOVZX 0x5d(SP), R8											
  checker.go:17550	0x8063ad		488b442440		MOVQ 0x40(SP), AX											
  checker.go:17550	0x8063b2		e869000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getHashedRelationKey(SB)		
  checker.go:17550	0x8063b7		4883c430		ADDQ $0x30, SP												
  checker.go:17550	0x8063bb		5d			POPQ BP													
  checker.go:17550	0x8063bc		c3			RET													
  checker.go:17540	0x8063bd		4889442408		MOVQ AX, 0x8(SP)											
  checker.go:17540	0x8063c2		48895c2410		MOVQ BX, 0x10(SP)											
  checker.go:17540	0x8063c7		48894c2418		MOVQ CX, 0x18(SP)											
  checker.go:17540	0x8063cc		897c2420		MOVL DI, 0x20(SP)											
  checker.go:17540	0x8063d0		4088742424		MOVB SI, 0x24(SP)											
  checker.go:17540	0x8063d5		4488442425		MOVB R8, 0x25(SP)											
  checker.go:17540	0x8063da		e82196c8ff		CALL runtime.morestack_noctxt.abi0(SB)									
  checker.go:17540	0x8063df		488b442408		MOVQ 0x8(SP), AX											
  checker.go:17540	0x8063e4		488b5c2410		MOVQ 0x10(SP), BX											
  checker.go:17540	0x8063e9		488b4c2418		MOVQ 0x18(SP), CX											
  checker.go:17540	0x8063ee		8b7c2420		MOVL 0x20(SP), DI											
  checker.go:17540	0x8063f2		0fb6742424		MOVZX 0x24(SP), SI											
  checker.go:17540	0x8063f7		440fb6442425		MOVZX 0x25(SP), R8											
  checker.go:17540	0x8063fd		0f1f00			NOPL 0(AX)												
  checker.go:17540	0x806400		e9bbfeffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getRelationKey(SB)			

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getHashedRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17554	0x806420		4c8da42488fbffff	LEAQ 0xfffffb88(SP), R12																	
  checker.go:17554	0x806428		4d3b6610		CMPQ R12, 0x10(R14)																		
  checker.go:17554	0x80642c		0f8641020000		JBE 0x806673																			
  checker.go:17554	0x806432		55			PUSHQ BP																			
  checker.go:17554	0x806433		4889e5			MOVQ SP, BP																			
  checker.go:17554	0x806436		4881ecf0040000		SUBQ $0x4f0, SP																			
  checker.go:17557	0x80643d		4889842400050000	MOVQ AX, 0x500(SP)																		
  checker.go:17557	0x806445		48899c2408050000	MOVQ BX, 0x508(SP)																		
  checker.go:17557	0x80644d		48898c2410050000	MOVQ CX, 0x510(SP)																		
  checker.go:17557	0x806455		89bc2418050000		MOVL DI, 0x518(SP)																		
  checker.go:17555	0x80645c		488d542450		LEAQ 0x50(SP), DX																		
  checker.go:17555	0x806461		41b912000000		MOVL $0x12, R9																			
  checker.go:17555	0x806467		440f113a		MOVUPS X15, 0(DX)																		
  checker.go:17555	0x80646b		440f117a10		MOVUPS X15, 0x10(DX)																		
  checker.go:17555	0x806470		440f117a20		MOVUPS X15, 0x20(DX)																		
  checker.go:17555	0x806475		440f117a30		MOVUPS X15, 0x30(DX)																		
  checker.go:17555	0x80647a		4883c240		ADDQ $0x40, DX																			
  checker.go:17555	0x80647e		6690			NOPW																				
  checker.go:17555	0x806480		41ffc9			DECL R9																				
  checker.go:17555	0x806483		75e2			JNE 0x806467																			
  checker.go:17555	0x806485		440f113a		MOVUPS X15, 0(DX)																		
  checker.go:17555	0x806489		440f117a10		MOVUPS X15, 0x10(DX)																		
  checker.go:17557	0x80648e		4084f6			TESTL SI, SI																			
  checker.go:17557	0x806491		7447			JE 0x8064da																			
  checker.go:17557	0x806493		448884241d050000	MOVB R8, 0x51d(SP)																		
  checker.go:17558	0x80649b		90			NOPL																				
  checker.go:17333	0x80649c		c644242767		MOVB $0x67, 0x27(SP)																		
  hasher.go:90		0x8064a1		90			NOPL																				
  hasher.go:103		0x8064a2		488d442450		LEAQ 0x50(SP), AX																		
  hasher.go:103		0x8064a7		488d5c2427		LEAQ 0x27(SP), BX																		
  hasher.go:103		0x8064ac		b901000000		MOVL $0x1, CX																			
  hasher.go:103		0x8064b1		e8caded9ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)														
  checker.go:17559	0x8064b6		488d442450		LEAQ 0x50(SP), AX																		
  checker.go:17559	0x8064bb		488b9c2408050000	MOVQ 0x508(SP), BX																		
  checker.go:17559	0x8064c3		488b8c2410050000	MOVQ 0x510(SP), CX																		
  checker.go:17559	0x8064cb		0fb6bc241d050000	MOVZX 0x51d(SP), DI																		
  checker.go:17559	0x8064d3		e8e8ecffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeGenericTypeReferences(SB)								
  checker.go:17559	0x8064d8		eb57			JMP 0x806531																			
  checker.go:17561	0x8064da		90			NOPL																				
  checker.go:17333	0x8064db		c644242673		MOVB $0x73, 0x26(SP)																		
  hasher.go:90		0x8064e0		90			NOPL																				
  hasher.go:103		0x8064e1		488d442450		LEAQ 0x50(SP), AX																		
  hasher.go:103		0x8064e6		488d5c2426		LEAQ 0x26(SP), BX																		
  hasher.go:103		0x8064eb		b901000000		MOVL $0x1, CX																			
  hasher.go:103		0x8064f0		e88bded9ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)														
  checker.go:17349	0x8064f5		488b942408050000	MOVQ 0x508(SP), DX																		
  checker.go:17349	0x8064fd		8b4a08			MOVL 0x8(DX), CX																		
  checker.go:17562	0x806500		90			NOPL																				
  checker.go:17349	0x806501		488d05a8d7d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.TypeId](SB), AX			
  checker.go:17349	0x806508		488d5c2450		LEAQ 0x50(SP), BX																		
  checker.go:17349	0x80650d		e80e2e1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17349	0x806512		488b942410050000	MOVQ 0x510(SP), DX																		
  checker.go:17349	0x80651a		8b4a08			MOVL 0x8(DX), CX																		
  checker.go:17563	0x80651d		90			NOPL																				
  checker.go:17349	0x80651e		488d058bd7d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.TypeId](SB), AX			
  checker.go:17349	0x806525		488d5c2450		LEAQ 0x50(SP), BX																		
  checker.go:17349	0x80652a		e8f12d1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17349	0x80652f		31c0			XORL AX, AX																			
  checker.go:17565	0x806531		88442425		MOVB AL, 0x25(SP)																		
  checker.go:17565	0x806535		488d0524d8d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.IntersectionState](SB), AX	
  checker.go:17565	0x80653c		488d5c2450		LEAQ 0x50(SP), BX																		
  checker.go:17565	0x806541		8b8c2418050000		MOVL 0x518(SP), CX																		
  checker.go:17565	0x806548		e8d32d1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17329	0x80654d		488d442450		LEAQ 0x50(SP), AX																		
  checker.go:17329	0x806552		e809e5d9ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)															
  checker.go:17329	0x806557		4889442438		MOVQ AX, 0x38(SP)																		
  checker.go:17329	0x80655c		48895c2430		MOVQ BX, 0x30(SP)																		
  checker.go:17570	0x806561		4889442440		MOVQ AX, 0x40(SP)																		
  checker.go:17570	0x806566		48895c2448		MOVQ BX, 0x48(SP)																		
  checker.go:17570	0x80656b		488b942400050000	MOVQ 0x500(SP), DX																		
  checker.go:17570	0x806573		488b9ac00f0000		MOVQ 0xfc0(DX), BX																		
  checker.go:17570	0x80657a		488d05bf1a5c00		LEAQ 0x5c1abf(IP), AX																		
  checker.go:17570	0x806581		488d4c2440		LEAQ 0x40(SP), CX																		
  checker.go:17570	0x806586		e895b7c0ff		CALL runtime.mapaccess1(SB)																	
  checker.go:17570	0x80658b		488b10			MOVQ 0(AX), DX																			
  checker.go:17570	0x80658e		4885d2			TESTQ DX, DX																			
  checker.go:17570	0x806591		0f85b7000000		JNE 0x80664e																			
  checker.go:17573	0x806597		48baffffffffffffff7f	MOVQ $0x7fffffffffffffff, DX																	
  checker.go:17573	0x8065a1		488bb42400050000	MOVQ 0x500(SP), SI																		
  checker.go:17573	0x8065a9		483996c80f0000		CMPQ 0xfc8(SI), DX																		
  checker.go:17573	0x8065b0		0f84a9000000		JE 0x80665f																			
  checker.go:17576	0x8065b6		4883bec00f000000	CMPQ 0xfc0(SI), $0x0																		
  checker.go:17576	0x8065be		6690			NOPW																				
  checker.go:17576	0x8065c0		753d			JNE 0x8065ff																			
  checker.go:17577	0x8065c2		e8f916c8ff		CALL runtime.makemap_small(SB)																	
  checker.go:17577	0x8065c7		833d42df6e0100		CMPL runtime.writeBarrier(SB), $0x0																
  checker.go:17577	0x8065ce		750a			JNE 0x8065da																			
  checker.go:17577	0x8065d0		488b942400050000	MOVQ 0x500(SP), DX																		
  checker.go:17577	0x8065d8		eb1b			JMP 0x8065f5																			
  checker.go:17577	0x8065da		488b942400050000	MOVQ 0x500(SP), DX																		
  checker.go:17577	0x8065e2		488bb2c00f0000		MOVQ 0xfc0(DX), SI																		
  checker.go:17577	0x8065e9		e812afc8ff		CALL runtime.gcWriteBarrier2(SB)																
  checker.go:17577	0x8065ee		498903			MOVQ AX, 0(R11)																			
  checker.go:17577	0x8065f1		49897308		MOVQ SI, 0x8(R11)																		
  checker.go:17577	0x8065f5		488982c00f0000		MOVQ AX, 0xfc0(DX)																		
  checker.go:17579	0x8065fc		4889d6			MOVQ DX, SI																			
  checker.go:17579	0x8065ff		488b96c80f0000		MOVQ 0xfc8(SI), DX																		
  checker.go:17579	0x806606		48ffc2			INCQ DX																				
  checker.go:17579	0x806609		488996c80f0000		MOVQ DX, 0xfc8(SI)																		
  checker.go:17581	0x806610		488b7c2438		MOVQ 0x38(SP), DI																		
  checker.go:17581	0x806615		48897c2440		MOVQ DI, 0x40(SP)																		
  checker.go:17581	0x80661a		488b7c2430		MOVQ 0x30(SP), DI																		
  checker.go:17581	0x80661f		48897c2448		MOVQ DI, 0x48(SP)																		
  checker.go:17580	0x806624		480fbaea3f		BTSQ $0x3f, DX																			
  checker.go:17580	0x806629		4889542428		MOVQ DX, 0x28(SP)																		
  checker.go:17581	0x80662e		488b9ec00f0000		MOVQ 0xfc0(SI), BX																		
  checker.go:17581	0x806635		488d05041a5c00		LEAQ 0x5c1a04(IP), AX																		
  checker.go:17581	0x80663c		488d4c2440		LEAQ 0x40(SP), CX																		
  checker.go:17581	0x806641		e89abcc0ff		CALL runtime.mapassign(SB)																	
  checker.go:17581	0x806646		488b542428		MOVQ 0x28(SP), DX																		
  checker.go:17581	0x80664b		488910			MOVQ DX, 0(AX)																			
  checker.go:17566	0x80664e		4889d0			MOVQ DX, AX																			
  checker.go:17566	0x806651		0fb65c2425		MOVZX 0x25(SP), BX																		
  checker.go:17566	0x806656		4881c4f0040000		ADDQ $0x4f0, SP																			
  checker.go:17566	0x80665d		5d			POPQ BP																				
  checker.go:17566	0x80665e		c3			RET																				
  checker.go:17574	0x80665f		488d055a915500		LEAQ 0x55915a(IP), AX																		
  checker.go:17574	0x806666		488d1de3d0d100		LEAQ 0xd1d0e3(IP), BX																		
  checker.go:17574	0x80666d		e82e34c8ff		CALL runtime.gopanic(SB)																	
  checker.go:17574	0x806672		90			NOPL																				
  checker.go:17554	0x806673		4889442408		MOVQ AX, 0x8(SP)																		
  checker.go:17554	0x806678		48895c2410		MOVQ BX, 0x10(SP)																		
  checker.go:17554	0x80667d		48894c2418		MOVQ CX, 0x18(SP)																		
  checker.go:17554	0x806682		897c2420		MOVL DI, 0x20(SP)																		
  checker.go:17554	0x806686		4088742424		MOVB SI, 0x24(SP)																		
  checker.go:17554	0x80668b		4488442425		MOVB R8, 0x25(SP)																		
  checker.go:17554	0x806690		e86b93c8ff		CALL runtime.morestack_noctxt.abi0(SB)																
  checker.go:17554	0x806695		488b442408		MOVQ 0x8(SP), AX																		
  checker.go:17554	0x80669a		488b5c2410		MOVQ 0x10(SP), BX																		
  checker.go:17554	0x80669f		488b4c2418		MOVQ 0x18(SP), CX																		
  checker.go:17554	0x8066a4		8b7c2420		MOVL 0x20(SP), DI																		
  checker.go:17554	0x8066a8		0fb6742424		MOVZX 0x24(SP), SI																		
  checker.go:17554	0x8066ad		440fb6442425		MOVZX 0x25(SP), R8																		
  checker.go:17554	0x8066b3		e968fdffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getHashedRelationKey(SB)									
