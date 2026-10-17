TEXT github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17372	0x805ae0		4c8d6424c8		LEAQ -0x38(SP), R12									
  checker.go:17372	0x805ae5		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17372	0x805ae9		766d			JBE 0x805b58										
  checker.go:17372	0x805aeb		55			PUSHQ BP										
  checker.go:17372	0x805aec		4889e5			MOVQ SP, BP										
  checker.go:17372	0x805aef		4881ecb0000000		SUBQ $0xb0, SP										
  checker.go:17372	0x805af6		48898424c0000000	MOVQ AX, 0xc0(SP)									
  checker.go:17373	0x805afe		488d542420		LEAQ 0x20(SP), DX									
  checker.go:17373	0x805b03		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17373	0x805b07		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17373	0x805b0c		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17373	0x805b11		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17373	0x805b16		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17373	0x805b1b		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17373	0x805b20		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17373	0x805b25		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17373	0x805b2a		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17374	0x805b32		4889cf			MOVQ CX, DI										
  checker.go:17374	0x805b35		4889d9			MOVQ BX, CX										
  checker.go:17374	0x805b38		4889c3			MOVQ AX, BX										
  checker.go:17374	0x805b3b		4889d0			MOVQ DX, AX										
  checker.go:17374	0x805b3e		6690			NOPW											
  checker.go:17374	0x805b40		e81bf5ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17375	0x805b45		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17375	0x805b4a		e8917f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17375	0x805b4f		4881c4b0000000		ADDQ $0xb0, SP										
  checker.go:17375	0x805b56		5d			POPQ BP											
  checker.go:17375	0x805b57		c3			RET											
  checker.go:17372	0x805b58		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17372	0x805b5d		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17372	0x805b62		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17372	0x805b67		e8949ec8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17372	0x805b6c		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17372	0x805b71		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17372	0x805b76		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17372	0x805b7b		0f1f440000		NOPL 0(AX)(AX*1)									
  checker.go:17372	0x805b80		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17456	0x806440		4c8d6424d8			LEAQ -0x28(SP), R12										
  checker.go:17456	0x806445		4d3b6610			CMPQ R12, 0x10(R14)										
  checker.go:17456	0x806449		0f86d9000000			JBE 0x806528											
  checker.go:17456	0x80644f		55				PUSHQ BP											
  checker.go:17456	0x806450		4889e5				MOVQ SP, BP											
  checker.go:17456	0x806453		4881eca0000000			SUBQ $0xa0, SP											
  checker.go:17457	0x80645a		488d542410			LEAQ 0x10(SP), DX										
  checker.go:17457	0x80645f		440f113a			MOVUPS X15, 0(DX)										
  checker.go:17457	0x806463		440f117a10			MOVUPS X15, 0x10(DX)										
  checker.go:17457	0x806468		440f117a20			MOVUPS X15, 0x20(DX)										
  checker.go:17457	0x80646d		440f117a30			MOVUPS X15, 0x30(DX)										
  checker.go:17457	0x806472		440f117a40			MOVUPS X15, 0x40(DX)										
  checker.go:17457	0x806477		440f117a50			MOVUPS X15, 0x50(DX)										
  checker.go:17457	0x80647c		440f117a60			MOVUPS X15, 0x60(DX)										
  checker.go:17457	0x806481		440f117a70			MOVUPS X15, 0x70(DX)										
  checker.go:17457	0x806486		440f11ba80000000		MOVUPS X15, 0x80(DX)										
  checker.go:17307	0x80648e		8b7008				MOVL 0x8(AX), SI										
  checker.go:17458	0x806491		90				NOPL												
  keybuilder.go:62	0x806492		90				NOPL												
  binary.go:98		0x806493		89742410			MOVL SI, 0x10(SP)										
  keybuilder.go:63	0x806497		48c784249000000004000000	MOVQ $0x4, 0x90(SP)										
  checker.go:17307	0x8064a3		8b7308				MOVL 0x8(BX), SI										
  checker.go:17459	0x8064a6		90				NOPL												
  keybuilder.go:62	0x8064a7		90				NOPL												
  binary.go:98		0x8064a8		89742414			MOVL SI, 0x14(SP)										
  keybuilder.go:63	0x8064ac		488384249000000004		ADDQ $0x4, 0x90(SP)										
  keybuilder.go:61	0x8064b5		488bb42490000000		MOVQ 0x90(SP), SI										
  checker.go:17460	0x8064bd		90				NOPL												
  checker.go:17460	0x8064be		6690				NOPW												
  keybuilder.go:61	0x8064c0		4883fe7c			CMPQ SI, $0x7c											
  keybuilder.go:61	0x8064c4		7f18				JG 0x8064de											
  keybuilder.go:62	0x8064c6		4881fe80000000			CMPQ SI, $0x80											
  keybuilder.go:62	0x8064cd		774c				JA 0x80651b											
  binary.go:98		0x8064cf		894c3410			MOVL CX, 0x10(SP)(SI*1)										
  keybuilder.go:63	0x8064d3		488384249000000004		ADDQ $0x4, 0x90(SP)										
  keybuilder.go:63	0x8064dc		eb1f				JMP 0x8064fd											
  keybuilder.go:61	0x8064de		4889bc24c8000000		MOVQ DI, 0xc8(SP)										
  keybuilder.go:65	0x8064e6		4889d0				MOVQ DX, AX											
  keybuilder.go:65	0x8064e9		89cb				MOVL CX, BX											
  keybuilder.go:65	0x8064eb		e870780900			CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)	
  checker.go:17457	0x8064f0		488d542410			LEAQ 0x10(SP), DX										
  checker.go:17461	0x8064f5		488bbc24c8000000		MOVQ 0xc8(SP), DI										
  checker.go:17461	0x8064fd		4889d0				MOVQ DX, AX											
  checker.go:17461	0x806500		4889fb				MOVQ DI, BX											
  checker.go:17461	0x806503		e878ecffff			CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)		
  checker.go:17462	0x806508		488d442410			LEAQ 0x10(SP), AX										
  checker.go:17462	0x80650d		e8ce750900			CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)			
  checker.go:17462	0x806512		4881c4a0000000			ADDQ $0xa0, SP											
  checker.go:17462	0x806519		5d				POPQ BP												
  checker.go:17462	0x80651a		c3				RET												
  keybuilder.go:62	0x80651b		48c7c080000000			MOVQ $0x80, AX											
  keybuilder.go:62	0x806522		e879b3c8ff			CALL runtime.panicBounds(SB)									
  keybuilder.go:62	0x806527		90				NOPL												
  checker.go:17456	0x806528		4889442408			MOVQ AX, 0x8(SP)										
  checker.go:17456	0x80652d		48895c2410			MOVQ BX, 0x10(SP)										
  checker.go:17456	0x806532		894c2418			MOVL CX, 0x18(SP)										
  checker.go:17456	0x806536		48897c2420			MOVQ DI, 0x20(SP)										
  checker.go:17456	0x80653b		0f1f440000			NOPL 0(AX)(AX*1)										
  checker.go:17456	0x806540		e8bb94c8ff			CALL runtime.morestack_noctxt.abi0(SB)								
  checker.go:17456	0x806545		488b442408			MOVQ 0x8(SP), AX										
  checker.go:17456	0x80654a		488b5c2410			MOVQ 0x10(SP), BX										
  checker.go:17456	0x80654f		8b4c2418			MOVL 0x18(SP), CX										
  checker.go:17456	0x806553		488b7c2420			MOVQ 0x20(SP), DI										
  checker.go:17456	0x806558		e9e3feffff			JMP github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB)			

