 ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:170	0x8ce6e0		493b6610		CMPQ SP, 0x10(R14)																										
  relater.go:170	0x8ce6e4		0f8654040000		JBE 0x8ceb3e																											
  relater.go:170	0x8ce6ea		55			PUSHQ BP																											
  relater.go:170	0x8ce6eb		4889e5			MOVQ SP, BP																											
  relater.go:170	0x8ce6ee		4883ec68		SUBQ $0x68, SP																											
  checker.go:25244	0x8ce6f2		8b13			MOVL 0(BX), DX																											
  checker.go:25244	0x8ce6f4		f7c2003c0100		TESTL $0x13c00, DX																										
  checker.go:25244	0x8ce6fa		7426			JE 0x8ce722																											
  types.go:691		0x8ce6fc		488b5328		MOVQ 0x28(BX), DX																										
  types.go:691		0x8ce700		4c8d157984c600		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.LiteralType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), R10										
  types.go:691		0x8ce707		4c39d2			CMPQ DX, R10																											
  types.go:691		0x8ce70a		0f8517040000		JNE 0x8ceb27																											
  types.go:691		0x8ce710		488b5330		MOVQ 0x30(BX), DX																										
 ... [unrelated caller instructions omitted] ...
  relater.go:104	0x8ce950		488b12			MOVQ 0(DX), DX																											
  relater.go:220	0x8ce953		90			NOPL																												
  relater.go:104	0x8ce954		4889d9			MOVQ BX, CX																											
  relater.go:104	0x8ce957		4889c3			MOVQ AX, BX																											
  relater.go:104	0x8ce95a		4889d0			MOVQ DX, AX																											
  relater.go:104	0x8ce95d		0f1f00			NOPL 0(AX)																											
  relater.go:104	0x8ce960		e81b000200		CALL github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).get(SB)																		
  relater.go:221	0x8ce965		85c0			TESTL AX, AX																											
  relater.go:221	0x8ce967		7519			JNE 0x8ce982																											
  relater.go:405	0x8ce969		488b442478		MOVQ 0x78(SP), AX																										
  relater.go:225	0x8ce96e		488b4c2458		MOVQ 0x58(SP), CX																										
  relater.go:225	0x8ce973		488b5c2460		MOVQ 0x60(SP), BX																										
  relater.go:405	0x8ce978		488bbc2490000000	MOVQ 0x90(SP), DI																										
  relater.go:221	0x8ce980		eb09			JMP 0x8ce98b																											
 ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Relater).recursiveTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:3091	0x8dfdc0		4c8da42450feffff	LEAQ 0xfffffe50(SP), R12												
  relater.go:3091	0x8dfdc8		4d3b6610		CMPQ R12, 0x10(R14)													
  relater.go:3091	0x8dfdcc		0f86a70d0000		JBE 0x8e0b79														
  relater.go:3091	0x8dfdd2		55			PUSHQ BP														
  relater.go:3091	0x8dfdd3		4889e5			MOVQ SP, BP														
  relater.go:3091	0x8dfdd6		4881ec28020000		SUBQ $0x228, SP														
  relater.go:3091	0x8dfddd		66440fd6bc2420020000	MOVQ X15, 0x220(SP)													
  relater.go:3091	0x8dfde7		c644244b00		MOVB $0x0, 0x4b(SP)													
  relater.go:3091	0x8dfdec		c644244600		MOVB $0x0, 0x46(SP)													
  relater.go:3092	0x8dfdf1		80b8a100000000		CMPB 0xa1(AX), $0x0													
  relater.go:3092	0x8dfdf8		0f85480d0000		JNE 0x8e0b46														
  relater.go:3092	0x8dfdfe		4889842438020000	MOVQ AX, 0x238(SP)													
  relater.go:3092	0x8dfe06		48899c2440020000	MOVQ BX, 0x240(SP)													
 ... [unrelated caller instructions omitted] ...
  relater.go:3098	0x8dfe62		488b942438020000	MOVQ 0x238(SP), DX													
  relater.go:3098	0x8dfe6a		488b5208		MOVQ 0x8(DX), DX													
  relater.go:104	0x8dfe6e		488b12			MOVQ 0(DX), DX														
  relater.go:104	0x8dfe71		4889d9			MOVQ BX, CX														
  relater.go:104	0x8dfe74		4889c3			MOVQ AX, BX														
  relater.go:104	0x8dfe77		4889d0			MOVQ DX, AX														
  relater.go:104	0x8dfe7a		e801eb0000		CALL github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).get(SB)					
  relater.go:104	0x8dfe7f		90			NOPL															
  relater.go:3098	0x8dfe80		85c0			TESTL AX, AX														
  relater.go:3098	0x8dfe82		0f84dd010000		JE 0x8e0065														
  relater.go:3092	0x8dfe88		0fb6942450020000	MOVZX 0x250(SP), DX													
  relater.go:3092	0x8dfe90		84d2			TESTL DL, DL														
  relater.go:3099	0x8dfe92		7417			JE 0x8dfeab														
  relater.go:3099	0x8dfe94		0fbae001		BTL $0x1, AX														
 ... [unrelated caller instructions omitted] ...
  printer.go:178	0x8dff3d		31f6			XORL SI, SI														
  printer.go:178	0x8dff3f		90			NOPL															
  printer.go:178	0x8dff40		e83b82feff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).typeToStringEx(SB)					
  printer.go:178	0x8dff45		4889842490000000	MOVQ AX, 0x90(SP)													
  printer.go:178	0x8dff4d		48895c2458		MOVQ BX, 0x58(SP)													
  relater.go:3108	0x8dff52		488d05a74d4900		LEAQ 0x494da7(IP), AX													
  relater.go:3108	0x8dff59		e8e23fb4ff		CALL runtime.newobject(SB)												
  relater.go:3108	0x8dff5e		4889842408020000	MOVQ AX, 0x208(SP)													
  relater.go:3108	0x8dff66		488b842498000000	MOVQ 0x98(SP), AX													
  relater.go:3108	0x8dff6e		488b5c2460		MOVQ 0x60(SP), BX													
  relater.go:3108	0x8dff73		e86876baff		CALL runtime.convTstring(SB)												
  relater.go:3108	0x8dff78		488d1541084800		LEAQ 0x480841(IP), DX													
  relater.go:3108	0x8dff7f		4c8b842408020000	MOVQ 0x208(SP), R8													
  relater.go:3108	0x8dff87		498910			MOVQ DX, 0(R8)														
 ... [unrelated caller instructions omitted] ...
  set.go:20		0x8e008e		4889542468		MOVQ DX, 0x68(SP)													
  set.go:20		0x8e0093		488b942480000000	MOVQ 0x80(SP), DX													
  set.go:20		0x8e009b		4889542470		MOVQ DX, 0x70(SP)													
  set.go:20		0x8e00a0		488b5e50		MOVQ 0x50(SI), BX													
  set.go:20		0x8e00a4		488d05152b4e00		LEAQ 0x4e2b15(IP), AX													
  set.go:20		0x8e00ab		488d4c2468		LEAQ 0x68(SP), CX													
  set.go:20		0x8e00b0		e82b1fb3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8e00b5		84db			TESTL BL, BL														
  relater.go:3121	0x8e00b7		0f855f0a0000		JNE 0x8e0b1c														
  relater.go:3097	0x8e00bd		0fb6542449		MOVZX 0x49(SP), DX													
  relater.go:3097	0x8e00c2		84d2			TESTL DL, DL														
  relater.go:3127	0x8e00c4		746e			JE 0x8e0134														
  relater.go:3128	0x8e00c6		488b942438020000	MOVQ 0x238(SP), DX													
  relater.go:3128	0x8e00ce		4c8b4208		MOVQ 0x8(DX), R8													
 ... [unrelated caller instructions omitted] ...
  set.go:20		0x8e0105		4889442468		MOVQ AX, 0x68(SP)													
  set.go:20		0x8e010a		48895c2470		MOVQ BX, 0x70(SP)													
  set.go:20		0x8e010f		488b942438020000	MOVQ 0x238(SP), DX													
  set.go:20		0x8e0117		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8e011b		488d059e2a4e00		LEAQ 0x4e2a9e(IP), AX													
  set.go:20		0x8e0122		488d4c2468		LEAQ 0x68(SP), CX													
  set.go:20		0x8e0127		e8b41eb3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8e012c		84db			TESTL BL, BL														
  relater.go:3129	0x8e012e		0f85d5090000		JNE 0x8e0b09														
  relater.go:3133	0x8e0134		488b942438020000	MOVQ 0x238(SP), DX													
  relater.go:3133	0x8e013c		48837a6064		CMPQ 0x60(DX), $0x64													
  relater.go:3133	0x8e0141		7407			JE 0x8e014a														
  relater.go:3133	0x8e0143		48837a7864		CMPQ 0x78(DX), $0x64													
  relater.go:3133	0x8e0148		7517			JNE 0x8e0161														
 ... [unrelated caller instructions omitted] ...
  relater.go:3138	0x8e01cc		488bbc2488000000	MOVQ 0x88(SP), DI													
  relater.go:3138	0x8e01d4		48893c30		MOVQ DI, 0(AX)(SI*1)													
  relater.go:3138	0x8e01d8		4c8b842480000000	MOVQ 0x80(SP), R8													
  relater.go:3138	0x8e01e0		4c89443008		MOVQ R8, 0x8(AX)(SI*1)													
  set.go:25		0x8e01e5		48837a5000		CMPQ 0x50(DX), $0x0													
  set.go:25		0x8e01ea		7544			JNE 0x8e0230														
  set.go:26		0x8e01ec		e8cf7abaff		CALL runtime.makemap_small(SB)												
  set.go:26		0x8e01f1		833d1863610100		CMPL runtime.writeBarrier(SB), $0x0											
  set.go:26		0x8e01f8		750a			JNE 0x8e0204														
  set.go:26		0x8e01fa		488b942438020000	MOVQ 0x238(SP), DX													
  set.go:26		0x8e0202		eb18			JMP 0x8e021c														
  set.go:26		0x8e0204		488b942438020000	MOVQ 0x238(SP), DX													
  set.go:26		0x8e020c		488b7250		MOVQ 0x50(DX), SI													
  set.go:26		0x8e0210		e8eb12bbff		CALL runtime.gcWriteBarrier2(SB)											
 ... [unrelated caller instructions omitted] ...
  set.go:28		0x8e0228		4c8b842480000000	MOVQ 0x80(SP), R8													
  set.go:28		0x8e0230		48897c2468		MOVQ DI, 0x68(SP)													
  set.go:28		0x8e0235		4c89442470		MOVQ R8, 0x70(SP)													
  set.go:28		0x8e023a		488b5a50		MOVQ 0x50(DX), BX													
  set.go:28		0x8e023e		488d057b294e00		LEAQ 0x4e297b(IP), AX													
  set.go:28		0x8e0245		488d4c2468		LEAQ 0x68(SP), CX													
  set.go:28		0x8e024a		e89120b3ff		CALL runtime.mapassign(SB)												
  set.go:28		0x8e024f		8400			TESTB AL, 0(AX)														
  relater.go:3140	0x8e0251		488b842438020000	MOVQ 0x238(SP), AX													
  relater.go:3140	0x8e0259		0fb690a0000000		MOVZX 0xa0(AX), DX													
  relater.go:3140	0x8e0260		88542447		MOVB DL, 0x47(SP)													
  relater.go:3141	0x8e0264		8bb42458020000		MOVL 0x258(SP), SI													
  relater.go:3141	0x8e026b		0fbae600		BTL $0x0, SI														
  relater.go:3141	0x8e026f		0f8323010000		JAE 0x8e0398														
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e05c3		e858fcb3ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8e05c8		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3158	0x8e05d0		488d05695c4e00		LEAQ 0x4e5c69(IP), AX													
  relater.go:3158	0x8e05d7		488d9c24c8010000	LEAQ 0x1c8(SP), BX													
  relater.go:3158	0x8e05df		488d0db9197200		LEAQ 0x7219b9(IP), CX													
  relater.go:3158	0x8e05e6		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8e05eb		e8303cb3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e05f0		488d0d49104800		LEAQ 0x481049(IP), CX													
  relater.go:3158	0x8e05f7		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e05fa		833d0f5f610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e0601		750a			JNE 0x8e060d														
  relater.go:3158	0x8e0603		488b942400020000	MOVQ 0x200(SP), DX													
  relater.go:3158	0x8e060b		eb18			JMP 0x8e0625														
  relater.go:3158	0x8e060d		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e0639		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3158	0x8e0641		488d05f85b4e00		LEAQ 0x4e5bf8(IP), AX													
  relater.go:3158	0x8e0648		488d9c24c8010000	LEAQ 0x1c8(SP), BX													
  relater.go:3158	0x8e0650		488d0d50197200		LEAQ 0x721950(IP), CX													
  relater.go:3158	0x8e0657		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8e065c		0f1f4000		NOPL 0(AX)														
  relater.go:3158	0x8e0660		e8bb3bb3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e0665		488d0dd40f4800		LEAQ 0x480fd4(IP), CX													
  relater.go:3158	0x8e066c		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e066f		833d9a5e610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e0676		750a			JNE 0x8e0682														
  relater.go:3158	0x8e0678		488b942400020000	MOVQ 0x200(SP), DX													
  relater.go:3158	0x8e0680		eb18			JMP 0x8e069a														
  relater.go:3158	0x8e0682		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e06aa		e8b16ebaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8e06af		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3158	0x8e06b7		488d05825b4e00		LEAQ 0x4e5b82(IP), AX													
  relater.go:3158	0x8e06be		488d9c24c8010000	LEAQ 0x1c8(SP), BX													
  relater.go:3158	0x8e06c6		488d0d6efa7100		LEAQ 0x71fa6e(IP), CX													
  relater.go:3158	0x8e06cd		bf05000000		MOVL $0x5, DI														
  relater.go:3158	0x8e06d2		e8493bb3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e06d7		488d0d22034800		LEAQ 0x480322(IP), CX													
  relater.go:3158	0x8e06de		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e06e1		833d285e610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e06e8		750a			JNE 0x8e06f4														
  relater.go:3158	0x8e06ea		488b942400020000	MOVQ 0x200(SP), DX													
  relater.go:3158	0x8e06f2		eb18			JMP 0x8e070c														
  relater.go:3158	0x8e06f4		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8e0720		e83b6ebaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8e0725		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3158	0x8e072d		488d050c5b4e00		LEAQ 0x4e5b0c(IP), AX													
  relater.go:3158	0x8e0734		488d9c24c8010000	LEAQ 0x1c8(SP), BX													
  relater.go:3158	0x8e073c		488d0d5f3a7200		LEAQ 0x723a5f(IP), CX													
  relater.go:3158	0x8e0743		bf0b000000		MOVL $0xb, DI														
  relater.go:3158	0x8e0748		e8d33ab3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8e074d		488d0dac024800		LEAQ 0x4802ac(IP), CX													
  relater.go:3158	0x8e0754		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8e0757		833db25d610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8e075e		6690			NOPW															
  relater.go:3158	0x8e0760		750a			JNE 0x8e076c														
  relater.go:3158	0x8e0762		4c8b8c2400020000	MOVQ 0x200(SP), R9													
  relater.go:3158	0x8e076a		eb18			JMP 0x8e0784														
 ... [unrelated caller instructions omitted] ...
  relater.go:3162	0x8e07da		4c8b00			MOVQ 0(AX), R8														
  relater.go:3162	0x8e07dd		418400			TESTB AL, 0(R8)														
  relater.go:3162	0x8e07e0		4d8b8088120000		MOVQ 0x1288(R8), R8													
  relater.go:3162	0x8e07e7		4c898424a8000000	MOVQ R8, 0xa8(SP)													
  relater.go:3162	0x8e07ef		4d85c0			TESTQ R8, R8														
  relater.go:3162	0x8e07f2		0f8446010000		JE 0x8e093e														
  relater.go:3163	0x8e07f8		e8c374baff		CALL runtime.makemap_small(SB)												
  relater.go:3163	0x8e07fd		48898424f8010000	MOVQ AX, 0x1f8(SP)													
  relater.go:3163	0x8e0805		488b842440020000	MOVQ 0x240(SP), AX													
  relater.go:3163	0x8e080d		8b4008			MOVL 0x8(AX), AX													
  relater.go:3163	0x8e0810		e80bfab3ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8e0815		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3163	0x8e081d		488d051c5a4e00		LEAQ 0x4e5a1c(IP), AX													
  relater.go:3163	0x8e0824		488b9c24f8010000	MOVQ 0x1f8(SP), BX													
  relater.go:3163	0x8e082c		488d0d6c177200		LEAQ 0x72176c(IP), CX													
  relater.go:3163	0x8e0833		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8e0838		e8e339b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8e083d		488d0dfc0d4800		LEAQ 0x480dfc(IP), CX													
  relater.go:3163	0x8e0844		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8e0847		833dc25c610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8e084e		750a			JNE 0x8e085a														
  relater.go:3163	0x8e0850		488b942400020000	MOVQ 0x200(SP), DX													
  relater.go:3163	0x8e0858		eb1a			JMP 0x8e0874														
  relater.go:3163	0x8e085a		488b4808		MOVQ 0x8(AX), CX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3163	0x8e0883		e898f9b3ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8e0888		4889842400020000	MOVQ AX, 0x200(SP)													
  relater.go:3163	0x8e0890		488d05a9594e00		LEAQ 0x4e59a9(IP), AX													
  relater.go:3163	0x8e0897		488b9c24f8010000	MOVQ 0x1f8(SP), BX													
  relater.go:3163	0x8e089f		488d0d01177200		LEAQ 0x721701(IP), CX													
  relater.go:3163	0x8e08a6		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8e08ab		e87039b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8e08b0		488d0d890d4800		LEAQ 0x480d89(IP), CX													
  relater.go:3163	0x8e08b7		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8e08ba		833d4f5c610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8e08c1		750a			JNE 0x8e08cd														
  relater.go:3163	0x8e08c3		4c8b942400020000	MOVQ 0x200(SP), R10													
  relater.go:3163	0x8e08cb		eb18			JMP 0x8e08e5														
  relater.go:3163	0x8e08cd		488b5008		MOVQ 0x8(AX), DX													
 ... [unrelated caller instructions omitted] ...
  relater.go:3167	0x8e0a45		897c2450		MOVL DI, 0x50(SP)													
  relater.go:3192	0x8e0a49		488b5008		MOVQ 0x8(AX), DX													
  relater.go:108	0x8e0a4d		48833a00		CMPQ 0(DX), $0x0													
  relater.go:108	0x8e0a51		7545			JNE 0x8e0a98														
  relater.go:3192	0x8e0a53		48899424b8000000	MOVQ DX, 0xb8(SP)													
  relater.go:109	0x8e0a5b		488d05de195a00		LEAQ 0x5a19de(IP), AX													
  relater.go:109	0x8e0a62		e8d934b4ff		CALL runtime.newobject(SB)												
  relater.go:109	0x8e0a67		833da25a610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8e0a6e		750a			JNE 0x8e0a7a														
  relater.go:109	0x8e0a70		488b9424b8000000	MOVQ 0xb8(SP), DX													
  relater.go:109	0x8e0a78		eb17			JMP 0x8e0a91														
  relater.go:109	0x8e0a7a		488b9424b8000000	MOVQ 0xb8(SP), DX													
  relater.go:109	0x8e0a82		488b32			MOVQ 0(DX), SI														
  relater.go:109	0x8e0a85		e8760abbff		CALL runtime.gcWriteBarrier2(SB)											
 ... [unrelated caller instructions omitted] ...
  relater.go:3192	0x8e0a98		89fe			MOVL DI, SI														
  relater.go:3192	0x8e0a9a		83ce02			ORL $0x2, SI														
  relater.go:111	0x8e0a9d		488b02			MOVQ 0(DX), AX														
  relater.go:111	0x8e0aa0		488b9c2488000000	MOVQ 0x88(SP), BX													
  relater.go:111	0x8e0aa8		488b8c2480000000	MOVQ 0x80(SP), CX													
  relater.go:111	0x8e0ab0		89f7			MOVL SI, DI														
  relater.go:111	0x8e0ab2		e829e00000		CALL github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).set(SB)					
  relater.go:3193	0x8e0ab7		488b842438020000	MOVQ 0x238(SP), AX													
  relater.go:3193	0x8e0abf		48ff88a8000000		DECQ 0xa8(AX)														
  relater.go:3194	0x8e0ac6		488b5c2478		MOVQ 0x78(SP), BX													
  relater.go:3194	0x8e0acb		8b4c2450		MOVL 0x50(SP), CX													
  relater.go:3194	0x8e0acf		31ff			XORL DI, DI														
  relater.go:3194	0x8e0ad1		e8ea000000		CALL github.com/microsoft/typescript-go/internal/checker.(*Relater).resetMaybeStack(SB)					
  relater.go:3196	0x8e0ad6		0fb64c2448		MOVZX 0x48(SP), CX													
 ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Relater).resetMaybeStack(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:3199	0x8e0bc0		493b6610		CMPQ SP, 0x10(R14)									
  relater.go:3199	0x8e0bc4		0f8666010000		JBE 0x8e0d30										
  relater.go:3199	0x8e0bca		55			PUSHQ BP										
  relater.go:3199	0x8e0bcb		4889e5			MOVQ SP, BP										
  relater.go:3199	0x8e0bce		4883ec58		SUBQ $0x58, SP										
  relater.go:3200	0x8e0bd2		4889442468		MOVQ AX, 0x68(SP)									
  relater.go:3200	0x8e0bd7		48895c2470		MOVQ BX, 0x70(SP)									
  relater.go:3200	0x8e0bdc		894c2478		MOVL CX, 0x78(SP)									
  relater.go:3200	0x8e0be0		40887c247c		MOVB DI, 0x7c(SP)									
  relater.go:3200	0x8e0be5		4889da			MOVQ BX, DX										
  relater.go:3200	0x8e0be8		eb1b			JMP 0x8e0c05										
  relater.go:3200	0x8e0bea		488b5c2420		MOVQ 0x20(SP), BX									
  relater.go:3200	0x8e0bef		48ffc3			INCQ BX											
 ... [unrelated caller instructions omitted] ...
  relater.go:108	0x8e0c8b		49833800		CMPQ 0(R8), $0x0									
  relater.go:108	0x8e0c8f		754f			JNE 0x8e0ce0										
  relater.go:3203	0x8e0c91		4c89442450		MOVQ R8, 0x50(SP)									
  relater.go:3203	0x8e0c96		48894c2430		MOVQ CX, 0x30(SP)									
  relater.go:3203	0x8e0c9b		48895c2428		MOVQ BX, 0x28(SP)									
  relater.go:109	0x8e0ca0		488d0599175a00		LEAQ 0x5a1799(IP), AX									
  relater.go:109	0x8e0ca7		e89432b4ff		CALL runtime.newobject(SB)								
  relater.go:109	0x8e0cac		833d5d58610100		CMPL runtime.writeBarrier(SB), $0x0							
  relater.go:109	0x8e0cb3		7507			JNE 0x8e0cbc										
  relater.go:109	0x8e0cb5		488b542450		MOVQ 0x50(SP), DX									
  relater.go:109	0x8e0cba		eb14			JMP 0x8e0cd0										
  relater.go:109	0x8e0cbc		488b542450		MOVQ 0x50(SP), DX									
  relater.go:109	0x8e0cc1		488b32			MOVQ 0(DX), SI										
  relater.go:109	0x8e0cc4		e83708bbff		CALL runtime.gcWriteBarrier2(SB)							
 ... [unrelated caller instructions omitted] ...
  relater.go:111	0x8e0cdd		4989d0			MOVQ DX, R8										
  relater.go:3203	0x8e0ce0		8b7c2478		MOVL 0x78(SP), DI									
  relater.go:3203	0x8e0ce4		89fa			MOVL DI, DX										
  relater.go:3203	0x8e0ce6		83ca01			ORL $0x1, DX										
  relater.go:111	0x8e0ce9		498b00			MOVQ 0(R8), AX										
  relater.go:111	0x8e0cec		89d7			MOVL DX, DI										
  relater.go:111	0x8e0cee		e8eddd0000		CALL github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).set(SB)	
  relater.go:3204	0x8e0cf3		488b542468		MOVQ 0x68(SP), DX									
  relater.go:3204	0x8e0cf8		48ff8aa8000000		DECQ 0xa8(DX)										
  relater.go:3200	0x8e0cff		0fb654247c		MOVZX 0x7c(SP), DX									
  relater.go:3204	0x8e0d04		e9e1feffff		JMP 0x8e0bea										
  relater.go:3200	0x8e0d09		488b4848		MOVQ 0x48(AX), CX									
  relater.go:3207	0x8e0d0d		4839ca			CMPQ DX, CX										
  relater.go:3207	0x8e0d10		770a			JA 0x8e0d1c										
