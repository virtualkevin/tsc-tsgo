TEXT github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17372	0x805700		4c8d6424c8		LEAQ -0x38(SP), R12									
  checker.go:17372	0x805705		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17372	0x805709		766d			JBE 0x805778										
  checker.go:17372	0x80570b		55			PUSHQ BP										
  checker.go:17372	0x80570c		4889e5			MOVQ SP, BP										
  checker.go:17372	0x80570f		4881ecb0000000		SUBQ $0xb0, SP										
  checker.go:17372	0x805716		48898424c0000000	MOVQ AX, 0xc0(SP)									
  checker.go:17373	0x80571e		488d542420		LEAQ 0x20(SP), DX									
  checker.go:17373	0x805723		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17373	0x805727		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17373	0x80572c		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17373	0x805731		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17373	0x805736		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17373	0x80573b		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17373	0x805740		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17373	0x805745		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17373	0x80574a		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17374	0x805752		4889cf			MOVQ CX, DI										
  checker.go:17374	0x805755		4889d9			MOVQ BX, CX										
  checker.go:17374	0x805758		4889c3			MOVQ AX, BX										
  checker.go:17374	0x80575b		4889d0			MOVQ DX, AX										
  checker.go:17374	0x80575e		6690			NOPW											
  checker.go:17374	0x805760		e8dbf8ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17375	0x805765		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17375	0x80576a		e871790900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17375	0x80576f		4881c4b0000000		ADDQ $0xb0, SP										
  checker.go:17375	0x805776		5d			POPQ BP											
  checker.go:17375	0x805777		c3			RET											
  checker.go:17372	0x805778		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17372	0x80577d		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17372	0x805782		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17372	0x805787		e874a2c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17372	0x80578c		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17372	0x805791		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17372	0x805796		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17372	0x80579b		0f1f440000		NOPL 0(AX)(AX*1)									
  checker.go:17372	0x8057a0		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17456	0x805e00		4c8d6424b8		LEAQ -0x48(SP), R12									
  checker.go:17456	0x805e05		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17456	0x805e09		0f86e9000000		JBE 0x805ef8										
  checker.go:17456	0x805e0f		55			PUSHQ BP										
  checker.go:17456	0x805e10		4889e5			MOVQ SP, BP										
  checker.go:17456	0x805e13		4881ecc0000000		SUBQ $0xc0, SP										
  checker.go:17462	0x805e1a		48899c24d8000000	MOVQ BX, 0xd8(SP)									
  checker.go:17462	0x805e22		898c24e0000000		MOVL CX, 0xe0(SP)									
  checker.go:17462	0x805e29		4889bc24e8000000	MOVQ DI, 0xe8(SP)									
  checker.go:17457	0x805e31		488d542430		LEAQ 0x30(SP), DX									
  checker.go:17457	0x805e36		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17457	0x805e3a		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17457	0x805e3f		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17457	0x805e44		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17457	0x805e49		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17457	0x805e4e		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17457	0x805e53		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17457	0x805e58		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17457	0x805e5d		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17307	0x805e65		8b7008			MOVL 0x8(AX), SI									
  checker.go:17458	0x805e68		90			NOPL											
  keybuilder.go:60	0x805e69		90			NOPL											
  binary.go:98		0x805e6a		89742428		MOVL SI, 0x28(SP)									
  keybuilder.go:61	0x805e6e		4889d0			MOVQ DX, AX										
  keybuilder.go:61	0x805e71		488d5c2428		LEAQ 0x28(SP), BX									
  keybuilder.go:61	0x805e76		b904000000		MOVL $0x4, CX										
  keybuilder.go:61	0x805e7b		4889cf			MOVQ CX, DI										
  keybuilder.go:61	0x805e7e		6690			NOPW											
  keybuilder.go:61	0x805e80		e89b730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)	
  checker.go:17307	0x805e85		488b9424d8000000	MOVQ 0xd8(SP), DX									
  checker.go:17307	0x805e8d		8b5208			MOVL 0x8(DX), DX									
  checker.go:17459	0x805e90		90			NOPL											
  keybuilder.go:60	0x805e91		90			NOPL											
  binary.go:98		0x805e92		89542424		MOVL DX, 0x24(SP)									
  keybuilder.go:61	0x805e96		488d442430		LEAQ 0x30(SP), AX									
  keybuilder.go:61	0x805e9b		488d5c2424		LEAQ 0x24(SP), BX									
  keybuilder.go:61	0x805ea0		b904000000		MOVL $0x4, CX										
  keybuilder.go:61	0x805ea5		4889cf			MOVQ CX, DI										
  keybuilder.go:61	0x805ea8		e873730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)	
  checker.go:17460	0x805ead		90			NOPL											
  keybuilder.go:60	0x805eae		90			NOPL											
  binary.go:98		0x805eaf		8b9424e0000000		MOVL 0xe0(SP), DX									
  binary.go:98		0x805eb6		8954242c		MOVL DX, 0x2c(SP)									
  keybuilder.go:61	0x805eba		488d442430		LEAQ 0x30(SP), AX									
  keybuilder.go:61	0x805ebf		488d5c242c		LEAQ 0x2c(SP), BX									
  keybuilder.go:61	0x805ec4		b904000000		MOVL $0x4, CX										
  keybuilder.go:61	0x805ec9		4889cf			MOVQ CX, DI										
  keybuilder.go:61	0x805ecc		e84f730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)	
  checker.go:17461	0x805ed1		488d442430		LEAQ 0x30(SP), AX									
  checker.go:17461	0x805ed6		488b9c24e8000000	MOVQ 0xe8(SP), BX									
  checker.go:17461	0x805ede		6690			NOPW											
  checker.go:17461	0x805ee0		e81bf2ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)	
  checker.go:17462	0x805ee5		488d442430		LEAQ 0x30(SP), AX									
  checker.go:17462	0x805eea		e8f1710900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17462	0x805eef		4881c4c0000000		ADDQ $0xc0, SP										
  checker.go:17462	0x805ef6		5d			POPQ BP											
  checker.go:17462	0x805ef7		c3			RET											
  checker.go:17456	0x805ef8		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17456	0x805efd		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17456	0x805f02		894c2418		MOVL CX, 0x18(SP)									
  checker.go:17456	0x805f06		48897c2420		MOVQ DI, 0x20(SP)									
  checker.go:17456	0x805f0b		e8f09ac8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17456	0x805f10		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17456	0x805f15		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17456	0x805f1a		8b4c2418		MOVL 0x18(SP), CX									
  checker.go:17456	0x805f1e		488b7c2420		MOVQ 0x20(SP), DI									
  checker.go:17456	0x805f23		e9d8feffff		JMP github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17479	0x806100		4c8d6424c8		LEAQ -0x38(SP), R12									
  checker.go:17479	0x806105		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17479	0x806109		0f86a9000000		JBE 0x8061b8										
  checker.go:17479	0x80610f		55			PUSHQ BP										
  checker.go:17479	0x806110		4889e5			MOVQ SP, BP										
  checker.go:17479	0x806113		4881ecb0000000		SUBQ $0xb0, SP										
  checker.go:17479	0x80611a		48898424c0000000	MOVQ AX, 0xc0(SP)									
  checker.go:17483	0x806122		4889bc24d8000000	MOVQ DI, 0xd8(SP)									
  checker.go:17483	0x80612a		4088b424e0000000	MOVB SI, 0xe0(SP)									
  checker.go:17480	0x806132		488d542420		LEAQ 0x20(SP), DX									
  checker.go:17480	0x806137		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17480	0x80613b		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17480	0x806140		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17480	0x806145		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17480	0x80614a		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17480	0x80614f		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17480	0x806154		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17480	0x806159		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17480	0x80615e		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17481	0x806166		4889cf			MOVQ CX, DI										
  checker.go:17481	0x806169		4889d9			MOVQ BX, CX										
  checker.go:17481	0x80616c		4889c3			MOVQ AX, BX										
  checker.go:17481	0x80616f		4889d0			MOVQ DX, AX										
  checker.go:17481	0x806172		e8c9eeffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17482	0x806177		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17482	0x80617c		488b9c24d8000000	MOVQ 0xd8(SP), BX									
  checker.go:17482	0x806184		e877efffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)	
  checker.go:17483	0x806189		0fb69424e0000000	MOVZX 0xe0(SP), DX									
  checker.go:17483	0x806191		84d2			TESTL DL, DL										
  checker.go:17483	0x806193		7410			JE 0x8061a5										
  checker.go:17484	0x806195		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17484	0x80619a		bb21000000		MOVL $0x21, BX										
  checker.go:17484	0x80619f		90			NOPL											
  checker.go:17484	0x8061a0		e85b720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)	
  checker.go:17486	0x8061a5		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17486	0x8061aa		e8316f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17486	0x8061af		4881c4b0000000		ADDQ $0xb0, SP										
  checker.go:17486	0x8061b6		5d			POPQ BP											
  checker.go:17486	0x8061b7		c3			RET											
  checker.go:17479	0x8061b8		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17479	0x8061bd		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17479	0x8061c2		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17479	0x8061c7		48897c2420		MOVQ DI, 0x20(SP)									
  checker.go:17479	0x8061cc		4088742428		MOVB SI, 0x28(SP)									
  checker.go:17479	0x8061d1		e82a98c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17479	0x8061d6		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17479	0x8061db		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17479	0x8061e0		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17479	0x8061e5		488b7c2420		MOVQ 0x20(SP), DI									
  checker.go:17479	0x8061ea		0fb6742428		MOVZX 0x28(SP), SI									
  checker.go:17479	0x8061ef		e90cffffff		JMP github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17489	0x806200		4c8d6424a8		LEAQ -0x58(SP), R12											
  checker.go:17489	0x806205		4d3b6610		CMPQ R12, 0x10(R14)											
  checker.go:17489	0x806209		0f8664010000		JBE 0x806373												
  checker.go:17489	0x80620f		55			PUSHQ BP												
  checker.go:17489	0x806210		4889e5			MOVQ SP, BP												
  checker.go:17489	0x806213		4881ecd0000000		SUBQ $0xd0, SP												
  checker.go:17490	0x80621a		898c24f0000000		MOVL CX, 0xf0(SP)											
  checker.go:17490	0x806221		4088b424f5000000	MOVB SI, 0xf5(SP)											
  checker.go:17490	0x806229		4084ff			TESTL DI, DI												
  checker.go:17490	0x80622c		7414			JE 0x806242												
  checker.go:17490	0x80622e		8b5008			MOVL 0x8(AX), DX											
  checker.go:17490	0x806231		395308			CMPL 0x8(BX), DX											
  checker.go:17490	0x806234		7215			JB 0x80624b												
  checker.go:17493	0x806236		4889da			MOVQ BX, DX												
  checker.go:17493	0x806239		4889c3			MOVQ AX, BX												
  checker.go:17493	0x80623c		4889d0			MOVQ DX, AX												
  checker.go:17493	0x80623f		90			NOPL													
  checker.go:17490	0x806240		eb09			JMP 0x80624b												
  checker.go:17493	0x806242		4889da			MOVQ BX, DX												
  checker.go:17493	0x806245		4889c3			MOVQ AX, BX												
  checker.go:17493	0x806248		4889d0			MOVQ DX, AX												
  checker.go:17493	0x80624b		48895c2438		MOVQ BX, 0x38(SP)											
  checker.go:17493	0x806250		4889442430		MOVQ AX, 0x30(SP)											
  checker.go:17493	0x806255		488d4c2440		LEAQ 0x40(SP), CX											
  checker.go:17493	0x80625a		440f1139		MOVUPS X15, 0(CX)											
  checker.go:17493	0x80625e		440f117910		MOVUPS X15, 0x10(CX)											
  checker.go:17493	0x806263		440f117920		MOVUPS X15, 0x20(CX)											
  checker.go:17493	0x806268		440f117930		MOVUPS X15, 0x30(CX)											
  checker.go:17493	0x80626d		440f117940		MOVUPS X15, 0x40(CX)											
  checker.go:17493	0x806272		440f117950		MOVUPS X15, 0x50(CX)											
  checker.go:17493	0x806277		440f117960		MOVUPS X15, 0x60(CX)											
  checker.go:17493	0x80627c		440f117970		MOVUPS X15, 0x70(CX)											
  checker.go:17493	0x806281		440f11b980000000	MOVUPS X15, 0x80(CX)											
  checker.go:17495	0x806289		4889d8			MOVQ BX, AX												
  checker.go:17495	0x80628c		e82f010000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x806291		84c0			TESTL AL, AL												
  checker.go:17495	0x806293		7504			JNE 0x806299												
  checker.go:17495	0x806295		31c0			XORL AX, AX												
  checker.go:17495	0x806297		eb0c			JMP 0x8062a5												
  checker.go:17495	0x806299		488b442430		MOVQ 0x30(SP), AX											
  checker.go:17495	0x80629e		6690			NOPW													
  checker.go:17495	0x8062a0		e81b010000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x8062a5		84c0			TESTL AL, AL												
  checker.go:17495	0x8062a7		742d			JE 0x8062d6												
  checker.go:17496	0x8062a9		488d442440		LEAQ 0x40(SP), AX											
  checker.go:17496	0x8062ae		bb67000000		MOVL $0x67, BX												
  checker.go:17496	0x8062b3		e848710900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)			
  checker.go:17497	0x8062b8		488d442440		LEAQ 0x40(SP), AX											
  checker.go:17497	0x8062bd		488b5c2438		MOVQ 0x38(SP), BX											
  checker.go:17497	0x8062c2		488b4c2430		MOVQ 0x30(SP), CX											
  checker.go:17497	0x8062c7		0fb6bc24f5000000	MOVZX 0xf5(SP), DI											
  checker.go:17497	0x8062cf		e8cceeffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeGenericTypeReferences(SB)	
  checker.go:17497	0x8062d4		eb5b			JMP 0x806331												
  checker.go:17499	0x8062d6		488d442440		LEAQ 0x40(SP), AX											
  checker.go:17499	0x8062db		bb73000000		MOVL $0x73, BX												
  checker.go:17499	0x8062e0		e81b710900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)			
  checker.go:17307	0x8062e5		488b4c2438		MOVQ 0x38(SP), CX											
  checker.go:17307	0x8062ea		8b4908			MOVL 0x8(CX), CX											
  checker.go:17500	0x8062ed		90			NOPL													
  keybuilder.go:60	0x8062ee		90			NOPL													
  binary.go:98		0x8062ef		894c2428		MOVL CX, 0x28(SP)											
  keybuilder.go:61	0x8062f3		488d442440		LEAQ 0x40(SP), AX											
  keybuilder.go:61	0x8062f8		488d5c2428		LEAQ 0x28(SP), BX											
  keybuilder.go:61	0x8062fd		b904000000		MOVL $0x4, CX												
  keybuilder.go:61	0x806302		4889cf			MOVQ CX, DI												
  keybuilder.go:61	0x806305		e8166f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)			
  checker.go:17307	0x80630a		488b4c2430		MOVQ 0x30(SP), CX											
  checker.go:17307	0x80630f		8b4908			MOVL 0x8(CX), CX											
  checker.go:17501	0x806312		90			NOPL													
  keybuilder.go:60	0x806313		90			NOPL													
  binary.go:98		0x806314		894c2424		MOVL CX, 0x24(SP)											
  keybuilder.go:61	0x806318		488d442440		LEAQ 0x40(SP), AX											
  keybuilder.go:61	0x80631d		488d5c2424		LEAQ 0x24(SP), BX											
  keybuilder.go:61	0x806322		b904000000		MOVL $0x4, CX												
  keybuilder.go:61	0x806327		4889cf			MOVQ CX, DI												
  keybuilder.go:61	0x80632a		e8f16e0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)			
  keybuilder.go:61	0x80632f		31c0			XORL AX, AX												
  checker.go:17503	0x806331		88442423		MOVB AL, 0x23(SP)											
  keybuilder.go:60	0x806335		90			NOPL													
  binary.go:98		0x806336		8b9424f0000000		MOVL 0xf0(SP), DX											
  binary.go:98		0x80633d		8954242c		MOVL DX, 0x2c(SP)											
  keybuilder.go:61	0x806341		488d442440		LEAQ 0x40(SP), AX											
  keybuilder.go:61	0x806346		488d5c242c		LEAQ 0x2c(SP), BX											
  keybuilder.go:61	0x80634b		b904000000		MOVL $0x4, CX												
  keybuilder.go:61	0x806350		4889cf			MOVQ CX, DI												
  keybuilder.go:61	0x806353		e8c86e0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)			
  checker.go:17504	0x806358		488d442440		LEAQ 0x40(SP), AX											
  checker.go:17504	0x80635d		0f1f00			NOPL 0(AX)												
  checker.go:17504	0x806360		e87b6d0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)				
  checker.go:17504	0x806365		0fb64c2423		MOVZX 0x23(SP), CX											
  checker.go:17504	0x80636a		4881c4d0000000		ADDQ $0xd0, SP												
  checker.go:17504	0x806371		5d			POPQ BP													
  checker.go:17504	0x806372		c3			RET													
  checker.go:17489	0x806373		4889442408		MOVQ AX, 0x8(SP)											
  checker.go:17489	0x806378		48895c2410		MOVQ BX, 0x10(SP)											
  checker.go:17489	0x80637d		894c2418		MOVL CX, 0x18(SP)											
  checker.go:17489	0x806381		40887c241c		MOVB DI, 0x1c(SP)											
  checker.go:17489	0x806386		408874241d		MOVB SI, 0x1d(SP)											
  checker.go:17489	0x80638b		e87096c8ff		CALL runtime.morestack_noctxt.abi0(SB)									
  checker.go:17489	0x806390		488b442408		MOVQ 0x8(SP), AX											
  checker.go:17489	0x806395		488b5c2410		MOVQ 0x10(SP), BX											
  checker.go:17489	0x80639a		8b4c2418		MOVL 0x18(SP), CX											
  checker.go:17489	0x80639e		0fb67c241c		MOVZX 0x1c(SP), DI											
  checker.go:17489	0x8063a3		0fb674241d		MOVZX 0x1d(SP), SI											
  checker.go:17489	0x8063a8		e953feffff		JMP github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)				

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:18	0x89d0e0		493b6610		CMPQ SP, 0x10(R14)								
  keybuilder.go:18	0x89d0e4		764a			JBE 0x89d130									
  keybuilder.go:18	0x89d0e6		55			PUSHQ BP									
  keybuilder.go:18	0x89d0e7		4889e5			MOVQ SP, BP									
  keybuilder.go:18	0x89d0ea		4883ec10		SUBQ $0x10, SP									
  keybuilder.go:19	0x89d0ee		488b8888000000		MOVQ 0x88(AX), CX								
  keybuilder.go:19	0x89d0f5		4885c9			TESTQ CX, CX									
  keybuilder.go:19	0x89d0f8		751b			JNE 0x89d115									
  keybuilder.go:22	0x89d0fa		488b9880000000		MOVQ 0x80(AX), BX								
  keybuilder.go:22	0x89d101		4881fb80000000		CMPQ BX, $0x80									
  keybuilder.go:22	0x89d108		7719			JA 0x89d123									
  hash128.go:9		0x89d10a		e8b146d0ff		CALL github.com/zeebo/xxh3.hashAny128(SB)					
  keybuilder.go:22	0x89d10f		4883c410		ADDQ $0x10, SP									
  keybuilder.go:22	0x89d113		5d			POPQ BP										
  keybuilder.go:22	0x89d114		c3			RET										
  keybuilder.go:20	0x89d115		4889c8			MOVQ CX, AX									
  keybuilder.go:20	0x89d118		e84379d0ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)					
  keybuilder.go:20	0x89d11d		4883c410		ADDQ $0x10, SP									
  keybuilder.go:20	0x89d121		5d			POPQ BP										
  keybuilder.go:20	0x89d122		c3			RET										
  keybuilder.go:22	0x89d123		48c7c080000000		MOVQ $0x80, AX									
  keybuilder.go:22	0x89d12a		e87147bfff		CALL runtime.panicBounds(SB)							
  keybuilder.go:22	0x89d12f		90			NOPL										
  keybuilder.go:18	0x89d130		4889442408		MOVQ AX, 0x8(SP)								
  keybuilder.go:18	0x89d135		e8c628bfff		CALL runtime.morestack_noctxt.abi0(SB)						
  keybuilder.go:18	0x89d13a		488b442408		MOVQ 0x8(SP), AX								
  keybuilder.go:18	0x89d13f		90			NOPL										
  keybuilder.go:18	0x89d140		eb9e			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:25	0x89d160		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:25	0x89d164		0f8687000000		JBE 0x89d1f1										
  keybuilder.go:25	0x89d16a		55			PUSHQ BP										
  keybuilder.go:25	0x89d16b		4889e5			MOVQ SP, BP										
  keybuilder.go:25	0x89d16e		4883ec18		SUBQ $0x18, SP										
  keybuilder.go:26	0x89d172		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:26	0x89d17a		755b			JNE 0x89d1d7										
  keybuilder.go:26	0x89d17c		4889442428		MOVQ AX, 0x28(SP)									
  keybuilder.go:27	0x89d181		488d05189a5f00		LEAQ 0x5f9a18(IP), AX									
  keybuilder.go:27	0x89d188		e8b36db8ff		CALL runtime.newobject(SB)								
  keybuilder.go:27	0x89d18d		833d7c73650100		CMPL runtime.writeBarrier(SB), $0x0							
  keybuilder.go:27	0x89d194		7507			JNE 0x89d19d										
  keybuilder.go:27	0x89d196		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:27	0x89d19b		eb18			JMP 0x89d1b5										
  keybuilder.go:27	0x89d19d		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:27	0x89d1a2		488b9388000000		MOVQ 0x88(BX), DX									
  keybuilder.go:27	0x89d1a9		e85243bfff		CALL runtime.gcWriteBarrier2(SB)							
  keybuilder.go:27	0x89d1ae		498903			MOVQ AX, 0(R11)										
  keybuilder.go:27	0x89d1b1		49895308		MOVQ DX, 0x8(R11)									
  keybuilder.go:27	0x89d1b5		48898388000000		MOVQ AX, 0x88(BX)									
  keybuilder.go:28	0x89d1bc		488b8b80000000		MOVQ 0x80(BX), CX									
  keybuilder.go:28	0x89d1c3		4881f980000000		CMPQ CX, $0x80										
  keybuilder.go:28	0x89d1ca		7718			JA 0x89d1e4										
  hasher.go:90		0x89d1cc		90			NOPL											
  hasher.go:103		0x89d1cd		e8ae71d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:30	0x89d1d2		488b442428		MOVQ 0x28(SP), AX									
  keybuilder.go:30	0x89d1d7		488b8088000000		MOVQ 0x88(AX), AX									
  keybuilder.go:30	0x89d1de		4883c418		ADDQ $0x18, SP										
  keybuilder.go:30	0x89d1e2		5d			POPQ BP											
  keybuilder.go:30	0x89d1e3		c3			RET											
  keybuilder.go:28	0x89d1e4		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:28	0x89d1eb		e8b046bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:28	0x89d1f0		90			NOPL											
  keybuilder.go:25	0x89d1f1		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:25	0x89d1f6		e80528bfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:25	0x89d1fb		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:25	0x89d200		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:33	0x89d220		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:33	0x89d224		0f86ae000000		JBE 0x89d2d8										
  keybuilder.go:33	0x89d22a		55			PUSHQ BP										
  keybuilder.go:33	0x89d22b		4889e5			MOVQ SP, BP										
  keybuilder.go:33	0x89d22e		4883ec20		SUBQ $0x20, SP										
  keybuilder.go:34	0x89d232		48894c2440		MOVQ CX, 0x40(SP)									
  keybuilder.go:34	0x89d237		48895c2438		MOVQ BX, 0x38(SP)									
  keybuilder.go:34	0x89d23c		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:34	0x89d244		7565			JNE 0x89d2ab										
  keybuilder.go:34	0x89d246		488b9080000000		MOVQ 0x80(AX), DX									
  keybuilder.go:34	0x89d24d		488d7280		LEAQ -0x80(DX), SI									
  keybuilder.go:34	0x89d251		4889f7			MOVQ SI, DI										
  keybuilder.go:34	0x89d254		48f7de			NEGQ SI											
  keybuilder.go:34	0x89d257		4839f1			CMPQ CX, SI										
  keybuilder.go:34	0x89d25a		7f4f			JG 0x89d2ab										
  keybuilder.go:34	0x89d25c		0f1f4000		NOPL 0(AX)										
  keybuilder.go:35	0x89d260		4881fa80000000		CMPQ DX, $0x80										
  keybuilder.go:35	0x89d267		7762			JA 0x89d2cb										
  keybuilder.go:34	0x89d269		4839f1			CMPQ CX, SI										
  keybuilder.go:35	0x89d26c		480f4cf1		CMOVL CX, SI										
  keybuilder.go:35	0x89d270		48c1ff3f		SARQ $0x3f, DI										
  keybuilder.go:35	0x89d274		4821fa			ANDQ DI, DX										
  keybuilder.go:35	0x89d277		4801c2			ADDQ AX, DX										
  keybuilder.go:35	0x89d27a		4839d3			CMPQ BX, DX										
  keybuilder.go:35	0x89d27d		741f			JE 0x89d29e										
  keybuilder.go:34	0x89d27f		4889442430		MOVQ AX, 0x30(SP)									
  keybuilder.go:35	0x89d284		4889742418		MOVQ SI, 0x18(SP)									
  keybuilder.go:35	0x89d289		4889d0			MOVQ DX, AX										
  keybuilder.go:35	0x89d28c		4889f1			MOVQ SI, CX										
  keybuilder.go:35	0x89d28f		e8ac49bfff		CALL runtime.memmove(SB)								
  keybuilder.go:35	0x89d294		488b442430		MOVQ 0x30(SP), AX									
  keybuilder.go:35	0x89d299		488b742418		MOVQ 0x18(SP), SI									
  keybuilder.go:35	0x89d29e		4801b080000000		ADDQ SI, 0x80(AX)									
  keybuilder.go:36	0x89d2a5		4883c420		ADDQ $0x20, SP										
  keybuilder.go:36	0x89d2a9		5d			POPQ BP											
  keybuilder.go:36	0x89d2aa		c3			RET											
  keybuilder.go:38	0x89d2ab		e8b0feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	
  hasher.go:90		0x89d2b0		90			NOPL											
  hasher.go:103		0x89d2b1		488b5c2438		MOVQ 0x38(SP), BX									
  hasher.go:103		0x89d2b6		488b4c2440		MOVQ 0x40(SP), CX									
  hasher.go:103		0x89d2bb		0f1f440000		NOPL 0(AX)(AX*1)									
  hasher.go:103		0x89d2c0		e8bb70d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:39	0x89d2c5		4883c420		ADDQ $0x20, SP										
  keybuilder.go:39	0x89d2c9		5d			POPQ BP											
  keybuilder.go:39	0x89d2ca		c3			RET											
  keybuilder.go:35	0x89d2cb		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:35	0x89d2d2		e8c945bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:35	0x89d2d7		90			NOPL											
  keybuilder.go:33	0x89d2d8		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:33	0x89d2dd		48895c2410		MOVQ BX, 0x10(SP)									
  keybuilder.go:33	0x89d2e2		48894c2418		MOVQ CX, 0x18(SP)									
  keybuilder.go:33	0x89d2e7		48897c2420		MOVQ DI, 0x20(SP)									
  keybuilder.go:33	0x89d2ec		e80f27bfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:33	0x89d2f1		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:33	0x89d2f6		488b5c2410		MOVQ 0x10(SP), BX									
  keybuilder.go:33	0x89d2fb		488b4c2418		MOVQ 0x18(SP), CX									
  keybuilder.go:33	0x89d300		488b7c2420		MOVQ 0x20(SP), DI									
  keybuilder.go:33	0x89d305		e916ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:41	0x89d320		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:41	0x89d324		0f86a8000000		JBE 0x89d3d2										
  keybuilder.go:41	0x89d32a		55			PUSHQ BP										
  keybuilder.go:41	0x89d32b		4889e5			MOVQ SP, BP										
  keybuilder.go:41	0x89d32e		4883ec20		SUBQ $0x20, SP										
  keybuilder.go:42	0x89d332		48894c2440		MOVQ CX, 0x40(SP)									
  keybuilder.go:42	0x89d337		48895c2438		MOVQ BX, 0x38(SP)									
  keybuilder.go:42	0x89d33c		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:42	0x89d344		7565			JNE 0x89d3ab										
  keybuilder.go:42	0x89d346		488b9080000000		MOVQ 0x80(AX), DX									
  keybuilder.go:42	0x89d34d		488d7280		LEAQ -0x80(DX), SI									
  keybuilder.go:42	0x89d351		4889f7			MOVQ SI, DI										
  keybuilder.go:42	0x89d354		48f7de			NEGQ SI											
  keybuilder.go:42	0x89d357		4839f1			CMPQ CX, SI										
  keybuilder.go:42	0x89d35a		7f4f			JG 0x89d3ab										
  keybuilder.go:42	0x89d35c		0f1f4000		NOPL 0(AX)										
  keybuilder.go:43	0x89d360		4881fa80000000		CMPQ DX, $0x80										
  keybuilder.go:43	0x89d367		775c			JA 0x89d3c5										
  keybuilder.go:42	0x89d369		4839f1			CMPQ CX, SI										
  keybuilder.go:43	0x89d36c		480f4cf1		CMOVL CX, SI										
  keybuilder.go:43	0x89d370		48c1ff3f		SARQ $0x3f, DI										
  keybuilder.go:43	0x89d374		4821fa			ANDQ DI, DX										
  keybuilder.go:43	0x89d377		4801c2			ADDQ AX, DX										
  keybuilder.go:43	0x89d37a		4839d3			CMPQ BX, DX										
  keybuilder.go:43	0x89d37d		741f			JE 0x89d39e										
  keybuilder.go:42	0x89d37f		4889442430		MOVQ AX, 0x30(SP)									
  keybuilder.go:43	0x89d384		4889742418		MOVQ SI, 0x18(SP)									
  keybuilder.go:43	0x89d389		4889d0			MOVQ DX, AX										
  keybuilder.go:43	0x89d38c		4889f1			MOVQ SI, CX										
  keybuilder.go:43	0x89d38f		e8ac48bfff		CALL runtime.memmove(SB)								
  keybuilder.go:43	0x89d394		488b442430		MOVQ 0x30(SP), AX									
  keybuilder.go:43	0x89d399		488b742418		MOVQ 0x18(SP), SI									
  keybuilder.go:43	0x89d39e		4801b080000000		ADDQ SI, 0x80(AX)									
  keybuilder.go:44	0x89d3a5		4883c420		ADDQ $0x20, SP										
  keybuilder.go:44	0x89d3a9		5d			POPQ BP											
  keybuilder.go:44	0x89d3aa		c3			RET											
  keybuilder.go:46	0x89d3ab		e8b0fdffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	
  hasher.go:97		0x89d3b0		488b5c2438		MOVQ 0x38(SP), BX									
  hasher.go:97		0x89d3b5		488b4c2440		MOVQ 0x40(SP), CX									
  hasher.go:97		0x89d3ba		e8c16fd0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:47	0x89d3bf		4883c420		ADDQ $0x20, SP										
  keybuilder.go:47	0x89d3c3		5d			POPQ BP											
  keybuilder.go:47	0x89d3c4		c3			RET											
  keybuilder.go:43	0x89d3c5		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:43	0x89d3cc		e8cf44bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:43	0x89d3d1		90			NOPL											
  keybuilder.go:41	0x89d3d2		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:41	0x89d3d7		48895c2410		MOVQ BX, 0x10(SP)									
  keybuilder.go:41	0x89d3dc		48894c2418		MOVQ CX, 0x18(SP)									
  keybuilder.go:41	0x89d3e1		e81a26bfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:41	0x89d3e6		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:41	0x89d3eb		488b5c2410		MOVQ 0x10(SP), BX									
  keybuilder.go:41	0x89d3f0		488b4c2418		MOVQ 0x18(SP), CX									
  keybuilder.go:41	0x89d3f5		e926ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:49	0x89d400		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:49	0x89d404		7662			JBE 0x89d468										
  keybuilder.go:49	0x89d406		55			PUSHQ BP										
  keybuilder.go:49	0x89d407		4889e5			MOVQ SP, BP										
  keybuilder.go:49	0x89d40a		4883ec28		SUBQ $0x28, SP										
  keybuilder.go:50	0x89d40e		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:50	0x89d416		7527			JNE 0x89d43f										
  keybuilder.go:50	0x89d418		488b9080000000		MOVQ 0x80(AX), DX									
  keybuilder.go:50	0x89d41f		90			NOPL											
  keybuilder.go:50	0x89d420		4883fa7f		CMPQ DX, $0x7f										
  keybuilder.go:50	0x89d424		7f19			JG 0x89d43f										
  keybuilder.go:51	0x89d426		4881fa80000000		CMPQ DX, $0x80										
  keybuilder.go:51	0x89d42d		732c			JAE 0x89d45b										
  keybuilder.go:51	0x89d42f		881c10			MOVB BL, 0(AX)(DX*1)									
  keybuilder.go:52	0x89d432		48ff8080000000		INCQ 0x80(AX)										
  keybuilder.go:53	0x89d439		4883c428		ADDQ $0x28, SP										
  keybuilder.go:53	0x89d43d		5d			POPQ BP											
  keybuilder.go:53	0x89d43e		c3			RET											
  keybuilder.go:55	0x89d43f		885c2427		MOVB BL, 0x27(SP)									
  keybuilder.go:55	0x89d443		488d5c2427		LEAQ 0x27(SP), BX									
  keybuilder.go:55	0x89d448		b901000000		MOVL $0x1, CX										
  keybuilder.go:55	0x89d44d		4889cf			MOVQ CX, DI										
  keybuilder.go:55	0x89d450		e8cbfdffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)	
  keybuilder.go:56	0x89d455		4883c428		ADDQ $0x28, SP										
  keybuilder.go:56	0x89d459		5d			POPQ BP											
  keybuilder.go:56	0x89d45a		c3			RET											
  keybuilder.go:51	0x89d45b		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:51	0x89d462		e83944bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:51	0x89d467		90			NOPL											
  keybuilder.go:49	0x89d468		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:49	0x89d46d		885c2410		MOVB BL, 0x10(SP)									
  keybuilder.go:49	0x89d471		e88a25bfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:49	0x89d476		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:49	0x89d47b		0fb65c2410		MOVZX 0x10(SP), BX									
  keybuilder.go:49	0x89d480		e97bffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)	
