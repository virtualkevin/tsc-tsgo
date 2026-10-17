 ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:170	0x8ce6e0		493b6610		CMPQ SP, 0x10(R14)																										
  relater.go:170	0x8ce6e4		0f867c040000		JBE 0x8ceb66																											
  relater.go:170	0x8ce6ea		55			PUSHQ BP																											
  relater.go:170	0x8ce6eb		4889e5			MOVQ SP, BP																											
  relater.go:170	0x8ce6ee		4883ec78		SUBQ $0x78, SP																											
  checker.go:25244	0x8ce6f2		8b13			MOVL 0(BX), DX																											
  checker.go:25244	0x8ce6f4		f7c2003c0100		TESTL $0x13c00, DX																										
  checker.go:25244	0x8ce6fa		7426			JE 0x8ce722																											
  types.go:691		0x8ce6fc		488b5328		MOVQ 0x28(BX), DX																										
  types.go:691		0x8ce700		4c8d15d971c600		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.LiteralType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), R10										
  types.go:691		0x8ce707		4c39d2			CMPQ DX, R10																											
  types.go:691		0x8ce70a		0f853d040000		JNE 0x8ceb4d																											
  types.go:691		0x8ce710		488b5330		MOVQ 0x30(BX), DX																										
 ... [unrelated caller instructions omitted] ...
  relater.go:104	0x8ce958		4889442448		MOVQ AX, 0x48(SP)																										
  relater.go:104	0x8ce95d		48895c2450		MOVQ BX, 0x50(SP)																										
  relater.go:104	0x8ce962		488b9424a0000000	MOVQ 0xa0(SP), DX																										
  relater.go:104	0x8ce96a		488b1a			MOVQ 0(DX), BX																											
  relater.go:104	0x8ce96d		488d05ac954f00		LEAQ 0x4f95ac(IP), AX																										
  relater.go:104	0x8ce974		488d4c2448		LEAQ 0x48(SP), CX																										
  relater.go:104	0x8ce979		e8a233b4ff		CALL runtime.mapaccess1(SB)																									
  relater.go:104	0x8ce97e		8b00			MOVL 0(AX), AX																											
  relater.go:221	0x8ce980		85c0			TESTL AX, AX																											
  relater.go:221	0x8ce982		751e			JNE 0x8ce9a2																											
  relater.go:405	0x8ce984		488b842488000000	MOVQ 0x88(SP), AX																										
  relater.go:225	0x8ce98c		488b4c2468		MOVQ 0x68(SP), CX																										
  relater.go:225	0x8ce991		488b5c2470		MOVQ 0x70(SP), BX																										
  relater.go:405	0x8ce996		488bbc24a0000000	MOVQ 0xa0(SP), DI																										
 ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Relater).recursiveTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:3091	0x8dfe00		4c8da42410feffff	LEAQ 0xfffffe10(SP), R12												
  relater.go:3091	0x8dfe08		4d3b6610		CMPQ R12, 0x10(R14)													
  relater.go:3091	0x8dfe0c		0f8681100000		JBE 0x8e0e93														
  relater.go:3091	0x8dfe12		55			PUSHQ BP														
  relater.go:3091	0x8dfe13		4889e5			MOVQ SP, BP														
  relater.go:3091	0x8dfe16		4881ec68020000		SUBQ $0x268, SP														
  relater.go:3091	0x8dfe1d		66440fd6bc2460020000	MOVQ X15, 0x260(SP)													
  relater.go:3091	0x8dfe27		c644244b00		MOVB $0x0, 0x4b(SP)													
  relater.go:3091	0x8dfe2c		c644244600		MOVB $0x0, 0x46(SP)													
  relater.go:3092	0x8dfe31		80b8a100000000		CMPB 0xa1(AX), $0x0													
  relater.go:3092	0x8dfe38		0f857b0d0000		JNE 0x8e0bb9														
  relater.go:3092	0x8dfe3e		4889842478020000	MOVQ AX, 0x278(SP)													
  relater.go:3092	0x8dfe46		48899c2480020000	MOVQ BX, 0x280(SP)													
 ... [unrelated caller instructions omitted] ...
  relater.go:3098	0x8dfeba		488b5208		MOVQ 0x8(DX), DX													
  relater.go:104	0x8dfebe		4889842488000000	MOVQ AX, 0x88(SP)													
  relater.go:104	0x8dfec6		48899c2490000000	MOVQ BX, 0x90(SP)													
  relater.go:104	0x8dfece		488b1a			MOVQ 0(DX), BX														
  relater.go:104	0x8dfed1		488d0548804e00		LEAQ 0x4e8048(IP), AX													
  relater.go:104	0x8dfed8		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:104	0x8dfee0		e83b1eb3ff		CALL runtime.mapaccess1(SB)												
  relater.go:104	0x8dfee5		8b10			MOVL 0(AX), DX														
  relater.go:3098	0x8dfee7		85d2			TESTL DX, DX														
  relater.go:3098	0x8dfee9		0f84d8010000		JE 0x8e00c7														
  relater.go:3092	0x8dfeef		440fb6842490020000	MOVZX 0x290(SP), R8													
  relater.go:3092	0x8dfef8		4584c0			TESTL R8, R8														
  relater.go:3099	0x8dfefb		7412			JE 0x8dff0f														
  relater.go:3099	0x8dfefd		0fbae201		BTL $0x1, DX														
 ... [unrelated caller instructions omitted] ...
  printer.go:178	0x8dffa2		31f6			XORL SI, SI														
  printer.go:178	0x8dffa4		e8d781feff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).typeToStringEx(SB)					
  printer.go:178	0x8dffa9		48898424c8000000	MOVQ AX, 0xc8(SP)													
  printer.go:178	0x8dffb1		48895c2460		MOVQ BX, 0x60(SP)													
  relater.go:3108	0x8dffb6		488d05633c4900		LEAQ 0x493c63(IP), AX													
  relater.go:3108	0x8dffbd		0f1f00			NOPL 0(AX)														
  relater.go:3108	0x8dffc0		e87b3fb4ff		CALL runtime.newobject(SB)												
  relater.go:3108	0x8dffc5		4889842410010000	MOVQ AX, 0x110(SP)													
  relater.go:3108	0x8dffcd		488b8424d0000000	MOVQ 0xd0(SP), AX													
  relater.go:3108	0x8dffd5		488b5c2468		MOVQ 0x68(SP), BX													
  relater.go:3108	0x8dffda		e80176baff		CALL runtime.convTstring(SB)												
  relater.go:3108	0x8dffdf		488d15faf64700		LEAQ 0x47f6fa(IP), DX													
  relater.go:3108	0x8dffe6		4c8b842410010000	MOVQ 0x110(SP), R8													
  relater.go:3108	0x8dffee		498910			MOVQ DX, 0(R8)														
 ... [unrelated caller instructions omitted] ...
  set.go:20		0x8e00ee		4889b424b8000000	MOVQ SI, 0xb8(SP)													
  set.go:20		0x8e00f6		488bb424a8000000	MOVQ 0xa8(SP), SI													
  set.go:20		0x8e00fe		4889b424c0000000	MOVQ SI, 0xc0(SP)													
  set.go:20		0x8e0106		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8e010a		488d05cf194e00		LEAQ 0x4e19cf(IP), AX													
  set.go:20		0x8e0111		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:20		0x8e0119		e8c21eb3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8e011e		6690			NOPW															
  set.go:20		0x8e0120		84db			TESTL BL, BL														
  relater.go:3121	0x8e0122		0f85670a0000		JNE 0x8e0b8f														
  relater.go:3097	0x8e0128		0fb6542449		MOVZX 0x49(SP), DX													
  relater.go:3097	0x8e012d		84d2			TESTL DL, DL														
  relater.go:3127	0x8e012f		0f8483000000		JE 0x8e01b8														
  relater.go:3128	0x8e0135		488b942478020000	MOVQ 0x278(SP), DX													
 ... [unrelated caller instructions omitted] ...
  set.go:20		0x8e0180		48898424b8000000	MOVQ AX, 0xb8(SP)													
  set.go:20		0x8e0188		48899c24c0000000	MOVQ BX, 0xc0(SP)													
  set.go:20		0x8e0190		488b942478020000	MOVQ 0x278(SP), DX													
  set.go:20		0x8e0198		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8e019c		488d053d194e00		LEAQ 0x4e193d(IP), AX													
  set.go:20		0x8e01a3		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:20		0x8e01ab		e8301eb3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8e01b0		84db			TESTL BL, BL														
  relater.go:3129	0x8e01b2		0f85c4090000		JNE 0x8e0b7c														
  relater.go:3133	0x8e01b8		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3133	0x8e01c0		48837a6064		CMPQ 0x60(DX), $0x64													
  relater.go:3133	0x8e01c5		0f849a090000		JE 0x8e0b65														
  relater.go:3133	0x8e01cb		48837a7864		CMPQ 0x78(DX), $0x64													
  relater.go:3133	0x8e01d0		0f848f090000		JE 0x8e0b65														
 ... [unrelated caller instructions omitted] ...
  relater.go:3138	0x8e0247		488bbc24b0000000	MOVQ 0xb0(SP), DI													
  relater.go:3138	0x8e024f		48893c30		MOVQ DI, 0(AX)(SI*1)													
  relater.go:3138	0x8e0253		4c8b8424a8000000	MOVQ 0xa8(SP), R8													
  relater.go:3138	0x8e025b		4c89443008		MOVQ R8, 0x8(AX)(SI*1)													
  set.go:25		0x8e0260		48837a5000		CMPQ 0x50(DX), $0x0													
  set.go:25		0x8e0265		7544			JNE 0x8e02ab														
  set.go:26		0x8e0267		e8547abaff		CALL runtime.makemap_small(SB)												
  set.go:26		0x8e026c		833d9d42610100		CMPL runtime.writeBarrier(SB), $0x0											
  set.go:26		0x8e0273		750a			JNE 0x8e027f														
  set.go:26		0x8e0275		488b942478020000	MOVQ 0x278(SP), DX													
  set.go:26		0x8e027d		eb18			JMP 0x8e0297														
  set.go:26		0x8e027f		488b942478020000	MOVQ 0x278(SP), DX													
  set.go:26		0x8e0287		488b7250		MOVQ 0x50(DX), SI													
  set.go:26		0x8e028b		e87012bbff		CALL runtime.gcWriteBarrier2(SB)											
 ... [unrelated caller instructions omitted] ...
  set.go:28		0x8e02a3		4c8b8424a8000000	MOVQ 0xa8(SP), R8													
  set.go:28		0x8e02ab		4889bc24b8000000	MOVQ DI, 0xb8(SP)													
  set.go:28		0x8e02b3		4c898424c0000000	MOVQ R8, 0xc0(SP)													
  set.go:28		0x8e02bb		488b5a50		MOVQ 0x50(DX), BX													
  set.go:28		0x8e02bf		488d051a184e00		LEAQ 0x4e181a(IP), AX													
  set.go:28		0x8e02c6		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:28		0x8e02ce		e80d20b3ff		CALL runtime.mapassign(SB)												
  set.go:28		0x8e02d3		8400			TESTB AL, 0(AX)														
  relater.go:3140	0x8e02d5		488b842478020000	MOVQ 0x278(SP), AX													
  relater.go:3140	0x8e02dd		0fb690a0000000		MOVZX 0xa0(AX), DX													
  relater.go:3140	0x8e02e4		88542447		MOVB DL, 0x47(SP)													
  relater.go:3141	0x8e02e8		8bb42498020000		MOVL 0x298(SP), SI													
  relater.go:3141	0x8e02ef		0fbae600		BTL $0x0, SI														
  relater.go:3141	0x8e02f3		0f8323010000		JAE 0x8e041c														
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e0643		e8d8fbb3ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8e0648		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8e0650		488d05094b4e00		LEAQ 0x4e4b09(IP), AX													
  relater.go:3158	0x8e0657		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8e065f		488d0d99067200		LEAQ 0x720699(IP), CX													
  relater.go:3158	0x8e0666		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8e066b		e8b03bb3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e0670		488d0de9fe4700		LEAQ 0x47fee9(IP), CX													
  relater.go:3158	0x8e0677		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e067a		833d8f3e610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e0681		750a			JNE 0x8e068d														
  relater.go:3158	0x8e0683		488b942408010000	MOVQ 0x108(SP), DX													
  relater.go:3158	0x8e068b		eb18			JMP 0x8e06a5														
  relater.go:3158	0x8e068d		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e06b9		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8e06c1		488d05984a4e00		LEAQ 0x4e4a98(IP), AX													
  relater.go:3158	0x8e06c8		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8e06d0		488d0d30067200		LEAQ 0x720630(IP), CX													
  relater.go:3158	0x8e06d7		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8e06dc		0f1f4000		NOPL 0(AX)														
  relater.go:3158	0x8e06e0		e83b3bb3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e06e5		488d0d74fe4700		LEAQ 0x47fe74(IP), CX													
  relater.go:3158	0x8e06ec		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e06ef		833d1a3e610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e06f6		750a			JNE 0x8e0702														
  relater.go:3158	0x8e06f8		488b942408010000	MOVQ 0x108(SP), DX													
  relater.go:3158	0x8e0700		eb18			JMP 0x8e071a														
  relater.go:3158	0x8e0702		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e072a		e8316ebaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8e072f		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8e0737		488d05224a4e00		LEAQ 0x4e4a22(IP), AX													
  relater.go:3158	0x8e073e		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8e0746		488d0d4ee77100		LEAQ 0x71e74e(IP), CX													
  relater.go:3158	0x8e074d		bf05000000		MOVL $0x5, DI														
  relater.go:3158	0x8e0752		e8c93ab3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e0757		488d0dc2f14700		LEAQ 0x47f1c2(IP), CX													
  relater.go:3158	0x8e075e		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e0761		833da83d610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e0768		750a			JNE 0x8e0774														
  relater.go:3158	0x8e076a		488b942408010000	MOVQ 0x108(SP), DX													
  relater.go:3158	0x8e0772		eb18			JMP 0x8e078c														
  relater.go:3158	0x8e0774		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e07a0		e8bb6dbaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8e07a5		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8e07ad		488d05ac494e00		LEAQ 0x4e49ac(IP), AX													
  relater.go:3158	0x8e07b4		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8e07bc		488d0d3f277200		LEAQ 0x72273f(IP), CX													
  relater.go:3158	0x8e07c3		bf0b000000		MOVL $0xb, DI														
  relater.go:3158	0x8e07c8		e8533ab3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e07cd		488d0d4cf14700		LEAQ 0x47f14c(IP), CX													
  relater.go:3158	0x8e07d4		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e07d7		833d323d610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e07de		6690			NOPW															
  relater.go:3158	0x8e07e0		750a			JNE 0x8e07ec														
  relater.go:3158	0x8e07e2		4c8b8c2408010000	MOVQ 0x108(SP), R9													
  relater.go:3158	0x8e07ea		eb18			JMP 0x8e0804														
 ... [unrelated caller instructions omitted] ...
  relater.go:3162	0x8e085a		4c8b00			MOVQ 0(AX), R8														
  relater.go:3162	0x8e085d		418400			TESTB AL, 0(R8)														
  relater.go:3162	0x8e0860		4d8b8088120000		MOVQ 0x1288(R8), R8													
  relater.go:3162	0x8e0867		4c898424e0000000	MOVQ R8, 0xe0(SP)													
  relater.go:3162	0x8e086f		4d85c0			TESTQ R8, R8														
  relater.go:3162	0x8e0872		0f8446010000		JE 0x8e09be														
  relater.go:3163	0x8e0878		e84374baff		CALL runtime.makemap_small(SB)												
  relater.go:3163	0x8e087d		4889842400010000	MOVQ AX, 0x100(SP)													
  relater.go:3163	0x8e0885		488b842480020000	MOVQ 0x280(SP), AX													
  relater.go:3163	0x8e088d		8b4008			MOVL 0x8(AX), AX													
  relater.go:3163	0x8e0890		e88bf9b3ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8e0895		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3163	0x8e089d		488d05bc484e00		LEAQ 0x4e48bc(IP), AX													
  relater.go:3163	0x8e08a4		488b9c2400010000	MOVQ 0x100(SP), BX													
  relater.go:3163	0x8e08ac		488d0d4c047200		LEAQ 0x72044c(IP), CX													
  relater.go:3163	0x8e08b3		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8e08b8		e86339b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8e08bd		488d0d9cfc4700		LEAQ 0x47fc9c(IP), CX													
  relater.go:3163	0x8e08c4		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8e08c7		833d423c610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8e08ce		750a			JNE 0x8e08da														
  relater.go:3163	0x8e08d0		488b942408010000	MOVQ 0x108(SP), DX													
  relater.go:3163	0x8e08d8		eb1a			JMP 0x8e08f4														
  relater.go:3163	0x8e08da		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3163	0x8e0903		e818f9b3ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8e0908		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3163	0x8e0910		488d0549484e00		LEAQ 0x4e4849(IP), AX													
  relater.go:3163	0x8e0917		488b9c2400010000	MOVQ 0x100(SP), BX													
  relater.go:3163	0x8e091f		488d0de1037200		LEAQ 0x7203e1(IP), CX													
  relater.go:3163	0x8e0926		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8e092b		e8f038b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8e0930		488d0d29fc4700		LEAQ 0x47fc29(IP), CX													
  relater.go:3163	0x8e0937		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8e093a		833dcf3b610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8e0941		750a			JNE 0x8e094d														
  relater.go:3163	0x8e0943		4c8b942408010000	MOVQ 0x108(SP), R10													
  relater.go:3163	0x8e094b		eb18			JMP 0x8e0965														
  relater.go:3163	0x8e094d		488b5008		MOVQ 0x8(AX), DX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3200	0x8e0aa8		488b9424a0000000	MOVQ 0xa0(SP), DX													
  relater.go:3200	0x8e0ab0		e910020000		JMP 0x8e0cc5														
  relater.go:3192	0x8e0ab5		488b5008		MOVQ 0x8(AX), DX													
  relater.go:108	0x8e0ab9		48833a00		CMPQ 0(DX), $0x0													
  relater.go:108	0x8e0abd		753f			JNE 0x8e0afe														
  relater.go:3192	0x8e0abf		48899424f8000000	MOVQ DX, 0xf8(SP)													
  relater.go:109	0x8e0ac7		e8f471baff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8e0acc		833d3d3a610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8e0ad3		750a			JNE 0x8e0adf														
  relater.go:109	0x8e0ad5		488b9424f8000000	MOVQ 0xf8(SP), DX													
  relater.go:109	0x8e0add		eb17			JMP 0x8e0af6														
  relater.go:109	0x8e0adf		488b9424f8000000	MOVQ 0xf8(SP), DX													
  relater.go:109	0x8e0ae7		488b32			MOVQ 0(DX), SI														
  relater.go:109	0x8e0aea		e8110abbff		CALL runtime.gcWriteBarrier2(SB)											
 ... [unrelated caller instructions omitted] ...
  relater.go:111	0x8e0b16		4889b42490000000	MOVQ SI, 0x90(SP)													
  relater.go:3192	0x8e0b1e		4183c802		ORL $0x2, R8														
  relater.go:3192	0x8e0b22		4489442454		MOVL R8, 0x54(SP)													
  relater.go:111	0x8e0b27		488b1a			MOVQ 0(DX), BX														
  relater.go:111	0x8e0b2a		488d05ef734e00		LEAQ 0x4e73ef(IP), AX													
  relater.go:111	0x8e0b31		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:111	0x8e0b39		e8a217b3ff		CALL runtime.mapassign(SB)												
  relater.go:111	0x8e0b3e		8b542454		MOVL 0x54(SP), DX													
  relater.go:111	0x8e0b42		8910			MOVL DX, 0(AX)														
  relater.go:3193	0x8e0b44		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3193	0x8e0b4c		48ff8aa8000000		DECQ 0xa8(DX)														
  relater.go:3194	0x8e0b53		90			NOPL															
  relater.go:3200	0x8e0b54		488b8424a0000000	MOVQ 0xa0(SP), AX													
  relater.go:3200	0x8e0b5c		0f1f4000		NOPL 0(AX)														
 ... [unrelated caller instructions omitted] ...
  relater.go:3203	0x8e0cfa		8b542458		MOVL 0x58(SP), DX													
  relater.go:3203	0x8e0cfe		83ca01			ORL $0x1, DX														
  relater.go:3203	0x8e0d01		89542450		MOVL DX, 0x50(SP)													
  relater.go:111	0x8e0d05		488b1e			MOVQ 0(SI), BX														
  relater.go:111	0x8e0d08		488d0511724e00		LEAQ 0x4e7211(IP), AX													
  relater.go:111	0x8e0d0f		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:111	0x8e0d17		e8c415b3ff		CALL runtime.mapassign(SB)												
  relater.go:111	0x8e0d1c		8b542450		MOVL 0x50(SP), DX													
  relater.go:111	0x8e0d20		8910			MOVL DX, 0(AX)														
  relater.go:3204	0x8e0d22		488b842478020000	MOVQ 0x278(SP), AX													
  relater.go:3204	0x8e0d2a		48ff88a8000000		DECQ 0xa8(AX)														
  relater.go:3200	0x8e0d31		488b942480000000	MOVQ 0x80(SP), DX													
  relater.go:3200	0x8e0d39		48ffc2			INCQ DX															
  relater.go:3196	0x8e0d3c		0fb64c2448		MOVZX 0x48(SP), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3203	0x8e0ddd		4f8b440108		MOVQ 0x8(R9)(R8*1), R8													
  relater.go:108	0x8e0de2		48833e00		CMPQ 0(SI), $0x0													
  relater.go:108	0x8e0de6		0f85fefeffff		JNE 0x8e0cea														
  relater.go:3203	0x8e0dec		4889b424f0000000	MOVQ SI, 0xf0(SP)													
  relater.go:3203	0x8e0df4		4c899424b0000000	MOVQ R10, 0xb0(SP)													
  relater.go:3203	0x8e0dfc		4c898424a8000000	MOVQ R8, 0xa8(SP)													
  relater.go:109	0x8e0e04		e8b76ebaff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8e0e09		833d0037610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8e0e10		750a			JNE 0x8e0e1c														
  relater.go:109	0x8e0e12		488b9424f0000000	MOVQ 0xf0(SP), DX													
  relater.go:109	0x8e0e1a		eb17			JMP 0x8e0e33														
  relater.go:109	0x8e0e1c		488b9424f0000000	MOVQ 0xf0(SP), DX													
  relater.go:109	0x8e0e24		488b32			MOVQ 0(DX), SI														
  relater.go:109	0x8e0e27		e8d406bbff		CALL runtime.gcWriteBarrier2(SB)											
