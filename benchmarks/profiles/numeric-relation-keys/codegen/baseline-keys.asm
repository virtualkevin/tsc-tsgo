TEXT github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17529	0x8062c0		4c8da424a0fbffff	LEAQ 0xfffffba0(SP), R12																	
  checker.go:17529	0x8062c8		4d3b6610		CMPQ R12, 0x10(R14)																		
  checker.go:17529	0x8062cc		0f8650010000		JBE 0x806422																			
  checker.go:17529	0x8062d2		55			PUSHQ BP																			
  checker.go:17529	0x8062d3		4889e5			MOVQ SP, BP																			
  checker.go:17529	0x8062d6		4881ecd8040000		SUBQ $0x4d8, SP																			
  checker.go:17530	0x8062dd		898c24f8040000		MOVL CX, 0x4f8(SP)																		
  checker.go:17530	0x8062e4		4088b424fd040000	MOVB SI, 0x4fd(SP)																		
  checker.go:17530	0x8062ec		4084ff			TESTL DI, DI																			
  checker.go:17530	0x8062ef		7413			JE 0x806304																			
  checker.go:17530	0x8062f1		8b5008			MOVL 0x8(AX), DX																		
  checker.go:17530	0x8062f4		395308			CMPL 0x8(BX), DX																		
  checker.go:17530	0x8062f7		7214			JB 0x80630d																			
  checker.go:17533	0x8062f9		4889da			MOVQ BX, DX																			
  checker.go:17533	0x8062fc		4889c3			MOVQ AX, BX																			
  checker.go:17533	0x8062ff		4889d0			MOVQ DX, AX																			
  checker.go:17530	0x806302		eb09			JMP 0x80630d																			
  checker.go:17533	0x806304		4889da			MOVQ BX, DX																			
  checker.go:17533	0x806307		4889c3			MOVQ AX, BX																			
  checker.go:17533	0x80630a		4889d0			MOVQ DX, AX																			
  checker.go:17533	0x80630d		48895c2430		MOVQ BX, 0x30(SP)																		
  checker.go:17533	0x806312		4889442428		MOVQ AX, 0x28(SP)																		
  checker.go:17533	0x806317		488d4c2438		LEAQ 0x38(SP), CX																		
  checker.go:17533	0x80631c		ba12000000		MOVL $0x12, DX																			
  checker.go:17533	0x806321		440f1139		MOVUPS X15, 0(CX)																		
  checker.go:17533	0x806325		440f117910		MOVUPS X15, 0x10(CX)																		
  checker.go:17533	0x80632a		440f117920		MOVUPS X15, 0x20(CX)																		
  checker.go:17533	0x80632f		440f117930		MOVUPS X15, 0x30(CX)																		
  checker.go:17533	0x806334		4883c140		ADDQ $0x40, CX																			
  checker.go:17533	0x806338		ffca			DECL DX																				
  checker.go:17533	0x80633a		75e5			JNE 0x806321																			
  checker.go:17533	0x80633c		440f1139		MOVUPS X15, 0(CX)																		
  checker.go:17533	0x806340		440f117910		MOVUPS X15, 0x10(CX)																		
  checker.go:17535	0x806345		4889d8			MOVQ BX, AX																			
  checker.go:17535	0x806348		e813010000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)								
  checker.go:17535	0x80634d		84c0			TESTL AL, AL																			
  checker.go:17535	0x80634f		7504			JNE 0x806355																			
  checker.go:17535	0x806351		31c0			XORL AX, AX																			
  checker.go:17535	0x806353		eb0b			JMP 0x806360																			
  checker.go:17535	0x806355		488b442428		MOVQ 0x28(SP), AX																		
  checker.go:17535	0x80635a		e801010000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)								
  checker.go:17535	0x80635f		90			NOPL																				
  checker.go:17535	0x806360		84c0			TESTL AL, AL																			
  checker.go:17535	0x806362		7439			JE 0x80639d																			
  checker.go:17536	0x806364		90			NOPL																				
  checker.go:17331	0x806365		c644242767		MOVB $0x67, 0x27(SP)																		
  hasher.go:90		0x80636a		90			NOPL																				
  hasher.go:103		0x80636b		488d442438		LEAQ 0x38(SP), AX																		
  hasher.go:103		0x806370		488d5c2427		LEAQ 0x27(SP), BX																		
  hasher.go:103		0x806375		b901000000		MOVL $0x1, CX																			
  hasher.go:103		0x80637a		e801e0d9ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)														
  checker.go:17537	0x80637f		488d442438		LEAQ 0x38(SP), AX																		
  checker.go:17537	0x806384		488b5c2430		MOVQ 0x30(SP), BX																		
  checker.go:17537	0x806389		488b4c2428		MOVQ 0x28(SP), CX																		
  checker.go:17537	0x80638e		0fb6bc24fd040000	MOVZX 0x4fd(SP), DI																		
  checker.go:17537	0x806396		e825eeffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeGenericTypeReferences(SB)								
  checker.go:17537	0x80639b		eb51			JMP 0x8063ee																			
  checker.go:17539	0x80639d		90			NOPL																				
  checker.go:17331	0x80639e		c644242673		MOVB $0x73, 0x26(SP)																		
  hasher.go:90		0x8063a3		90			NOPL																				
  hasher.go:103		0x8063a4		488d442438		LEAQ 0x38(SP), AX																		
  hasher.go:103		0x8063a9		488d5c2426		LEAQ 0x26(SP), BX																		
  hasher.go:103		0x8063ae		b901000000		MOVL $0x1, CX																			
  hasher.go:103		0x8063b3		e8c8dfd9ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)														
  checker.go:17347	0x8063b8		488b542430		MOVQ 0x30(SP), DX																		
  checker.go:17347	0x8063bd		8b4a08			MOVL 0x8(DX), CX																		
  checker.go:17540	0x8063c0		90			NOPL																				
  checker.go:17347	0x8063c1		488d05c8d5d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.TypeId](SB), AX			
  checker.go:17347	0x8063c8		488d5c2438		LEAQ 0x38(SP), BX																		
  checker.go:17347	0x8063cd		e86e2e1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17347	0x8063d2		488b542428		MOVQ 0x28(SP), DX																		
  checker.go:17347	0x8063d7		8b4a08			MOVL 0x8(DX), CX																		
  checker.go:17541	0x8063da		90			NOPL																				
  checker.go:17347	0x8063db		488d05aed5d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.TypeId](SB), AX			
  checker.go:17347	0x8063e2		488d5c2438		LEAQ 0x38(SP), BX																		
  checker.go:17347	0x8063e7		e8542e1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17347	0x8063ec		31c0			XORL AX, AX																			
  checker.go:17543	0x8063ee		88442425		MOVB AL, 0x25(SP)																		
  checker.go:17543	0x8063f2		488d0507d5d100		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.IntersectionState](SB), AX	
  checker.go:17543	0x8063f9		488d5c2438		LEAQ 0x38(SP), BX																		
  checker.go:17543	0x8063fe		8b8c24f8040000		MOVL 0x4f8(SP), CX																		
  checker.go:17543	0x806405		e8362e1000		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)									
  checker.go:17327	0x80640a		488d442438		LEAQ 0x38(SP), AX																		
  checker.go:17327	0x80640f		e84ce6d9ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)															
  checker.go:17544	0x806414		0fb64c2425		MOVZX 0x25(SP), CX																		
  checker.go:17544	0x806419		4881c4d8040000		ADDQ $0x4d8, SP																			
  checker.go:17544	0x806420		5d			POPQ BP																				
  checker.go:17544	0x806421		c3			RET																				
  checker.go:17529	0x806422		4889442408		MOVQ AX, 0x8(SP)																		
  checker.go:17529	0x806427		48895c2410		MOVQ BX, 0x10(SP)																		
  checker.go:17529	0x80642c		894c2418		MOVL CX, 0x18(SP)																		
  checker.go:17529	0x806430		40887c241c		MOVB DI, 0x1c(SP)																		
  checker.go:17529	0x806435		408874241d		MOVB SI, 0x1d(SP)																		
  checker.go:17529	0x80643a		e8c195c8ff		CALL runtime.morestack_noctxt.abi0(SB)																
  checker.go:17529	0x80643f		488b442408		MOVQ 0x8(SP), AX																		
  checker.go:17529	0x806444		488b5c2410		MOVQ 0x10(SP), BX																		
  checker.go:17529	0x806449		8b4c2418		MOVL 0x18(SP), CX																		
  checker.go:17529	0x80644d		0fb67c241c		MOVZX 0x1c(SP), DI																		
  checker.go:17529	0x806452		0fb674241d		MOVZX 0x1d(SP), SI																		
  checker.go:17529	0x806457		e964feffff		JMP github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)											
