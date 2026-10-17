  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:170	0x8cdcc0		493b6610		CMPQ SP, 0x10(R14)																										
  relater.go:170	0x8cdcc4		0f865c040000		JBE 0x8ce126																											
  relater.go:170	0x8cdcca		55			PUSHQ BP																											
  relater.go:170	0x8cdccb		4889e5			MOVQ SP, BP																											
  relater.go:170	0x8cdcce		4883ec68		SUBQ $0x68, SP																											
  checker.go:25322	0x8cdcd2		8b13			MOVL 0(BX), DX																											
  checker.go:25322	0x8cdcd4		f7c2003c0100		TESTL $0x13c00, DX																										
  checker.go:25322	0x8cdcda		7426			JE 0x8cdd02																											
  types.go:691		0x8cdcdc		488b5328		MOVQ 0x28(BX), DX																										
  types.go:691		0x8cdce0		4c8d15597cc600		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.LiteralType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), R10										
  types.go:691		0x8cdce7		4c39d2			CMPQ DX, R10																											
  ... [unrelated caller instructions omitted] ...
  relater.go:218	0x8cdf00		0fbae214		BTL $0x14, DX																											
  relater.go:218	0x8cdf04		7367			JAE 0x8cdf6d																											
  relater.go:218	0x8cdf06		8b11			MOVL 0(CX), DX																											
  relater.go:218	0x8cdf08		0fbae214		BTL $0x14, DX																											
  relater.go:218	0x8cdf0c		735f			JAE 0x8cdf6d																											
  relater.go:219	0x8cdf0e		4839b8b80f0000		CMPQ 0xfb8(AX), DI																										
  relater.go:219	0x8cdf15		400f94c6		SETE SI																												
  relater.go:219	0x8cdf19		31ff			XORL DI, DI																											
  relater.go:219	0x8cdf1b		4531c0			XORL R8, R8																											
  relater.go:219	0x8cdf1e		6690			NOPW																												
  relater.go:219	0x8cdf20		e89b83f3ff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getRelationKey(SB)																		
  relater.go:104	0x8cdf25		488b942490000000	MOVQ 0x90(SP), DX																										
  relater.go:104	0x8cdf2d		488b1a			MOVQ 0(DX), BX																											
  relater.go:220	0x8cdf30		90			NOPL																												
  relater.go:104	0x8cdf31		4889c1			MOVQ AX, CX																											
  relater.go:104	0x8cdf34		488d0585a04f00		LEAQ 0x4fa085(IP), AX																										
  relater.go:104	0x8cdf3b		0f1f440000		NOPL 0(AX)(AX*1)																										
  relater.go:104	0x8cdf40		e89b51b4ff		CALL runtime.mapaccess1_fast64(SB)																								
  relater.go:104	0x8cdf45		8b00			MOVL 0(AX), AX																											
  relater.go:221	0x8cdf47		85c0			TESTL AX, AX																											
  relater.go:221	0x8cdf49		7519			JNE 0x8cdf64																											
  relater.go:405	0x8cdf4b		488b442478		MOVQ 0x78(SP), AX																										
  relater.go:225	0x8cdf50		488b4c2458		MOVQ 0x58(SP), CX																										
  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Relater).recursiveTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:3091	0x8df3a0		4c8da42438feffff	LEAQ 0xfffffe38(SP), R12												
  relater.go:3091	0x8df3a8		4d3b6610		CMPQ R12, 0x10(R14)													
  relater.go:3091	0x8df3ac		0f861b0f0000		JBE 0x8e02cd														
  relater.go:3091	0x8df3b2		55			PUSHQ BP														
  relater.go:3091	0x8df3b3		4889e5			MOVQ SP, BP														
  relater.go:3091	0x8df3b6		4881ec40020000		SUBQ $0x240, SP														
  relater.go:3091	0x8df3bd		66440fd6bc2438020000	MOVQ X15, 0x238(SP)													
  relater.go:3091	0x8df3c7		c644244b00		MOVB $0x0, 0x4b(SP)													
  relater.go:3091	0x8df3cc		c644244600		MOVB $0x0, 0x46(SP)													
  relater.go:3092	0x8df3d1		80b8a100000000		CMPB 0xa1(AX), $0x0													
  relater.go:3092	0x8df3d8		0f85ad0c0000		JNE 0x8e008b														
  ... [unrelated caller instructions omitted] ...
  relater.go:3092	0x8df3f6		4088bc2468020000	MOVB DI, 0x268(SP)													
  relater.go:3092	0x8df3fe		89b4246c020000		MOVL SI, 0x26c(SP)													
  relater.go:3092	0x8df405		4489842470020000	MOVL R8, 0x270(SP)													
  relater.go:3097	0x8df40d		488b5008		MOVQ 0x8(AX), DX													
  relater.go:3097	0x8df411		488b00			MOVQ 0(AX), AX														
  relater.go:3097	0x8df414		483990b80f0000		CMPQ 0xfb8(AX), DX													
  relater.go:3097	0x8df41b		0f94c2			SETE DL															
  relater.go:3097	0x8df41e		89f7			MOVL SI, DI														
  relater.go:3097	0x8df420		89d6			MOVL DX, SI														
  relater.go:3097	0x8df422		4531c0			XORL R8, R8														
  relater.go:3097	0x8df425		e8966ef2ff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getRelationKey(SB)					
  relater.go:3097	0x8df42a		4889442478		MOVQ AX, 0x78(SP)													
  relater.go:3097	0x8df42f		885c2449		MOVB BL, 0x49(SP)													
  relater.go:3098	0x8df433		488b942450020000	MOVQ 0x250(SP), DX													
  relater.go:3098	0x8df43b		488b5208		MOVQ 0x8(DX), DX													
  relater.go:104	0x8df43f		488b1a			MOVQ 0(DX), BX														
  relater.go:104	0x8df442		4889c1			MOVQ AX, CX														
  relater.go:104	0x8df445		488d05748b4e00		LEAQ 0x4e8b74(IP), AX													
  relater.go:104	0x8df44c		e88f3cb3ff		CALL runtime.mapaccess1_fast64(SB)											
  relater.go:104	0x8df451		8b10			MOVL 0(AX), DX														
  relater.go:3098	0x8df453		85d2			TESTL DX, DX														
  relater.go:3098	0x8df455		0f84d9010000		JE 0x8df634														
  relater.go:3092	0x8df45b		440fb6842468020000	MOVZX 0x268(SP), R8													
  relater.go:3092	0x8df464		4584c0			TESTL R8, R8														
  ... [unrelated caller instructions omitted] ...
  relater.go:3113	0x8df62b		4881c440020000		ADDQ $0x240, SP														
  relater.go:3113	0x8df632		5d			POPQ BP															
  relater.go:3113	0x8df633		c3			RET															
  relater.go:3165	0x8df634		440fb6842468020000	MOVZX 0x268(SP), R8													
  relater.go:3116	0x8df63d		488b942450020000	MOVQ 0x250(SP), DX													
  relater.go:3116	0x8df645		4883baa800000000	CMPQ 0xa8(DX), $0x0													
  relater.go:3116	0x8df64d		0f8e210a0000		JLE 0x8e0074														
  set.go:20		0x8df653		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8df657		488d05a2254e00		LEAQ 0x4e25a2(IP), AX													
  set.go:20		0x8df65e		488b4c2478		MOVQ 0x78(SP), CX													
  set.go:20		0x8df663		e8783cb3ff		CALL runtime.mapaccess2_fast64(SB)											
  set.go:20		0x8df668		84db			TESTL BL, BL														
  relater.go:3121	0x8df66a		0f85f1090000		JNE 0x8e0061														
  relater.go:3097	0x8df670		0fb6542449		MOVZX 0x49(SP), DX													
  relater.go:3097	0x8df675		84d2			TESTL DL, DL														
  relater.go:3127	0x8df677		7462			JE 0x8df6db														
  relater.go:3128	0x8df679		488b942450020000	MOVQ 0x250(SP), DX													
  relater.go:3128	0x8df681		488b02			MOVQ 0(DX), AX														
  relater.go:3128	0x8df684		488b5208		MOVQ 0x8(DX), DX													
  relater.go:3128	0x8df688		483990b80f0000		CMPQ 0xfb8(AX), DX													
  relater.go:3128	0x8df68f		400f94c6		SETE SI															
  relater.go:3128	0x8df693		488b9c2458020000	MOVQ 0x258(SP), BX													
  relater.go:3128	0x8df69b		488b8c2460020000	MOVQ 0x260(SP), CX													
  relater.go:3128	0x8df6a3		8bbc246c020000		MOVL 0x26c(SP), DI													
  relater.go:3128	0x8df6aa		41b801000000		MOVL $0x1, R8														
  relater.go:3128	0x8df6b0		e80b6cf2ff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getRelationKey(SB)					
  set.go:20		0x8df6b5		488b942450020000	MOVQ 0x250(SP), DX													
  set.go:20		0x8df6bd		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8df6c1		488d1538254e00		LEAQ 0x4e2538(IP), DX													
  set.go:20		0x8df6c8		4889c1			MOVQ AX, CX														
  set.go:20		0x8df6cb		4889d0			MOVQ DX, AX														
  set.go:20		0x8df6ce		e80d3cb3ff		CALL runtime.mapaccess2_fast64(SB)											
  set.go:20		0x8df6d3		84db			TESTL BL, BL														
  relater.go:3129	0x8df6d5		0f8573090000		JNE 0x8e004e														
  relater.go:3133	0x8df6db		488b942450020000	MOVQ 0x250(SP), DX													
  relater.go:3133	0x8df6e3		48837a6064		CMPQ 0x60(DX), $0x64													
  relater.go:3133	0x8df6e8		0f8449090000		JE 0x8e0037														
  ... [unrelated caller instructions omitted] ...
  relater.go:3138	0x8df748		498903			MOVQ AX, 0(R11)														
  relater.go:3138	0x8df74b		49897308		MOVQ SI, 0x8(R11)													
  relater.go:3138	0x8df74f		48894238		MOVQ AX, 0x38(DX)													
  relater.go:3139	0x8df753		4989d8			MOVQ BX, R8														
  relater.go:3200	0x8df756		488b9c2498000000	MOVQ 0x98(SP), BX													
  relater.go:3138	0x8df75e		4c894240		MOVQ R8, 0x40(DX)													
  relater.go:3138	0x8df762		488b4c2478		MOVQ 0x78(SP), CX													
  relater.go:3138	0x8df767		4a894cc0f8		MOVQ CX, -0x8(AX)(R8*8)													
  set.go:25		0x8df76c		48837a5000		CMPQ 0x50(DX), $0x0													
  set.go:25		0x8df771		753a			JNE 0x8df7ad														
  set.go:26		0x8df773		e84885baff		CALL runtime.makemap_small(SB)												
  set.go:26		0x8df778		833d914d610100		CMPL runtime.writeBarrier(SB), $0x0											
  set.go:26		0x8df77f		90			NOPL															
  set.go:26		0x8df780		750a			JNE 0x8df78c														
  set.go:26		0x8df782		488b942450020000	MOVQ 0x250(SP), DX													
  set.go:26		0x8df78a		eb18			JMP 0x8df7a4														
  set.go:26		0x8df78c		488b942450020000	MOVQ 0x250(SP), DX													
  set.go:26		0x8df794		488b7250		MOVQ 0x50(DX), SI													
  set.go:26		0x8df798		e8631dbbff		CALL runtime.gcWriteBarrier2(SB)											
  set.go:26		0x8df79d		498903			MOVQ AX, 0(R11)														
  set.go:26		0x8df7a0		49897308		MOVQ SI, 0x8(R11)													
  set.go:26		0x8df7a4		48894250		MOVQ AX, 0x50(DX)													
  set.go:28		0x8df7a8		488b4c2478		MOVQ 0x78(SP), CX													
  set.go:28		0x8df7ad		488b5a50		MOVQ 0x50(DX), BX													
  set.go:28		0x8df7b1		488d0548244e00		LEAQ 0x4e2448(IP), AX													
  set.go:28		0x8df7b8		e8433db3ff		CALL runtime.mapassign_fast64(SB)											
  set.go:28		0x8df7bd		8400			TESTB AL, 0(AX)														
  relater.go:3140	0x8df7bf		488b842450020000	MOVQ 0x250(SP), AX													
  relater.go:3140	0x8df7c7		0fb690a0000000		MOVZX 0xa0(AX), DX													
  relater.go:3140	0x8df7ce		88542447		MOVB DL, 0x47(SP)													
  relater.go:3141	0x8df7d2		8bb42470020000		MOVL 0x270(SP), SI													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfb16		e8e5afbaff		CALL runtime.rand(SB)													
  relater.go:3158	0x8dfb1b		4889842410020000	MOVQ AX, 0x210(SP)													
  relater.go:3158	0x8dfb23		488b842458020000	MOVQ 0x258(SP), AX													
  relater.go:3158	0x8dfb2b		8b4008			MOVL 0x8(AX), AX													
  relater.go:3158	0x8dfb2e		e8ed06b4ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8dfb33		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3158	0x8dfb3b		488d05be564e00		LEAQ 0x4e56be(IP), AX													
  relater.go:3158	0x8dfb42		488d9c2408020000	LEAQ 0x208(SP), BX													
  relater.go:3158	0x8dfb4a		488d0d9e117200		LEAQ 0x72119e(IP), CX													
  relater.go:3158	0x8dfb51		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8dfb56		e8c546b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfb5b		488d0dde0a4800		LEAQ 0x480ade(IP), CX													
  relater.go:3158	0x8dfb62		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfb65		833da449610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfb6c		750a			JNE 0x8dfb78														
  relater.go:3158	0x8dfb6e		488b9424d8000000	MOVQ 0xd8(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfb90		49894b08		MOVQ CX, 0x8(R11)													
  relater.go:3158	0x8dfb94		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfb98		488b8c2460020000	MOVQ 0x260(SP), CX													
  relater.go:3158	0x8dfba0		8b4108			MOVL 0x8(CX), AX													
  relater.go:3158	0x8dfba3		e87806b4ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8dfba8		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3158	0x8dfbb0		488d0549564e00		LEAQ 0x4e5649(IP), AX													
  relater.go:3158	0x8dfbb7		488d9c2408020000	LEAQ 0x208(SP), BX													
  relater.go:3158	0x8dfbbf		488d0d31117200		LEAQ 0x721131(IP), CX													
  relater.go:3158	0x8dfbc6		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8dfbcb		e85046b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfbd0		488d0d690a4800		LEAQ 0x480a69(IP), CX													
  relater.go:3158	0x8dfbd7		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfbda		833d2f49610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfbe1		750a			JNE 0x8dfbed														
  relater.go:3158	0x8dfbe3		488b9424d8000000	MOVQ 0xd8(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfc05		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfc09		488b8c2450020000	MOVQ 0x250(SP), CX													
  relater.go:3158	0x8dfc11		488b4160		MOVQ 0x60(CX), AX													
  relater.go:3158	0x8dfc15		e84679baff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8dfc1a		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3158	0x8dfc22		488d05d7554e00		LEAQ 0x4e55d7(IP), AX													
  relater.go:3158	0x8dfc29		488d9c2408020000	LEAQ 0x208(SP), BX													
  relater.go:3158	0x8dfc31		488d0d53f27100		LEAQ 0x71f253(IP), CX													
  relater.go:3158	0x8dfc38		bf05000000		MOVL $0x5, DI														
  relater.go:3158	0x8dfc3d		0f1f00			NOPL 0(AX)														
  relater.go:3158	0x8dfc40		e8db45b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfc45		488d0db4fd4700		LEAQ 0x47fdb4(IP), CX													
  relater.go:3158	0x8dfc4c		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfc4f		833dba48610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfc56		750a			JNE 0x8dfc62														
  relater.go:3158	0x8dfc58		488b9424d8000000	MOVQ 0xd8(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfc76		49894b08		MOVQ CX, 0x8(R11)													
  relater.go:3158	0x8dfc7a		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfc7e		488b8c2450020000	MOVQ 0x250(SP), CX													
  relater.go:3158	0x8dfc86		488b4178		MOVQ 0x78(CX), AX													
  relater.go:3158	0x8dfc8a		e8d178baff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8dfc8f		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3158	0x8dfc97		488d0562554e00		LEAQ 0x4e5562(IP), AX													
  relater.go:3158	0x8dfc9e		488d9c2408020000	LEAQ 0x208(SP), BX													
  relater.go:3158	0x8dfca6		488d0d45327200		LEAQ 0x723245(IP), CX													
  relater.go:3158	0x8dfcad		bf0b000000		MOVL $0xb, DI														
  relater.go:3158	0x8dfcb2		e86945b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfcb7		488d0d42fd4700		LEAQ 0x47fd42(IP), CX													
  relater.go:3158	0x8dfcbe		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfcc1		833d4848610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfcc8		750a			JNE 0x8dfcd4														
  relater.go:3158	0x8dfcca		4c8b8c24d8000000	MOVQ 0xd8(SP), R9													
  ... [unrelated caller instructions omitted] ...
  relater.go:3160	0x8dfd3b		31db			XORL BX, BX														
  relater.go:3160	0x8dfd3d		0f1f00			NOPL 0(AX)														
  relater.go:3167	0x8dfd40		e9b0010000		JMP 0x8dfef5														
  relater.go:3162	0x8dfd45		4c8b00			MOVQ 0(AX), R8														
  relater.go:3162	0x8dfd48		418400			TESTB AL, 0(R8)														
  relater.go:3162	0x8dfd4b		4d8b8098120000		MOVQ 0x1298(R8), R8													
  relater.go:3162	0x8dfd52		4c898424b0000000	MOVQ R8, 0xb0(SP)													
  relater.go:3162	0x8dfd5a		660f1f440000		NOPW 0(AX)(AX*1)													
  relater.go:3162	0x8dfd60		4d85c0			TESTQ R8, R8														
  relater.go:3162	0x8dfd63		0f844a010000		JE 0x8dfeb3														
  relater.go:3163	0x8dfd69		e8527fbaff		CALL runtime.makemap_small(SB)												
  relater.go:3163	0x8dfd6e		48898424d0000000	MOVQ AX, 0xd0(SP)													
  relater.go:3163	0x8dfd76		488b842458020000	MOVQ 0x258(SP), AX													
  relater.go:3163	0x8dfd7e		8b4008			MOVL 0x8(AX), AX													
  relater.go:3163	0x8dfd81		e89a04b4ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8dfd86		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3163	0x8dfd8e		488d056b544e00		LEAQ 0x4e546b(IP), AX													
  relater.go:3163	0x8dfd95		488b9c24d0000000	MOVQ 0xd0(SP), BX													
  relater.go:3163	0x8dfd9d		488d0d4b0f7200		LEAQ 0x720f4b(IP), CX													
  relater.go:3163	0x8dfda4		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8dfda9		e87244b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8dfdae		488d0d8b084800		LEAQ 0x48088b(IP), CX													
  relater.go:3163	0x8dfdb5		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8dfdb8		833d5147610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8dfdbf		90			NOPL															
  relater.go:3163	0x8dfdc0		750a			JNE 0x8dfdcc														
  ... [unrelated caller instructions omitted] ...
  relater.go:3163	0x8dfde4		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3163	0x8dfde8		488b8c2460020000	MOVQ 0x260(SP), CX													
  relater.go:3163	0x8dfdf0		8b4108			MOVL 0x8(CX), AX													
  relater.go:3163	0x8dfdf3		e82804b4ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8dfdf8		48898424d8000000	MOVQ AX, 0xd8(SP)													
  relater.go:3163	0x8dfe00		488d05f9534e00		LEAQ 0x4e53f9(IP), AX													
  relater.go:3163	0x8dfe07		488b9c24d0000000	MOVQ 0xd0(SP), BX													
  relater.go:3163	0x8dfe0f		488d0de10e7200		LEAQ 0x720ee1(IP), CX													
  relater.go:3163	0x8dfe16		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8dfe1b		0f1f440000		NOPL 0(AX)(AX*1)													
  relater.go:3163	0x8dfe20		e8fb43b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8dfe25		488d0d14084800		LEAQ 0x480814(IP), CX													
  relater.go:3163	0x8dfe2c		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8dfe2f		833dda46610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8dfe36		750a			JNE 0x8dfe42														
  relater.go:3163	0x8dfe38		4c8b9424d8000000	MOVQ 0xd8(SP), R10													
  ... [unrelated caller instructions omitted] ...
  relater.go:3178	0x8dff8e		750d			JNE 0x8dff9d														
  relater.go:3200	0x8dff90		488b942498000000	MOVQ 0x98(SP), DX													
  relater.go:3200	0x8dff98		e937020000		JMP 0x8e01d4														
  relater.go:3200	0x8dff9d		488b942498000000	MOVQ 0x98(SP), DX													
  relater.go:3200	0x8dffa5		e9bb010000		JMP 0x8e0165														
  relater.go:3192	0x8dffaa		488b5008		MOVQ 0x8(AX), DX													
  relater.go:108	0x8dffae		48833a00		CMPQ 0(DX), $0x0													
  relater.go:108	0x8dffb2		7543			JNE 0x8dfff7														
  relater.go:3192	0x8dffb4		48899424c8000000	MOVQ DX, 0xc8(SP)													
  relater.go:109	0x8dffbc		0f1f4000		NOPL 0(AX)														
  relater.go:109	0x8dffc0		e8fb7cbaff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8dffc5		833d4445610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8dffcc		750a			JNE 0x8dffd8														
  relater.go:109	0x8dffce		488b9424c8000000	MOVQ 0xc8(SP), DX													
  relater.go:109	0x8dffd6		eb17			JMP 0x8dffef														
  relater.go:109	0x8dffd8		488b9424c8000000	MOVQ 0xc8(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:109	0x8dffe3		e81815bbff		CALL runtime.gcWriteBarrier2(SB)											
  relater.go:109	0x8dffe8		498903			MOVQ AX, 0(R11)														
  relater.go:109	0x8dffeb		49897308		MOVQ SI, 0x8(R11)													
  relater.go:109	0x8dffef		488902			MOVQ AX, 0(DX)														
  relater.go:3192	0x8dfff2		448b442458		MOVL 0x58(SP), R8													
  relater.go:3192	0x8dfff7		4183c802		ORL $0x2, R8														
  relater.go:3192	0x8dfffb		4489442454		MOVL R8, 0x54(SP)													
  relater.go:111	0x8e0000		488b1a			MOVQ 0(DX), BX														
  relater.go:111	0x8e0003		488d05b67f4e00		LEAQ 0x4e7fb6(IP), AX													
  relater.go:111	0x8e000a		488b4c2478		MOVQ 0x78(SP), CX													
  relater.go:111	0x8e000f		e8ec34b3ff		CALL runtime.mapassign_fast64(SB)											
  relater.go:111	0x8e0014		8b542454		MOVL 0x54(SP), DX													
  relater.go:111	0x8e0018		8910			MOVL DX, 0(AX)														
  relater.go:3193	0x8e001a		488b942450020000	MOVQ 0x250(SP), DX													
  relater.go:3193	0x8e0022		48ff8aa8000000		DECQ 0xa8(DX)														
  relater.go:3194	0x8e0029		90			NOPL															
  ... [unrelated caller instructions omitted] ...
  relater.go:3207	0x8e017a		7209			JB 0x8e0185														
  relater.go:3207	0x8e017c		48897840		MOVQ DI, 0x40(AX)													
  relater.go:3183	0x8e0180		e964ffffff		JMP 0x8e00e9														
  relater.go:3207	0x8e0185		e81617bbff		CALL runtime.panicBounds(SB)												
  relater.go:3203	0x8e018a		8b542458		MOVL 0x58(SP), DX													
  relater.go:3203	0x8e018e		83ca01			ORL $0x1, DX														
  relater.go:3203	0x8e0191		89542450		MOVL DX, 0x50(SP)													
  relater.go:111	0x8e0195		488b1e			MOVQ 0(SI), BX														
  relater.go:111	0x8e0198		488d05217e4e00		LEAQ 0x4e7e21(IP), AX													
  relater.go:111	0x8e019f		90			NOPL															
  relater.go:111	0x8e01a0		e85b33b3ff		CALL runtime.mapassign_fast64(SB)											
  relater.go:111	0x8e01a5		8b542450		MOVL 0x50(SP), DX													
  relater.go:111	0x8e01a9		8910			MOVL DX, 0(AX)														
  relater.go:3204	0x8e01ab		488b842450020000	MOVQ 0x250(SP), AX													
  relater.go:3204	0x8e01b3		48ff88a8000000		DECQ 0xa8(AX)														
  relater.go:3200	0x8e01ba		488b942490000000	MOVQ 0x90(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3203	0x8e0219		0f1f8000000000		NOPL 0(AX)														
  relater.go:3203	0x8e0220		4839f7			CMPQ DI, SI														
  relater.go:3203	0x8e0223		0f8381000000		JAE 0x8e02aa														
  relater.go:3203	0x8e0229		488b7208		MOVQ 0x8(DX), SI													
  relater.go:3203	0x8e022d		4c8b4238		MOVQ 0x38(DX), R8													
  relater.go:3203	0x8e0231		498b0cf8		MOVQ 0(R8)(DI*8), CX													
  relater.go:108	0x8e0235		48833e00		CMPQ 0(SI), $0x0													
  relater.go:108	0x8e0239		0f854bffffff		JNE 0x8e018a														
  relater.go:3203	0x8e023f		4889b424c0000000	MOVQ SI, 0xc0(SP)													
  relater.go:3203	0x8e0247		48894c2470		MOVQ CX, 0x70(SP)													
  relater.go:109	0x8e024c		e86f7abaff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8e0251		833db842610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8e0258		750a			JNE 0x8e0264														
  relater.go:109	0x8e025a		488b9424c0000000	MOVQ 0xc0(SP), DX													
  relater.go:109	0x8e0262		eb17			JMP 0x8e027b														
  relater.go:109	0x8e0264		488b9424c0000000	MOVQ 0xc0(SP), DX													