TEXT github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17479	0x8067c0		4c8d6424c8		LEAQ -0x38(SP), R12										
  checker.go:17479	0x8067c5		4d3b6610		CMPQ R12, 0x10(R14)										
  checker.go:17479	0x8067c9		0f86df000000		JBE 0x8068ae											
  checker.go:17479	0x8067cf		55			PUSHQ BP											
  checker.go:17479	0x8067d0		4889e5			MOVQ SP, BP											
  checker.go:17479	0x8067d3		4881ecb0000000		SUBQ $0xb0, SP											
  checker.go:17479	0x8067da		48898424c0000000	MOVQ AX, 0xc0(SP)										
  checker.go:17483	0x8067e2		4889bc24d8000000	MOVQ DI, 0xd8(SP)										
  checker.go:17483	0x8067ea		4088b424e0000000	MOVB SI, 0xe0(SP)										
  checker.go:17480	0x8067f2		488d542420		LEAQ 0x20(SP), DX										
  checker.go:17480	0x8067f7		440f113a		MOVUPS X15, 0(DX)										
  checker.go:17480	0x8067fb		440f117a10		MOVUPS X15, 0x10(DX)										
  checker.go:17480	0x806800		440f117a20		MOVUPS X15, 0x20(DX)										
  checker.go:17480	0x806805		440f117a30		MOVUPS X15, 0x30(DX)										
  checker.go:17480	0x80680a		440f117a40		MOVUPS X15, 0x40(DX)										
  checker.go:17480	0x80680f		440f117a50		MOVUPS X15, 0x50(DX)										
  checker.go:17480	0x806814		440f117a60		MOVUPS X15, 0x60(DX)										
  checker.go:17480	0x806819		440f117a70		MOVUPS X15, 0x70(DX)										
  checker.go:17480	0x80681e		440f11ba80000000	MOVUPS X15, 0x80(DX)										
  checker.go:17481	0x806826		4889cf			MOVQ CX, DI											
  checker.go:17481	0x806829		4889d9			MOVQ BX, CX											
  checker.go:17481	0x80682c		4889c3			MOVQ AX, BX											
  checker.go:17481	0x80682f		4889d0			MOVQ DX, AX											
  checker.go:17481	0x806832		e829e8ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)		
  checker.go:17482	0x806837		488d442420		LEAQ 0x20(SP), AX										
  checker.go:17482	0x80683c		488b9c24d8000000	MOVQ 0xd8(SP), BX										
  checker.go:17482	0x806844		e837e9ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)		
  checker.go:17483	0x806849		0fb69424e0000000	MOVZX 0xe0(SP), DX										
  checker.go:17483	0x806851		84d2			TESTL DL, DL											
  checker.go:17483	0x806853		7438			JE 0x80688d											
  keybuilder.go:52	0x806855		488b8c24a0000000	MOVQ 0xa0(SP), CX										
  checker.go:17484	0x80685d		90			NOPL												
  checker.go:17484	0x80685e		6690			NOPW												
  keybuilder.go:52	0x806860		4883f97f		CMPQ CX, $0x7f											
  keybuilder.go:52	0x806864		7f18			JG 0x80687e											
  keybuilder.go:53	0x806866		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:53	0x80686d		7332			JAE 0x8068a1											
  keybuilder.go:53	0x80686f		c6440c2021		MOVB $0x21, 0x20(SP)(CX*1)									
  keybuilder.go:54	0x806874		48ff8424a0000000	INCQ 0xa0(SP)											
  keybuilder.go:54	0x80687c		eb0f			JMP 0x80688d											
  keybuilder.go:56	0x80687e		488d442420		LEAQ 0x20(SP), AX										
  keybuilder.go:56	0x806883		bb21000000		MOVL $0x21, BX											
  keybuilder.go:56	0x806888		e873740900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	
  checker.go:17486	0x80688d		488d442420		LEAQ 0x20(SP), AX										
  checker.go:17486	0x806892		e849720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)			
  checker.go:17486	0x806897		4881c4b0000000		ADDQ $0xb0, SP											
  checker.go:17486	0x80689e		5d			POPQ BP												
  checker.go:17486	0x80689f		90			NOPL												
  checker.go:17486	0x8068a0		c3			RET												
  keybuilder.go:53	0x8068a1		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:53	0x8068a8		e8f3afc8ff		CALL runtime.panicBounds(SB)									
  keybuilder.go:53	0x8068ad		90			NOPL												
  checker.go:17479	0x8068ae		4889442408		MOVQ AX, 0x8(SP)										
  checker.go:17479	0x8068b3		48895c2410		MOVQ BX, 0x10(SP)										
  checker.go:17479	0x8068b8		48894c2418		MOVQ CX, 0x18(SP)										
  checker.go:17479	0x8068bd		48897c2420		MOVQ DI, 0x20(SP)										
  checker.go:17479	0x8068c2		4088742428		MOVB SI, 0x28(SP)										
  checker.go:17479	0x8068c7		e83491c8ff		CALL runtime.morestack_noctxt.abi0(SB)								
  checker.go:17479	0x8068cc		488b442408		MOVQ 0x8(SP), AX										
  checker.go:17479	0x8068d1		488b5c2410		MOVQ 0x10(SP), BX										
  checker.go:17479	0x8068d6		488b4c2418		MOVQ 0x18(SP), CX										
  checker.go:17479	0x8068db		488b7c2420		MOVQ 0x20(SP), DI										
  checker.go:17479	0x8068e0		0fb6742428		MOVZX 0x28(SP), SI										
  checker.go:17479	0x8068e5		e9d6feffff		JMP github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17489	0x806900		4c8d6424b0		LEAQ -0x50(SP), R12											
  checker.go:17489	0x806905		4d3b6610		CMPQ R12, 0x10(R14)											
  checker.go:17489	0x806909		0f8663020000		JBE 0x806b72												
  checker.go:17489	0x80690f		55			PUSHQ BP												
  checker.go:17489	0x806910		4889e5			MOVQ SP, BP												
  checker.go:17489	0x806913		4881ecc8000000		SUBQ $0xc8, SP												
  checker.go:17490	0x80691a		898c24e8000000		MOVL CX, 0xe8(SP)											
  checker.go:17490	0x806921		4088b424ed000000	MOVB SI, 0xed(SP)											
  checker.go:17490	0x806929		4084ff			TESTL DI, DI												
  checker.go:17490	0x80692c		7414			JE 0x806942												
  checker.go:17490	0x80692e		8b5008			MOVL 0x8(AX), DX											
  checker.go:17490	0x806931		395308			CMPL 0x8(BX), DX											
  checker.go:17490	0x806934		7215			JB 0x80694b												
  checker.go:17493	0x806936		4889da			MOVQ BX, DX												
  checker.go:17493	0x806939		4889c3			MOVQ AX, BX												
  checker.go:17493	0x80693c		4889d0			MOVQ DX, AX												
  checker.go:17493	0x80693f		90			NOPL													
  checker.go:17490	0x806940		eb09			JMP 0x80694b												
  checker.go:17493	0x806942		4889da			MOVQ BX, DX												
  checker.go:17493	0x806945		4889c3			MOVQ AX, BX												
  checker.go:17493	0x806948		4889d0			MOVQ DX, AX												
  checker.go:17493	0x80694b		48895c2430		MOVQ BX, 0x30(SP)											
  checker.go:17493	0x806950		4889442428		MOVQ AX, 0x28(SP)											
  checker.go:17493	0x806955		488d4c2438		LEAQ 0x38(SP), CX											
  checker.go:17493	0x80695a		440f1139		MOVUPS X15, 0(CX)											
  checker.go:17493	0x80695e		440f117910		MOVUPS X15, 0x10(CX)											
  checker.go:17493	0x806963		440f117920		MOVUPS X15, 0x20(CX)											
  checker.go:17493	0x806968		440f117930		MOVUPS X15, 0x30(CX)											
  checker.go:17493	0x80696d		440f117940		MOVUPS X15, 0x40(CX)											
  checker.go:17493	0x806972		440f117950		MOVUPS X15, 0x50(CX)											
  checker.go:17493	0x806977		440f117960		MOVUPS X15, 0x60(CX)											
  checker.go:17493	0x80697c		440f117970		MOVUPS X15, 0x70(CX)											
  checker.go:17493	0x806981		440f11b980000000	MOVUPS X15, 0x80(CX)											
  checker.go:17495	0x806989		4889d8			MOVQ BX, AX												
  checker.go:17495	0x80698c		e82f020000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x806991		84c0			TESTL AL, AL												
  checker.go:17495	0x806993		7504			JNE 0x806999												
  checker.go:17495	0x806995		31c0			XORL AX, AX												
  checker.go:17495	0x806997		eb0c			JMP 0x8069a5												
  checker.go:17495	0x806999		488b442428		MOVQ 0x28(SP), AX											
  checker.go:17495	0x80699e		6690			NOPW													
  checker.go:17495	0x8069a0		e81b020000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x8069a5		84c0			TESTL AL, AL												
  checker.go:17495	0x8069a7		7463			JE 0x806a0c												
  keybuilder.go:52	0x8069a9		488b9424b8000000	MOVQ 0xb8(SP), DX											
  checker.go:17496	0x8069b1		90			NOPL													
  keybuilder.go:52	0x8069b2		4883fa7f		CMPQ DX, $0x7f												
  keybuilder.go:52	0x8069b6		7f24			JG 0x8069dc												
  keybuilder.go:52	0x8069b8		0f1f840000000000	NOPL 0(AX)(AX*1)											
  keybuilder.go:53	0x8069c0		4881fa80000000		CMPQ DX, $0x80												
  keybuilder.go:53	0x8069c7		0f8398010000		JAE 0x806b65												
  keybuilder.go:53	0x8069cd		c644143867		MOVB $0x67, 0x38(SP)(DX*1)										
  keybuilder.go:54	0x8069d2		48ff8424b8000000	INCQ 0xb8(SP)												
  keybuilder.go:54	0x8069da		eb0f			JMP 0x8069eb												
  keybuilder.go:56	0x8069dc		488d442438		LEAQ 0x38(SP), AX											
  keybuilder.go:56	0x8069e1		bb67000000		MOVL $0x67, BX												
  keybuilder.go:56	0x8069e6		e815730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)		
  checker.go:17497	0x8069eb		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17497	0x8069f0		488b5c2430		MOVQ 0x30(SP), BX											
  checker.go:17497	0x8069f5		488b4c2428		MOVQ 0x28(SP), CX											
  checker.go:17497	0x8069fa		0fb6bc24ed000000	MOVZX 0xed(SP), DI											
  checker.go:17497	0x806a02		e879e8ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeGenericTypeReferences(SB)	
  checker.go:17497	0x806a07		e9c2000000		JMP 0x806ace												
  keybuilder.go:52	0x806a0c		488b8c24b8000000	MOVQ 0xb8(SP), CX											
  checker.go:17499	0x806a14		90			NOPL													
  keybuilder.go:52	0x806a15		4883f97f		CMPQ CX, $0x7f												
  keybuilder.go:52	0x806a19		7f21			JG 0x806a3c												
  keybuilder.go:52	0x806a1b		0f1f440000		NOPL 0(AX)(AX*1)											
  keybuilder.go:53	0x806a20		4881f980000000		CMPQ CX, $0x80												
  keybuilder.go:53	0x806a27		0f832a010000		JAE 0x806b57												
  keybuilder.go:53	0x806a2d		c6440c3873		MOVB $0x73, 0x38(SP)(CX*1)										
  keybuilder.go:54	0x806a32		48ff8424b8000000	INCQ 0xb8(SP)												
  keybuilder.go:54	0x806a3a		eb0f			JMP 0x806a4b												
  keybuilder.go:56	0x806a3c		488d442438		LEAQ 0x38(SP), AX											
  keybuilder.go:56	0x806a41		bb73000000		MOVL $0x73, BX												
  keybuilder.go:56	0x806a46		e8b5720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)		
  keybuilder.go:61	0x806a4b		488b8c24b8000000	MOVQ 0xb8(SP), CX											
  checker.go:17500	0x806a53		90			NOPL													
  checker.go:17307	0x806a54		488b542430		MOVQ 0x30(SP), DX											
  checker.go:17307	0x806a59		8b5a08			MOVL 0x8(DX), BX											
  checker.go:17307	0x806a5c		0f1f4000		NOPL 0(AX)												
  keybuilder.go:61	0x806a60		4883f97c		CMPQ CX, $0x7c												
  keybuilder.go:61	0x806a64		7f1c			JG 0x806a82												
  keybuilder.go:62	0x806a66		4881f980000000		CMPQ CX, $0x80												
  keybuilder.go:62	0x806a6d		0f87d8000000		JA 0x806b4b												
  binary.go:98		0x806a73		895c0c38		MOVL BX, 0x38(SP)(CX*1)											
  keybuilder.go:63	0x806a77		48838424b800000004	ADDQ $0x4, 0xb8(SP)											
  keybuilder.go:63	0x806a80		eb0a			JMP 0x806a8c												
  keybuilder.go:65	0x806a82		488d442438		LEAQ 0x38(SP), AX											
  keybuilder.go:65	0x806a87		e8d4720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)		
  keybuilder.go:61	0x806a8c		488b8c24b8000000	MOVQ 0xb8(SP), CX											
  checker.go:17501	0x806a94		90			NOPL													
  checker.go:17307	0x806a95		488b542428		MOVQ 0x28(SP), DX											
  checker.go:17307	0x806a9a		8b5a08			MOVL 0x8(DX), BX											
  checker.go:17307	0x806a9d		0f1f00			NOPL 0(AX)												
  keybuilder.go:61	0x806aa0		4883f97c		CMPQ CX, $0x7c												
  keybuilder.go:61	0x806aa4		7f1c			JG 0x806ac2												
  keybuilder.go:62	0x806aa6		4881f980000000		CMPQ CX, $0x80												
  keybuilder.go:62	0x806aad		0f878c000000		JA 0x806b3f												
  binary.go:98		0x806ab3		895c0c38		MOVL BX, 0x38(SP)(CX*1)											
  keybuilder.go:63	0x806ab7		48838424b800000004	ADDQ $0x4, 0xb8(SP)											
  keybuilder.go:63	0x806ac0		eb0a			JMP 0x806acc												
  keybuilder.go:65	0x806ac2		488d442438		LEAQ 0x38(SP), AX											
  keybuilder.go:65	0x806ac7		e894720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)		
  checker.go:17307	0x806acc		31c0			XORL AX, AX												
  checker.go:17503	0x806ace		88442427		MOVB AL, 0x27(SP)											
  keybuilder.go:61	0x806ad2		488b8c24b8000000	MOVQ 0xb8(SP), CX											
  keybuilder.go:61	0x806ada		660f1f440000		NOPW 0(AX)(AX*1)											
  keybuilder.go:61	0x806ae0		4883f97c		CMPQ CX, $0x7c												
  keybuilder.go:61	0x806ae4		7f1f			JG 0x806b05												
  keybuilder.go:62	0x806ae6		4881f980000000		CMPQ CX, $0x80												
  keybuilder.go:62	0x806aed		7744			JA 0x806b33												
  binary.go:98		0x806aef		8b9424e8000000		MOVL 0xe8(SP), DX											
  binary.go:98		0x806af6		89540c38		MOVL DX, 0x38(SP)(CX*1)											
  keybuilder.go:63	0x806afa		48838424b800000004	ADDQ $0x4, 0xb8(SP)											
  keybuilder.go:63	0x806b03		eb11			JMP 0x806b16												
  keybuilder.go:65	0x806b05		488d442438		LEAQ 0x38(SP), AX											
  keybuilder.go:65	0x806b0a		8b9c24e8000000		MOVL 0xe8(SP), BX											
  keybuilder.go:65	0x806b11		e84a720900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)		
  checker.go:17504	0x806b16		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17504	0x806b1b		0f1f440000		NOPL 0(AX)(AX*1)											
  checker.go:17504	0x806b20		e8bb6f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)				
  checker.go:17504	0x806b25		0fb64c2427		MOVZX 0x27(SP), CX											
  checker.go:17504	0x806b2a		4881c4c8000000		ADDQ $0xc8, SP												
  checker.go:17504	0x806b31		5d			POPQ BP													
  checker.go:17504	0x806b32		c3			RET													
  keybuilder.go:62	0x806b33		48c7c080000000		MOVQ $0x80, AX												
  keybuilder.go:62	0x806b3a		e861adc8ff		CALL runtime.panicBounds(SB)										
  keybuilder.go:62	0x806b3f		48c7c080000000		MOVQ $0x80, AX												
  keybuilder.go:62	0x806b46		e855adc8ff		CALL runtime.panicBounds(SB)										
  keybuilder.go:62	0x806b4b		48c7c080000000		MOVQ $0x80, AX												
  keybuilder.go:62	0x806b52		e849adc8ff		CALL runtime.panicBounds(SB)										
  keybuilder.go:53	0x806b57		48c7c080000000		MOVQ $0x80, AX												
  keybuilder.go:53	0x806b5e		6690			NOPW													
  keybuilder.go:53	0x806b60		e83badc8ff		CALL runtime.panicBounds(SB)										
  keybuilder.go:53	0x806b65		48c7c080000000		MOVQ $0x80, AX												
  keybuilder.go:53	0x806b6c		e82fadc8ff		CALL runtime.panicBounds(SB)										
  keybuilder.go:53	0x806b71		90			NOPL													
  checker.go:17489	0x806b72		4889442408		MOVQ AX, 0x8(SP)											
  checker.go:17489	0x806b77		48895c2410		MOVQ BX, 0x10(SP)											
  checker.go:17489	0x806b7c		894c2418		MOVL CX, 0x18(SP)											
  checker.go:17489	0x806b80		40887c241c		MOVB DI, 0x1c(SP)											
  checker.go:17489	0x806b85		408874241d		MOVB SI, 0x1d(SP)											
  checker.go:17489	0x806b8a		e8718ec8ff		CALL runtime.morestack_noctxt.abi0(SB)									
  checker.go:17489	0x806b8f		488b442408		MOVQ 0x8(SP), AX											
  checker.go:17489	0x806b94		488b5c2410		MOVQ 0x10(SP), BX											
  checker.go:17489	0x806b99		8b4c2418		MOVL 0x18(SP), CX											
  checker.go:17489	0x806b9d		0fb67c241c		MOVZX 0x1c(SP), DI											
  checker.go:17489	0x806ba2		0fb674241d		MOVZX 0x1d(SP), SI											
  checker.go:17489	0x806ba7		e954fdffff		JMP github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)				

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:19	0x89dae0		493b6610		CMPQ SP, 0x10(R14)								
  keybuilder.go:19	0x89dae4		764a			JBE 0x89db30									
  keybuilder.go:19	0x89dae6		55			PUSHQ BP									
  keybuilder.go:19	0x89dae7		4889e5			MOVQ SP, BP									
  keybuilder.go:19	0x89daea		4883ec10		SUBQ $0x10, SP									
  keybuilder.go:20	0x89daee		488b8888000000		MOVQ 0x88(AX), CX								
  keybuilder.go:20	0x89daf5		4885c9			TESTQ CX, CX									
  keybuilder.go:20	0x89daf8		751b			JNE 0x89db15									
  keybuilder.go:23	0x89dafa		488b9880000000		MOVQ 0x80(AX), BX								
  keybuilder.go:23	0x89db01		4881fb80000000		CMPQ BX, $0x80									
  keybuilder.go:23	0x89db08		7719			JA 0x89db23									
  hash128.go:9		0x89db0a		e8b13cd0ff		CALL github.com/zeebo/xxh3.hashAny128(SB)					
  keybuilder.go:23	0x89db0f		4883c410		ADDQ $0x10, SP									
  keybuilder.go:23	0x89db13		5d			POPQ BP										
  keybuilder.go:23	0x89db14		c3			RET										
  keybuilder.go:21	0x89db15		4889c8			MOVQ CX, AX									
  keybuilder.go:21	0x89db18		e8436fd0ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)					
  keybuilder.go:21	0x89db1d		4883c410		ADDQ $0x10, SP									
  keybuilder.go:21	0x89db21		5d			POPQ BP										
  keybuilder.go:21	0x89db22		c3			RET										
  keybuilder.go:23	0x89db23		48c7c080000000		MOVQ $0x80, AX									
  keybuilder.go:23	0x89db2a		e8713dbfff		CALL runtime.panicBounds(SB)							
  keybuilder.go:23	0x89db2f		90			NOPL										
  keybuilder.go:19	0x89db30		4889442408		MOVQ AX, 0x8(SP)								
  keybuilder.go:19	0x89db35		e8c61ebfff		CALL runtime.morestack_noctxt.abi0(SB)						
  keybuilder.go:19	0x89db3a		488b442408		MOVQ 0x8(SP), AX								
  keybuilder.go:19	0x89db3f		90			NOPL										
  keybuilder.go:19	0x89db40		eb9e			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:26	0x89db60		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:26	0x89db64		0f8695000000		JBE 0x89dbff										
  keybuilder.go:26	0x89db6a		55			PUSHQ BP										
  keybuilder.go:26	0x89db6b		4889e5			MOVQ SP, BP										
  keybuilder.go:26	0x89db6e		4883ec18		SUBQ $0x18, SP										
  keybuilder.go:27	0x89db72		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:27	0x89db7a		7569			JNE 0x89dbe5										
  keybuilder.go:27	0x89db7c		4889442428		MOVQ AX, 0x28(SP)									
  keybuilder.go:28	0x89db81		488d0518905f00		LEAQ 0x5f9018(IP), AX									
  keybuilder.go:28	0x89db88		e8b363b8ff		CALL runtime.newobject(SB)								
  keybuilder.go:28	0x89db8d		833d7c69650100		CMPL runtime.writeBarrier(SB), $0x0							
  keybuilder.go:28	0x89db94		7507			JNE 0x89db9d										
  keybuilder.go:28	0x89db96		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:28	0x89db9b		eb18			JMP 0x89dbb5										
  keybuilder.go:28	0x89db9d		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:28	0x89dba2		488b9388000000		MOVQ 0x88(BX), DX									
  keybuilder.go:28	0x89dba9		e85239bfff		CALL runtime.gcWriteBarrier2(SB)							
  keybuilder.go:28	0x89dbae		498903			MOVQ AX, 0(R11)										
  keybuilder.go:28	0x89dbb1		49895308		MOVQ DX, 0x8(R11)									
  keybuilder.go:28	0x89dbb5		48898388000000		MOVQ AX, 0x88(BX)									
  keybuilder.go:29	0x89dbbc		488b8b80000000		MOVQ 0x80(BX), CX									
  keybuilder.go:29	0x89dbc3		4881f980000000		CMPQ CX, $0x80										
  keybuilder.go:29	0x89dbca		7726			JA 0x89dbf2										
  hasher.go:90		0x89dbcc		90			NOPL											
  hasher.go:103		0x89dbcd		e8ae67d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:30	0x89dbd2		488b542428		MOVQ 0x28(SP), DX									
  keybuilder.go:30	0x89dbd7		48c7828000000080000000	MOVQ $0x80, 0x80(DX)									
  keybuilder.go:32	0x89dbe2		4889d0			MOVQ DX, AX										
  keybuilder.go:32	0x89dbe5		488b8088000000		MOVQ 0x88(AX), AX									
  keybuilder.go:32	0x89dbec		4883c418		ADDQ $0x18, SP										
  keybuilder.go:32	0x89dbf0		5d			POPQ BP											
  keybuilder.go:32	0x89dbf1		c3			RET											
  keybuilder.go:29	0x89dbf2		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:29	0x89dbf9		e8a23cbfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:29	0x89dbfe		90			NOPL											
  keybuilder.go:26	0x89dbff		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:26	0x89dc04		e8f71dbfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:26	0x89dc09		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:26	0x89dc0e		e94dffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:43	0x89dc20		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:43	0x89dc24		0f86a8000000		JBE 0x89dcd2										
  keybuilder.go:43	0x89dc2a		55			PUSHQ BP										
  keybuilder.go:43	0x89dc2b		4889e5			MOVQ SP, BP										
  keybuilder.go:43	0x89dc2e		4883ec20		SUBQ $0x20, SP										
  keybuilder.go:44	0x89dc32		48894c2440		MOVQ CX, 0x40(SP)									
  keybuilder.go:44	0x89dc37		48895c2438		MOVQ BX, 0x38(SP)									
  keybuilder.go:44	0x89dc3c		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:44	0x89dc44		7565			JNE 0x89dcab										
  keybuilder.go:44	0x89dc46		488b9080000000		MOVQ 0x80(AX), DX									
  keybuilder.go:44	0x89dc4d		488d7280		LEAQ -0x80(DX), SI									
  keybuilder.go:44	0x89dc51		4889f7			MOVQ SI, DI										
  keybuilder.go:44	0x89dc54		48f7de			NEGQ SI											
  keybuilder.go:44	0x89dc57		4839f1			CMPQ CX, SI										
  keybuilder.go:44	0x89dc5a		7f4f			JG 0x89dcab										
  keybuilder.go:44	0x89dc5c		0f1f4000		NOPL 0(AX)										
  keybuilder.go:45	0x89dc60		4881fa80000000		CMPQ DX, $0x80										
  keybuilder.go:45	0x89dc67		775c			JA 0x89dcc5										
  keybuilder.go:44	0x89dc69		4839f1			CMPQ CX, SI										
  keybuilder.go:45	0x89dc6c		480f4cf1		CMOVL CX, SI										
  keybuilder.go:45	0x89dc70		48c1ff3f		SARQ $0x3f, DI										
  keybuilder.go:45	0x89dc74		4821fa			ANDQ DI, DX										
  keybuilder.go:45	0x89dc77		4801c2			ADDQ AX, DX										
  keybuilder.go:45	0x89dc7a		4839d3			CMPQ BX, DX										
  keybuilder.go:45	0x89dc7d		741f			JE 0x89dc9e										
  keybuilder.go:44	0x89dc7f		4889442430		MOVQ AX, 0x30(SP)									
  keybuilder.go:45	0x89dc84		4889742418		MOVQ SI, 0x18(SP)									
  keybuilder.go:45	0x89dc89		4889d0			MOVQ DX, AX										
  keybuilder.go:45	0x89dc8c		4889f1			MOVQ SI, CX										
  keybuilder.go:45	0x89dc8f		e8ac3fbfff		CALL runtime.memmove(SB)								
  keybuilder.go:45	0x89dc94		488b442430		MOVQ 0x30(SP), AX									
  keybuilder.go:45	0x89dc99		488b742418		MOVQ 0x18(SP), SI									
  keybuilder.go:45	0x89dc9e		4801b080000000		ADDQ SI, 0x80(AX)									
  keybuilder.go:46	0x89dca5		4883c420		ADDQ $0x20, SP										
  keybuilder.go:46	0x89dca9		5d			POPQ BP											
  keybuilder.go:46	0x89dcaa		c3			RET											
  keybuilder.go:48	0x89dcab		e8b0feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	
  hasher.go:97		0x89dcb0		488b5c2438		MOVQ 0x38(SP), BX									
  hasher.go:97		0x89dcb5		488b4c2440		MOVQ 0x40(SP), CX									
  hasher.go:97		0x89dcba		e8c166d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:49	0x89dcbf		4883c420		ADDQ $0x20, SP										
  keybuilder.go:49	0x89dcc3		5d			POPQ BP											
  keybuilder.go:49	0x89dcc4		c3			RET											
  keybuilder.go:45	0x89dcc5		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:45	0x89dccc		e8cf3bbfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:45	0x89dcd1		90			NOPL											
  keybuilder.go:43	0x89dcd2		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:43	0x89dcd7		48895c2410		MOVQ BX, 0x10(SP)									
  keybuilder.go:43	0x89dcdc		48894c2418		MOVQ CX, 0x18(SP)									
  keybuilder.go:43	0x89dce1		e81a1dbfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:43	0x89dce6		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:43	0x89dceb		488b5c2410		MOVQ 0x10(SP), BX									
  keybuilder.go:43	0x89dcf0		488b4c2418		MOVQ 0x18(SP), CX									
  keybuilder.go:43	0x89dcf5		e926ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:80	0x89dd00		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:80	0x89dd04		7630			JBE 0x89dd36											
  keybuilder.go:80	0x89dd06		55			PUSHQ BP											
  keybuilder.go:80	0x89dd07		4889e5			MOVQ SP, BP											
  keybuilder.go:80	0x89dd0a		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:82	0x89dd0e		885c2438		MOVB BL, 0x38(SP)										
  keybuilder.go:81	0x89dd12		e849feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  keybuilder.go:81	0x89dd17		0fb64c2438		MOVZX 0x38(SP), CX										
  keybuilder.go:81	0x89dd1c		884c241f		MOVB CL, 0x1f(SP)										
  hasher.go:90		0x89dd20		90			NOPL												
  hasher.go:103		0x89dd21		488d5c241f		LEAQ 0x1f(SP), BX										
  hasher.go:103		0x89dd26		b901000000		MOVL $0x1, CX											
  hasher.go:103		0x89dd2b		e85066d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:82	0x89dd30		4883c420		ADDQ $0x20, SP											
  keybuilder.go:82	0x89dd34		5d			POPQ BP												
  keybuilder.go:82	0x89dd35		c3			RET												
  keybuilder.go:80	0x89dd36		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:80	0x89dd3b		885c2410		MOVB BL, 0x10(SP)										
  keybuilder.go:80	0x89dd3f		90			NOPL												
  keybuilder.go:80	0x89dd40		e8bb1cbfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:80	0x89dd45		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:80	0x89dd4a		0fb65c2410		MOVZX 0x10(SP), BX										
  keybuilder.go:80	0x89dd4f		ebaf			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:84	0x89dd60		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:84	0x89dd64		7628			JBE 0x89dd8e											
  keybuilder.go:84	0x89dd66		55			PUSHQ BP											
  keybuilder.go:84	0x89dd67		4889e5			MOVQ SP, BP											
  keybuilder.go:84	0x89dd6a		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:86	0x89dd6e		90			NOPL												
  binary.go:98		0x89dd6f		895c241c		MOVL BX, 0x1c(SP)										
  keybuilder.go:87	0x89dd73		e8e8fdffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  hasher.go:90		0x89dd78		90			NOPL												
  hasher.go:103		0x89dd79		488d5c241c		LEAQ 0x1c(SP), BX										
  hasher.go:103		0x89dd7e		b904000000		MOVL $0x4, CX											
  hasher.go:103		0x89dd83		e8f865d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:88	0x89dd88		4883c420		ADDQ $0x20, SP											
  keybuilder.go:88	0x89dd8c		5d			POPQ BP												
  keybuilder.go:88	0x89dd8d		c3			RET												
  keybuilder.go:84	0x89dd8e		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:84	0x89dd93		895c2410		MOVL BX, 0x10(SP)										
  keybuilder.go:84	0x89dd97		e8641cbfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:84	0x89dd9c		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:84	0x89dda1		8b5c2410		MOVL 0x10(SP), BX										
  keybuilder.go:84	0x89dda5		ebb9			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:90	0x89ddc0		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:90	0x89ddc4		7629			JBE 0x89ddef											
  keybuilder.go:90	0x89ddc6		55			PUSHQ BP											
  keybuilder.go:90	0x89ddc7		4889e5			MOVQ SP, BP											
  keybuilder.go:90	0x89ddca		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:92	0x89ddce		90			NOPL												
  binary.go:124		0x89ddcf		48895c2418		MOVQ BX, 0x18(SP)										
  keybuilder.go:93	0x89ddd4		e887fdffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  hasher.go:90		0x89ddd9		90			NOPL												
  hasher.go:103		0x89ddda		488d5c2418		LEAQ 0x18(SP), BX										
  hasher.go:103		0x89dddf		b908000000		MOVL $0x8, CX											
  hasher.go:103		0x89dde4		e89765d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:94	0x89dde9		4883c420		ADDQ $0x20, SP											
  keybuilder.go:94	0x89dded		5d			POPQ BP												
  keybuilder.go:94	0x89ddee		c3			RET												
  keybuilder.go:90	0x89ddef		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:90	0x89ddf4		48895c2410		MOVQ BX, 0x10(SP)										
  keybuilder.go:90	0x89ddf9		e8021cbfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:90	0x89ddfe		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:90	0x89de03		488b5c2410		MOVQ 0x10(SP), BX										
  keybuilder.go:90	0x89de08		ebb6			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB)	
