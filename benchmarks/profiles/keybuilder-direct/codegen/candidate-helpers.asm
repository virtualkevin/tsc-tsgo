TEXT github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17372	0x805640		4c8d6424c8		LEAQ -0x38(SP), R12									
  checker.go:17372	0x805645		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17372	0x805649		766d			JBE 0x8056b8										
  checker.go:17372	0x80564b		55			PUSHQ BP										
  checker.go:17372	0x80564c		4889e5			MOVQ SP, BP										
  checker.go:17372	0x80564f		4881ecb0000000		SUBQ $0xb0, SP										
  checker.go:17372	0x805656		48898424c0000000	MOVQ AX, 0xc0(SP)									
  checker.go:17373	0x80565e		488d542420		LEAQ 0x20(SP), DX									
  checker.go:17373	0x805663		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17373	0x805667		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17373	0x80566c		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17373	0x805671		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17373	0x805676		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17373	0x80567b		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17373	0x805680		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17373	0x805685		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17373	0x80568a		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17374	0x805692		4889cf			MOVQ CX, DI										
  checker.go:17374	0x805695		4889d9			MOVQ BX, CX										
  checker.go:17374	0x805698		4889c3			MOVQ AX, BX										
  checker.go:17374	0x80569b		4889d0			MOVQ DX, AX										
  checker.go:17374	0x80569e		6690			NOPW											
  checker.go:17374	0x8056a0		e87bf9ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17375	0x8056a5		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17375	0x8056aa		e811780900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17375	0x8056af		4881c4b0000000		ADDQ $0xb0, SP										
  checker.go:17375	0x8056b6		5d			POPQ BP											
  checker.go:17375	0x8056b7		c3			RET											
  checker.go:17372	0x8056b8		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17372	0x8056bd		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17372	0x8056c2		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17372	0x8056c7		e834a3c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17372	0x8056cc		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17372	0x8056d1		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17372	0x8056d6		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17372	0x8056db		0f1f440000		NOPL 0(AX)(AX*1)									
  checker.go:17372	0x8056e0		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.getTypeListKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17456	0x805d20		4c8d6424d8		LEAQ -0x28(SP), R12									
  checker.go:17456	0x805d25		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17456	0x805d29		0f86ae000000		JBE 0x805ddd										
  checker.go:17456	0x805d2f		55			PUSHQ BP										
  checker.go:17456	0x805d30		4889e5			MOVQ SP, BP										
  checker.go:17456	0x805d33		4881eca0000000		SUBQ $0xa0, SP										
  checker.go:17462	0x805d3a		48899c24b8000000	MOVQ BX, 0xb8(SP)									
  checker.go:17462	0x805d42		898c24c0000000		MOVL CX, 0xc0(SP)									
  checker.go:17462	0x805d49		4889bc24c8000000	MOVQ DI, 0xc8(SP)									
  checker.go:17457	0x805d51		488d4c2410		LEAQ 0x10(SP), CX									
  checker.go:17457	0x805d56		440f1139		MOVUPS X15, 0(CX)									
  checker.go:17457	0x805d5a		440f117910		MOVUPS X15, 0x10(CX)									
  checker.go:17457	0x805d5f		440f117920		MOVUPS X15, 0x20(CX)									
  checker.go:17457	0x805d64		440f117930		MOVUPS X15, 0x30(CX)									
  checker.go:17457	0x805d69		440f117940		MOVUPS X15, 0x40(CX)									
  checker.go:17457	0x805d6e		440f117950		MOVUPS X15, 0x50(CX)									
  checker.go:17457	0x805d73		440f117960		MOVUPS X15, 0x60(CX)									
  checker.go:17457	0x805d78		440f117970		MOVUPS X15, 0x70(CX)									
  checker.go:17457	0x805d7d		440f11b980000000	MOVUPS X15, 0x80(CX)									
  checker.go:17307	0x805d85		8b5808			MOVL 0x8(AX), BX									
  checker.go:17458	0x805d88		90			NOPL											
  checker.go:17307	0x805d89		4889c8			MOVQ CX, AX										
  checker.go:17307	0x805d8c		e8cf730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)	
  checker.go:17307	0x805d91		488b8c24b8000000	MOVQ 0xb8(SP), CX									
  checker.go:17307	0x805d99		8b5908			MOVL 0x8(CX), BX									
  checker.go:17459	0x805d9c		90			NOPL											
  checker.go:17307	0x805d9d		488d442410		LEAQ 0x10(SP), AX									
  checker.go:17307	0x805da2		e8b9730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)	
  checker.go:17460	0x805da7		488d442410		LEAQ 0x10(SP), AX									
  checker.go:17460	0x805dac		8b9c24c0000000		MOVL 0xc0(SP), BX									
  checker.go:17460	0x805db3		e8a8730900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)	
  checker.go:17461	0x805db8		488d442410		LEAQ 0x10(SP), AX									
  checker.go:17461	0x805dbd		488b9c24c8000000	MOVQ 0xc8(SP), BX									
  checker.go:17461	0x805dc5		e8f6f2ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)	
  checker.go:17462	0x805dca		488d442410		LEAQ 0x10(SP), AX									
  checker.go:17462	0x805dcf		e8ec700900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17462	0x805dd4		4881c4a0000000		ADDQ $0xa0, SP										
  checker.go:17462	0x805ddb		5d			POPQ BP											
  checker.go:17462	0x805ddc		c3			RET											
  checker.go:17456	0x805ddd		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17456	0x805de2		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17456	0x805de7		894c2418		MOVL CX, 0x18(SP)									
  checker.go:17456	0x805deb		48897c2420		MOVQ DI, 0x20(SP)									
  checker.go:17456	0x805df0		e80b9cc8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17456	0x805df5		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17456	0x805dfa		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17456	0x805dff		8b4c2418		MOVL 0x18(SP), CX									
  checker.go:17456	0x805e03		488b7c2420		MOVQ 0x20(SP), DI									
  checker.go:17456	0x805e08		e913ffffff		JMP github.com/microsoft/typescript-go/internal/checker.getIndexedAccessKey(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17479	0x805fc0		4c8d6424c8		LEAQ -0x38(SP), R12									
  checker.go:17479	0x805fc5		4d3b6610		CMPQ R12, 0x10(R14)									
  checker.go:17479	0x805fc9		0f86a9000000		JBE 0x806078										
  checker.go:17479	0x805fcf		55			PUSHQ BP										
  checker.go:17479	0x805fd0		4889e5			MOVQ SP, BP										
  checker.go:17479	0x805fd3		4881ecb0000000		SUBQ $0xb0, SP										
  checker.go:17479	0x805fda		48898424c0000000	MOVQ AX, 0xc0(SP)									
  checker.go:17483	0x805fe2		4889bc24d8000000	MOVQ DI, 0xd8(SP)									
  checker.go:17483	0x805fea		4088b424e0000000	MOVB SI, 0xe0(SP)									
  checker.go:17480	0x805ff2		488d542420		LEAQ 0x20(SP), DX									
  checker.go:17480	0x805ff7		440f113a		MOVUPS X15, 0(DX)									
  checker.go:17480	0x805ffb		440f117a10		MOVUPS X15, 0x10(DX)									
  checker.go:17480	0x806000		440f117a20		MOVUPS X15, 0x20(DX)									
  checker.go:17480	0x806005		440f117a30		MOVUPS X15, 0x30(DX)									
  checker.go:17480	0x80600a		440f117a40		MOVUPS X15, 0x40(DX)									
  checker.go:17480	0x80600f		440f117a50		MOVUPS X15, 0x50(DX)									
  checker.go:17480	0x806014		440f117a60		MOVUPS X15, 0x60(DX)									
  checker.go:17480	0x806019		440f117a70		MOVUPS X15, 0x70(DX)									
  checker.go:17480	0x80601e		440f11ba80000000	MOVUPS X15, 0x80(DX)									
  checker.go:17481	0x806026		4889cf			MOVQ CX, DI										
  checker.go:17481	0x806029		4889d9			MOVQ BX, CX										
  checker.go:17481	0x80602c		4889c3			MOVQ AX, BX										
  checker.go:17481	0x80602f		4889d0			MOVQ DX, AX										
  checker.go:17481	0x806032		e8e9efffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeTypes(SB)	
  checker.go:17482	0x806037		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17482	0x80603c		488b9c24d8000000	MOVQ 0xd8(SP), BX									
  checker.go:17482	0x806044		e877f0ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)	
  checker.go:17483	0x806049		0fb69424e0000000	MOVZX 0xe0(SP), DX									
  checker.go:17483	0x806051		84d2			TESTL DL, DL										
  checker.go:17483	0x806053		7410			JE 0x806065										
  checker.go:17484	0x806055		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17484	0x80605a		bb21000000		MOVL $0x21, BX										
  checker.go:17484	0x80605f		90			NOPL											
  checker.go:17484	0x806060		e87b700900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)	
  checker.go:17486	0x806065		488d442420		LEAQ 0x20(SP), AX									
  checker.go:17486	0x80606a		e8516e0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)		
  checker.go:17486	0x80606f		4881c4b0000000		ADDQ $0xb0, SP										
  checker.go:17486	0x806076		5d			POPQ BP											
  checker.go:17486	0x806077		c3			RET											
  checker.go:17479	0x806078		4889442408		MOVQ AX, 0x8(SP)									
  checker.go:17479	0x80607d		48895c2410		MOVQ BX, 0x10(SP)									
  checker.go:17479	0x806082		48894c2418		MOVQ CX, 0x18(SP)									
  checker.go:17479	0x806087		48897c2420		MOVQ DI, 0x20(SP)									
  checker.go:17479	0x80608c		4088742428		MOVB SI, 0x28(SP)									
  checker.go:17479	0x806091		e86a99c8ff		CALL runtime.morestack_noctxt.abi0(SB)							
  checker.go:17479	0x806096		488b442408		MOVQ 0x8(SP), AX									
  checker.go:17479	0x80609b		488b5c2410		MOVQ 0x10(SP), BX									
  checker.go:17479	0x8060a0		488b4c2418		MOVQ 0x18(SP), CX									
  checker.go:17479	0x8060a5		488b7c2420		MOVQ 0x20(SP), DI									
  checker.go:17479	0x8060aa		0fb6742428		MOVZX 0x28(SP), SI									
  checker.go:17479	0x8060af		e90cffffff		JMP github.com/microsoft/typescript-go/internal/checker.getConditionalTypeKey(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:17489	0x8060c0		4c8d6424b0		LEAQ -0x50(SP), R12											
  checker.go:17489	0x8060c5		4d3b6610		CMPQ R12, 0x10(R14)											
  checker.go:17489	0x8060c9		0f8626010000		JBE 0x8061f5												
  checker.go:17489	0x8060cf		55			PUSHQ BP												
  checker.go:17489	0x8060d0		4889e5			MOVQ SP, BP												
  checker.go:17489	0x8060d3		4881ecc8000000		SUBQ $0xc8, SP												
  checker.go:17490	0x8060da		898c24e8000000		MOVL CX, 0xe8(SP)											
  checker.go:17490	0x8060e1		4088b424ed000000	MOVB SI, 0xed(SP)											
  checker.go:17490	0x8060e9		4084ff			TESTL DI, DI												
  checker.go:17490	0x8060ec		7414			JE 0x806102												
  checker.go:17490	0x8060ee		8b5008			MOVL 0x8(AX), DX											
  checker.go:17490	0x8060f1		395308			CMPL 0x8(BX), DX											
  checker.go:17490	0x8060f4		7215			JB 0x80610b												
  checker.go:17493	0x8060f6		4889da			MOVQ BX, DX												
  checker.go:17493	0x8060f9		4889c3			MOVQ AX, BX												
  checker.go:17493	0x8060fc		4889d0			MOVQ DX, AX												
  checker.go:17493	0x8060ff		90			NOPL													
  checker.go:17490	0x806100		eb09			JMP 0x80610b												
  checker.go:17493	0x806102		4889da			MOVQ BX, DX												
  checker.go:17493	0x806105		4889c3			MOVQ AX, BX												
  checker.go:17493	0x806108		4889d0			MOVQ DX, AX												
  checker.go:17493	0x80610b		48895c2430		MOVQ BX, 0x30(SP)											
  checker.go:17493	0x806110		4889442428		MOVQ AX, 0x28(SP)											
  checker.go:17493	0x806115		488d4c2438		LEAQ 0x38(SP), CX											
  checker.go:17493	0x80611a		440f1139		MOVUPS X15, 0(CX)											
  checker.go:17493	0x80611e		440f117910		MOVUPS X15, 0x10(CX)											
  checker.go:17493	0x806123		440f117920		MOVUPS X15, 0x20(CX)											
  checker.go:17493	0x806128		440f117930		MOVUPS X15, 0x30(CX)											
  checker.go:17493	0x80612d		440f117940		MOVUPS X15, 0x40(CX)											
  checker.go:17493	0x806132		440f117950		MOVUPS X15, 0x50(CX)											
  checker.go:17493	0x806137		440f117960		MOVUPS X15, 0x60(CX)											
  checker.go:17493	0x80613c		440f117970		MOVUPS X15, 0x70(CX)											
  checker.go:17493	0x806141		440f11b980000000	MOVUPS X15, 0x80(CX)											
  checker.go:17495	0x806149		4889d8			MOVQ BX, AX												
  checker.go:17495	0x80614c		e8ef000000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x806151		84c0			TESTL AL, AL												
  checker.go:17495	0x806153		740f			JE 0x806164												
  checker.go:17495	0x806155		488b442428		MOVQ 0x28(SP), AX											
  checker.go:17495	0x80615a		e8e1000000		CALL github.com/microsoft/typescript-go/internal/checker.isTypeReferenceWithGenericArguments(SB)	
  checker.go:17495	0x80615f		90			NOPL													
  checker.go:17495	0x806160		84c0			TESTL AL, AL												
  checker.go:17495	0x806162		7539			JNE 0x80619d												
  checker.go:17499	0x806164		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17499	0x806169		bb73000000		MOVL $0x73, BX												
  checker.go:17499	0x80616e		e86d6f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)			
  checker.go:17307	0x806173		488b4c2430		MOVQ 0x30(SP), CX											
  checker.go:17307	0x806178		8b5908			MOVL 0x8(CX), BX											
  checker.go:17500	0x80617b		90			NOPL													
  checker.go:17307	0x80617c		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17307	0x806181		e8da6f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)			
  checker.go:17307	0x806186		488b4c2428		MOVQ 0x28(SP), CX											
  checker.go:17307	0x80618b		8b5908			MOVL 0x8(CX), BX											
  checker.go:17501	0x80618e		90			NOPL													
  checker.go:17307	0x80618f		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17307	0x806194		e8c76f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)			
  checker.go:17307	0x806199		31c0			XORL AX, AX												
  checker.go:17503	0x80619b		eb2b			JMP 0x8061c8												
  checker.go:17496	0x80619d		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17496	0x8061a2		bb67000000		MOVL $0x67, BX												
  checker.go:17496	0x8061a7		e8346f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)			
  checker.go:17497	0x8061ac		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17497	0x8061b1		488b5c2430		MOVQ 0x30(SP), BX											
  checker.go:17497	0x8061b6		488b4c2428		MOVQ 0x28(SP), CX											
  checker.go:17497	0x8061bb		0fb6bc24ed000000	MOVZX 0xed(SP), DI											
  checker.go:17497	0x8061c3		e898efffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeGenericTypeReferences(SB)	
  checker.go:17503	0x8061c8		88442427		MOVB AL, 0x27(SP)											
  checker.go:17503	0x8061cc		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17503	0x8061d1		8b9c24e8000000		MOVL 0xe8(SP), BX											
  checker.go:17503	0x8061d8		e8836f0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)			
  checker.go:17504	0x8061dd		488d442438		LEAQ 0x38(SP), AX											
  checker.go:17504	0x8061e2		e8d96c0900		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)				
  checker.go:17504	0x8061e7		0fb64c2427		MOVZX 0x27(SP), CX											
  checker.go:17504	0x8061ec		4881c4c8000000		ADDQ $0xc8, SP												
  checker.go:17504	0x8061f3		5d			POPQ BP													
  checker.go:17504	0x8061f4		c3			RET													
  checker.go:17489	0x8061f5		4889442408		MOVQ AX, 0x8(SP)											
  checker.go:17489	0x8061fa		48895c2410		MOVQ BX, 0x10(SP)											
  checker.go:17489	0x8061ff		894c2418		MOVL CX, 0x18(SP)											
  checker.go:17489	0x806203		40887c241c		MOVB DI, 0x1c(SP)											
  checker.go:17489	0x806208		408874241d		MOVB SI, 0x1d(SP)											
  checker.go:17489	0x80620d		e8ee97c8ff		CALL runtime.morestack_noctxt.abi0(SB)									
  checker.go:17489	0x806212		488b442408		MOVQ 0x8(SP), AX											
  checker.go:17489	0x806217		488b5c2410		MOVQ 0x10(SP), BX											
  checker.go:17489	0x80621c		8b4c2418		MOVL 0x18(SP), CX											
  checker.go:17489	0x806220		0fb67c241c		MOVZX 0x1c(SP), DI											
  checker.go:17489	0x806225		0fb674241d		MOVZX 0x1d(SP), SI											
  checker.go:17489	0x80622a		e991feffff		JMP github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)				

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:18	0x89cec0		493b6610		CMPQ SP, 0x10(R14)								
  keybuilder.go:18	0x89cec4		764a			JBE 0x89cf10									
  keybuilder.go:18	0x89cec6		55			PUSHQ BP									
  keybuilder.go:18	0x89cec7		4889e5			MOVQ SP, BP									
  keybuilder.go:18	0x89ceca		4883ec10		SUBQ $0x10, SP									
  keybuilder.go:19	0x89cece		488b8888000000		MOVQ 0x88(AX), CX								
  keybuilder.go:19	0x89ced5		4885c9			TESTQ CX, CX									
  keybuilder.go:19	0x89ced8		751b			JNE 0x89cef5									
  keybuilder.go:22	0x89ceda		488b9880000000		MOVQ 0x80(AX), BX								
  keybuilder.go:22	0x89cee1		4881fb80000000		CMPQ BX, $0x80									
  keybuilder.go:22	0x89cee8		7719			JA 0x89cf03									
  hash128.go:9		0x89ceea		e8d148d0ff		CALL github.com/zeebo/xxh3.hashAny128(SB)					
  keybuilder.go:22	0x89ceef		4883c410		ADDQ $0x10, SP									
  keybuilder.go:22	0x89cef3		5d			POPQ BP										
  keybuilder.go:22	0x89cef4		c3			RET										
  keybuilder.go:20	0x89cef5		4889c8			MOVQ CX, AX									
  keybuilder.go:20	0x89cef8		e8637bd0ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)					
  keybuilder.go:20	0x89cefd		4883c410		ADDQ $0x10, SP									
  keybuilder.go:20	0x89cf01		5d			POPQ BP										
  keybuilder.go:20	0x89cf02		c3			RET										
  keybuilder.go:22	0x89cf03		48c7c080000000		MOVQ $0x80, AX									
  keybuilder.go:22	0x89cf0a		e89149bfff		CALL runtime.panicBounds(SB)							
  keybuilder.go:22	0x89cf0f		90			NOPL										
  keybuilder.go:18	0x89cf10		4889442408		MOVQ AX, 0x8(SP)								
  keybuilder.go:18	0x89cf15		e8e62abfff		CALL runtime.morestack_noctxt.abi0(SB)						
  keybuilder.go:18	0x89cf1a		488b442408		MOVQ 0x8(SP), AX								
  keybuilder.go:18	0x89cf1f		90			NOPL										
  keybuilder.go:18	0x89cf20		eb9e			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:25	0x89cf40		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:25	0x89cf44		0f8687000000		JBE 0x89cfd1										
  keybuilder.go:25	0x89cf4a		55			PUSHQ BP										
  keybuilder.go:25	0x89cf4b		4889e5			MOVQ SP, BP										
  keybuilder.go:25	0x89cf4e		4883ec18		SUBQ $0x18, SP										
  keybuilder.go:26	0x89cf52		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:26	0x89cf5a		755b			JNE 0x89cfb7										
  keybuilder.go:26	0x89cf5c		4889442428		MOVQ AX, 0x28(SP)									
  keybuilder.go:27	0x89cf61		488d05389c5f00		LEAQ 0x5f9c38(IP), AX									
  keybuilder.go:27	0x89cf68		e8d36fb8ff		CALL runtime.newobject(SB)								
  keybuilder.go:27	0x89cf6d		833d9c75650100		CMPL runtime.writeBarrier(SB), $0x0							
  keybuilder.go:27	0x89cf74		7507			JNE 0x89cf7d										
  keybuilder.go:27	0x89cf76		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:27	0x89cf7b		eb18			JMP 0x89cf95										
  keybuilder.go:27	0x89cf7d		488b5c2428		MOVQ 0x28(SP), BX									
  keybuilder.go:27	0x89cf82		488b9388000000		MOVQ 0x88(BX), DX									
  keybuilder.go:27	0x89cf89		e87245bfff		CALL runtime.gcWriteBarrier2(SB)							
  keybuilder.go:27	0x89cf8e		498903			MOVQ AX, 0(R11)										
  keybuilder.go:27	0x89cf91		49895308		MOVQ DX, 0x8(R11)									
  keybuilder.go:27	0x89cf95		48898388000000		MOVQ AX, 0x88(BX)									
  keybuilder.go:28	0x89cf9c		488b8b80000000		MOVQ 0x80(BX), CX									
  keybuilder.go:28	0x89cfa3		4881f980000000		CMPQ CX, $0x80										
  keybuilder.go:28	0x89cfaa		7718			JA 0x89cfc4										
  hasher.go:90		0x89cfac		90			NOPL											
  hasher.go:103		0x89cfad		e8ce73d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:30	0x89cfb2		488b442428		MOVQ 0x28(SP), AX									
  keybuilder.go:30	0x89cfb7		488b8088000000		MOVQ 0x88(AX), AX									
  keybuilder.go:30	0x89cfbe		4883c418		ADDQ $0x18, SP										
  keybuilder.go:30	0x89cfc2		5d			POPQ BP											
  keybuilder.go:30	0x89cfc3		c3			RET											
  keybuilder.go:28	0x89cfc4		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:28	0x89cfcb		e8d048bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:28	0x89cfd0		90			NOPL											
  keybuilder.go:25	0x89cfd1		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:25	0x89cfd6		e8252abfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:25	0x89cfdb		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:25	0x89cfe0		e95bffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:41	0x89d000		493b6610		CMPQ SP, 0x10(R14)									
  keybuilder.go:41	0x89d004		0f86a8000000		JBE 0x89d0b2										
  keybuilder.go:41	0x89d00a		55			PUSHQ BP										
  keybuilder.go:41	0x89d00b		4889e5			MOVQ SP, BP										
  keybuilder.go:41	0x89d00e		4883ec20		SUBQ $0x20, SP										
  keybuilder.go:42	0x89d012		48894c2440		MOVQ CX, 0x40(SP)									
  keybuilder.go:42	0x89d017		48895c2438		MOVQ BX, 0x38(SP)									
  keybuilder.go:42	0x89d01c		4883b88800000000	CMPQ 0x88(AX), $0x0									
  keybuilder.go:42	0x89d024		7565			JNE 0x89d08b										
  keybuilder.go:42	0x89d026		488b9080000000		MOVQ 0x80(AX), DX									
  keybuilder.go:42	0x89d02d		488d7280		LEAQ -0x80(DX), SI									
  keybuilder.go:42	0x89d031		4889f7			MOVQ SI, DI										
  keybuilder.go:42	0x89d034		48f7de			NEGQ SI											
  keybuilder.go:42	0x89d037		4839f1			CMPQ CX, SI										
  keybuilder.go:42	0x89d03a		7f4f			JG 0x89d08b										
  keybuilder.go:42	0x89d03c		0f1f4000		NOPL 0(AX)										
  keybuilder.go:43	0x89d040		4881fa80000000		CMPQ DX, $0x80										
  keybuilder.go:43	0x89d047		775c			JA 0x89d0a5										
  keybuilder.go:42	0x89d049		4839f1			CMPQ CX, SI										
  keybuilder.go:43	0x89d04c		480f4cf1		CMOVL CX, SI										
  keybuilder.go:43	0x89d050		48c1ff3f		SARQ $0x3f, DI										
  keybuilder.go:43	0x89d054		4821fa			ANDQ DI, DX										
  keybuilder.go:43	0x89d057		4801c2			ADDQ AX, DX										
  keybuilder.go:43	0x89d05a		4839d3			CMPQ BX, DX										
  keybuilder.go:43	0x89d05d		741f			JE 0x89d07e										
  keybuilder.go:42	0x89d05f		4889442430		MOVQ AX, 0x30(SP)									
  keybuilder.go:43	0x89d064		4889742418		MOVQ SI, 0x18(SP)									
  keybuilder.go:43	0x89d069		4889d0			MOVQ DX, AX										
  keybuilder.go:43	0x89d06c		4889f1			MOVQ SI, CX										
  keybuilder.go:43	0x89d06f		e8cc4bbfff		CALL runtime.memmove(SB)								
  keybuilder.go:43	0x89d074		488b442430		MOVQ 0x30(SP), AX									
  keybuilder.go:43	0x89d079		488b742418		MOVQ 0x18(SP), SI									
  keybuilder.go:43	0x89d07e		4801b080000000		ADDQ SI, 0x80(AX)									
  keybuilder.go:44	0x89d085		4883c420		ADDQ $0x20, SP										
  keybuilder.go:44	0x89d089		5d			POPQ BP											
  keybuilder.go:44	0x89d08a		c3			RET											
  keybuilder.go:46	0x89d08b		e8b0feffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)	
  hasher.go:97		0x89d090		488b5c2438		MOVQ 0x38(SP), BX									
  hasher.go:97		0x89d095		488b4c2440		MOVQ 0x40(SP), CX									
  hasher.go:97		0x89d09a		e8e172d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)					
  keybuilder.go:47	0x89d09f		4883c420		ADDQ $0x20, SP										
  keybuilder.go:47	0x89d0a3		5d			POPQ BP											
  keybuilder.go:47	0x89d0a4		c3			RET											
  keybuilder.go:43	0x89d0a5		48c7c080000000		MOVQ $0x80, AX										
  keybuilder.go:43	0x89d0ac		e8ef47bfff		CALL runtime.panicBounds(SB)								
  keybuilder.go:43	0x89d0b1		90			NOPL											
  keybuilder.go:41	0x89d0b2		4889442408		MOVQ AX, 0x8(SP)									
  keybuilder.go:41	0x89d0b7		48895c2410		MOVQ BX, 0x10(SP)									
  keybuilder.go:41	0x89d0bc		48894c2418		MOVQ CX, 0x18(SP)									
  keybuilder.go:41	0x89d0c1		e83a29bfff		CALL runtime.morestack_noctxt.abi0(SB)							
  keybuilder.go:41	0x89d0c6		488b442408		MOVQ 0x8(SP), AX									
  keybuilder.go:41	0x89d0cb		488b5c2410		MOVQ 0x10(SP), BX									
  keybuilder.go:41	0x89d0d0		488b4c2418		MOVQ 0x18(SP), CX									
  keybuilder.go:41	0x89d0d5		e926ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeString(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:49	0x89d0e0		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:49	0x89d0e4		7652			JBE 0x89d138											
  keybuilder.go:49	0x89d0e6		55			PUSHQ BP											
  keybuilder.go:49	0x89d0e7		4889e5			MOVQ SP, BP											
  keybuilder.go:49	0x89d0ea		4883ec10		SUBQ $0x10, SP											
  keybuilder.go:50	0x89d0ee		4883b88800000000	CMPQ 0x88(AX), $0x0										
  keybuilder.go:50	0x89d0f6		7523			JNE 0x89d11b											
  keybuilder.go:50	0x89d0f8		488b8880000000		MOVQ 0x80(AX), CX										
  keybuilder.go:50	0x89d0ff		90			NOPL												
  keybuilder.go:50	0x89d100		4883f97f		CMPQ CX, $0x7f											
  keybuilder.go:50	0x89d104		7f15			JG 0x89d11b											
  keybuilder.go:51	0x89d106		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:51	0x89d10d		731c			JAE 0x89d12b											
  keybuilder.go:51	0x89d10f		881c08			MOVB BL, 0(AX)(CX*1)										
  keybuilder.go:52	0x89d112		48ff8080000000		INCQ 0x80(AX)											
  keybuilder.go:52	0x89d119		eb0a			JMP 0x89d125											
  keybuilder.go:54	0x89d11b		0f1f440000		NOPL 0(AX)(AX*1)										
  keybuilder.go:54	0x89d120		e83b010000		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	
  keybuilder.go:56	0x89d125		4883c410		ADDQ $0x10, SP											
  keybuilder.go:56	0x89d129		5d			POPQ BP												
  keybuilder.go:56	0x89d12a		c3			RET												
  keybuilder.go:51	0x89d12b		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:51	0x89d132		e86947bfff		CALL runtime.panicBounds(SB)									
  keybuilder.go:51	0x89d137		90			NOPL												
  keybuilder.go:49	0x89d138		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:49	0x89d13d		885c2410		MOVB BL, 0x10(SP)										
  keybuilder.go:49	0x89d141		e8ba28bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:49	0x89d146		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:49	0x89d14b		0fb65c2410		MOVZX 0x10(SP), BX										
  keybuilder.go:49	0x89d150		eb8e			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByte(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:58	0x89d160		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:58	0x89d164		7652			JBE 0x89d1b8											
  keybuilder.go:58	0x89d166		55			PUSHQ BP											
  keybuilder.go:58	0x89d167		4889e5			MOVQ SP, BP											
  keybuilder.go:58	0x89d16a		4883ec10		SUBQ $0x10, SP											
  keybuilder.go:59	0x89d16e		4883b88800000000	CMPQ 0x88(AX), $0x0										
  keybuilder.go:59	0x89d176		7524			JNE 0x89d19c											
  keybuilder.go:59	0x89d178		488b8880000000		MOVQ 0x80(AX), CX										
  keybuilder.go:59	0x89d17f		90			NOPL												
  keybuilder.go:59	0x89d180		4883f97c		CMPQ CX, $0x7c											
  keybuilder.go:59	0x89d184		7f16			JG 0x89d19c											
  keybuilder.go:60	0x89d186		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:60	0x89d18d		771c			JA 0x89d1ab											
  binary.go:98		0x89d18f		891c08			MOVL BX, 0(AX)(CX*1)										
  keybuilder.go:61	0x89d192		4883808000000004	ADDQ $0x4, 0x80(AX)										
  keybuilder.go:61	0x89d19a		eb09			JMP 0x89d1a5											
  keybuilder.go:63	0x89d19c		0f1f4000		NOPL 0(AX)											
  keybuilder.go:63	0x89d1a0		e81b010000		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)	
  keybuilder.go:65	0x89d1a5		4883c410		ADDQ $0x10, SP											
  keybuilder.go:65	0x89d1a9		5d			POPQ BP												
  keybuilder.go:65	0x89d1aa		c3			RET												
  keybuilder.go:60	0x89d1ab		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:60	0x89d1b2		e8e946bfff		CALL runtime.panicBounds(SB)									
  keybuilder.go:60	0x89d1b7		90			NOPL												
  keybuilder.go:58	0x89d1b8		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:58	0x89d1bd		895c2410		MOVL BX, 0x10(SP)										
  keybuilder.go:58	0x89d1c1		e83a28bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:58	0x89d1c6		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:58	0x89d1cb		8b5c2410		MOVL 0x10(SP), BX										
  keybuilder.go:58	0x89d1cf		eb8f			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:67	0x89d1e0		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:67	0x89d1e4		7652			JBE 0x89d238											
  keybuilder.go:67	0x89d1e6		55			PUSHQ BP											
  keybuilder.go:67	0x89d1e7		4889e5			MOVQ SP, BP											
  keybuilder.go:67	0x89d1ea		4883ec10		SUBQ $0x10, SP											
  keybuilder.go:68	0x89d1ee		4883b88800000000	CMPQ 0x88(AX), $0x0										
  keybuilder.go:68	0x89d1f6		7525			JNE 0x89d21d											
  keybuilder.go:68	0x89d1f8		488b8880000000		MOVQ 0x80(AX), CX										
  keybuilder.go:68	0x89d1ff		90			NOPL												
  keybuilder.go:68	0x89d200		4883f978		CMPQ CX, $0x78											
  keybuilder.go:68	0x89d204		7f17			JG 0x89d21d											
  keybuilder.go:69	0x89d206		4881f980000000		CMPQ CX, $0x80											
  keybuilder.go:69	0x89d20d		771c			JA 0x89d22b											
  binary.go:124		0x89d20f		48891c08		MOVQ BX, 0(AX)(CX*1)										
  keybuilder.go:70	0x89d213		4883808000000008	ADDQ $0x8, 0x80(AX)										
  keybuilder.go:70	0x89d21b		eb08			JMP 0x89d225											
  keybuilder.go:72	0x89d21d		0f1f00			NOPL 0(AX)											
  keybuilder.go:72	0x89d220		e8fb000000		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB)	
  keybuilder.go:74	0x89d225		4883c410		ADDQ $0x10, SP											
  keybuilder.go:74	0x89d229		5d			POPQ BP												
  keybuilder.go:74	0x89d22a		c3			RET												
  keybuilder.go:69	0x89d22b		48c7c080000000		MOVQ $0x80, AX											
  keybuilder.go:69	0x89d232		e86946bfff		CALL runtime.panicBounds(SB)									
  keybuilder.go:69	0x89d237		90			NOPL												
  keybuilder.go:67	0x89d238		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:67	0x89d23d		48895c2410		MOVQ BX, 0x10(SP)										
  keybuilder.go:67	0x89d242		e8b927bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:67	0x89d247		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:67	0x89d24c		488b5c2410		MOVQ 0x10(SP), BX										
  keybuilder.go:67	0x89d251		eb8d			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:78	0x89d260		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:78	0x89d264		7630			JBE 0x89d296											
  keybuilder.go:78	0x89d266		55			PUSHQ BP											
  keybuilder.go:78	0x89d267		4889e5			MOVQ SP, BP											
  keybuilder.go:78	0x89d26a		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:80	0x89d26e		885c2438		MOVB BL, 0x38(SP)										
  keybuilder.go:79	0x89d272		e8c9fcffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  keybuilder.go:79	0x89d277		0fb64c2438		MOVZX 0x38(SP), CX										
  keybuilder.go:79	0x89d27c		884c241f		MOVB CL, 0x1f(SP)										
  hasher.go:90		0x89d280		90			NOPL												
  hasher.go:103		0x89d281		488d5c241f		LEAQ 0x1f(SP), BX										
  hasher.go:103		0x89d286		b901000000		MOVL $0x1, CX											
  hasher.go:103		0x89d28b		e8f070d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:80	0x89d290		4883c420		ADDQ $0x20, SP											
  keybuilder.go:80	0x89d294		5d			POPQ BP												
  keybuilder.go:80	0x89d295		c3			RET												
  keybuilder.go:78	0x89d296		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:78	0x89d29b		885c2410		MOVB BL, 0x10(SP)										
  keybuilder.go:78	0x89d29f		90			NOPL												
  keybuilder.go:78	0x89d2a0		e85b27bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:78	0x89d2a5		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:78	0x89d2aa		0fb65c2410		MOVZX 0x10(SP), BX										
  keybuilder.go:78	0x89d2af		ebaf			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeByteOverflow(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:82	0x89d2c0		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:82	0x89d2c4		7628			JBE 0x89d2ee											
  keybuilder.go:82	0x89d2c6		55			PUSHQ BP											
  keybuilder.go:82	0x89d2c7		4889e5			MOVQ SP, BP											
  keybuilder.go:82	0x89d2ca		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:84	0x89d2ce		90			NOPL												
  binary.go:98		0x89d2cf		895c241c		MOVL BX, 0x1c(SP)										
  keybuilder.go:85	0x89d2d3		e868fcffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  hasher.go:90		0x89d2d8		90			NOPL												
  hasher.go:103		0x89d2d9		488d5c241c		LEAQ 0x1c(SP), BX										
  hasher.go:103		0x89d2de		b904000000		MOVL $0x4, CX											
  hasher.go:103		0x89d2e3		e89870d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:86	0x89d2e8		4883c420		ADDQ $0x20, SP											
  keybuilder.go:86	0x89d2ec		5d			POPQ BP												
  keybuilder.go:86	0x89d2ed		c3			RET												
  keybuilder.go:82	0x89d2ee		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:82	0x89d2f3		895c2410		MOVL BX, 0x10(SP)										
  keybuilder.go:82	0x89d2f7		e80427bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:82	0x89d2fc		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:82	0x89d301		8b5c2410		MOVL 0x10(SP), BX										
  keybuilder.go:82	0x89d305		ebb9			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32Overflow(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB) github.com/microsoft/typescript-go/internal/checker/keybuilder.go
  keybuilder.go:88	0x89d320		493b6610		CMPQ SP, 0x10(R14)										
  keybuilder.go:88	0x89d324		7629			JBE 0x89d34f											
  keybuilder.go:88	0x89d326		55			PUSHQ BP											
  keybuilder.go:88	0x89d327		4889e5			MOVQ SP, BP											
  keybuilder.go:88	0x89d32a		4883ec20		SUBQ $0x20, SP											
  keybuilder.go:90	0x89d32e		90			NOPL												
  binary.go:124		0x89d32f		48895c2418		MOVQ BX, 0x18(SP)										
  keybuilder.go:91	0x89d334		e807fcffff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).stream(SB)		
  hasher.go:90		0x89d339		90			NOPL												
  hasher.go:103		0x89d33a		488d5c2418		LEAQ 0x18(SP), BX										
  hasher.go:103		0x89d33f		b908000000		MOVL $0x8, CX											
  hasher.go:103		0x89d344		e83770d0ff		CALL github.com/zeebo/xxh3.(*Hasher).updateString(SB)						
  keybuilder.go:92	0x89d349		4883c420		ADDQ $0x20, SP											
  keybuilder.go:92	0x89d34d		5d			POPQ BP												
  keybuilder.go:92	0x89d34e		c3			RET												
  keybuilder.go:88	0x89d34f		4889442408		MOVQ AX, 0x8(SP)										
  keybuilder.go:88	0x89d354		48895c2410		MOVQ BX, 0x10(SP)										
  keybuilder.go:88	0x89d359		e8a226bfff		CALL runtime.morestack_noctxt.abi0(SB)								
  keybuilder.go:88	0x89d35e		488b442408		MOVQ 0x8(SP), AX										
  keybuilder.go:88	0x89d363		488b5c2410		MOVQ 0x10(SP), BX										
  keybuilder.go:88	0x89d368		ebb6			JMP github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint64Overflow(SB)	
