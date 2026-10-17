  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:170	0x8cda40		493b6610		CMPQ SP, 0x10(R14)																										
  relater.go:170	0x8cda44		0f867c040000		JBE 0x8cdec6																											
  relater.go:170	0x8cda4a		55			PUSHQ BP																											
  relater.go:170	0x8cda4b		4889e5			MOVQ SP, BP																											
  relater.go:170	0x8cda4e		4883ec78		SUBQ $0x78, SP																											
  checker.go:25284	0x8cda52		8b13			MOVL 0(BX), DX																											
  checker.go:25284	0x8cda54		f7c2003c0100		TESTL $0x13c00, DX																										
  checker.go:25284	0x8cda5a		7426			JE 0x8cda82																											
  types.go:691		0x8cda5c		488b5328		MOVQ 0x28(BX), DX																										
  types.go:691		0x8cda60		4c8d15b97bc600		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.LiteralType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), R10										
  types.go:691		0x8cda67		4c39d2			CMPQ DX, R10																											
  ... [unrelated caller instructions omitted] ...
  relater.go:218	0x8cdc93		7376			JAE 0x8cdd0b																											
  relater.go:218	0x8cdc95		8b11			MOVL 0(CX), DX																											
  relater.go:218	0x8cdc97		0fbae214		BTL $0x14, DX																											
  relater.go:218	0x8cdc9b		736e			JAE 0x8cdd0b																											
  relater.go:219	0x8cdc9d		4839b8b80f0000		CMPQ 0xfb8(AX), DI																										
  relater.go:219	0x8cdca4		400f94c7		SETE DI																												
  relater.go:219	0x8cdca8		4889d8			MOVQ BX, AX																											
  relater.go:219	0x8cdcab		4889cb			MOVQ CX, BX																											
  relater.go:219	0x8cdcae		31c9			XORL CX, CX																											
  relater.go:219	0x8cdcb0		31f6			XORL SI, SI																											
  relater.go:219	0x8cdcb2		e80986f3ff		CALL github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)																			
  relater.go:220	0x8cdcb7		90			NOPL																												
  relater.go:104	0x8cdcb8		4889442448		MOVQ AX, 0x48(SP)																										
  relater.go:104	0x8cdcbd		48895c2450		MOVQ BX, 0x50(SP)																										
  relater.go:104	0x8cdcc2		488b9424a0000000	MOVQ 0xa0(SP), DX																										
  relater.go:104	0x8cdcca		488b1a			MOVQ 0(DX), BX																											
  relater.go:104	0x8cdccd		488d052ca14f00		LEAQ 0x4fa12c(IP), AX																										
  relater.go:104	0x8cdcd4		488d4c2448		LEAQ 0x48(SP), CX																										
  relater.go:104	0x8cdcd9		e84240b4ff		CALL runtime.mapaccess1(SB)																									
  relater.go:104	0x8cdcde		8b00			MOVL 0(AX), AX																											
  relater.go:221	0x8cdce0		85c0			TESTL AX, AX																											
  relater.go:221	0x8cdce2		751e			JNE 0x8cdd02																											
  relater.go:405	0x8cdce4		488b842488000000	MOVQ 0x88(SP), AX																										
  relater.go:225	0x8cdcec		488b4c2468		MOVQ 0x68(SP), CX																										
  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Relater).recursiveTypeRelatedTo(SB) github.com/microsoft/typescript-go/internal/checker/relater.go
  relater.go:3091	0x8df160		4c8da42410feffff	LEAQ 0xfffffe10(SP), R12												
  relater.go:3091	0x8df168		4d3b6610		CMPQ R12, 0x10(R14)													
  relater.go:3091	0x8df16c		0f8681100000		JBE 0x8e01f3														
  relater.go:3091	0x8df172		55			PUSHQ BP														
  relater.go:3091	0x8df173		4889e5			MOVQ SP, BP														
  relater.go:3091	0x8df176		4881ec68020000		SUBQ $0x268, SP														
  relater.go:3091	0x8df17d		66440fd6bc2460020000	MOVQ X15, 0x260(SP)													
  relater.go:3091	0x8df187		c644244b00		MOVB $0x0, 0x4b(SP)													
  relater.go:3091	0x8df18c		c644244600		MOVB $0x0, 0x46(SP)													
  relater.go:3092	0x8df191		80b8a100000000		CMPB 0xa1(AX), $0x0													
  relater.go:3092	0x8df198		0f857b0d0000		JNE 0x8dff19														
  ... [unrelated caller instructions omitted] ...
  relater.go:3092	0x8df1be		89b42494020000		MOVL SI, 0x294(SP)													
  relater.go:3092	0x8df1c5		4489842498020000	MOVL R8, 0x298(SP)													
  relater.go:3097	0x8df1cd		488b5008		MOVQ 0x8(AX), DX													
  relater.go:3097	0x8df1d1		4c8b00			MOVQ 0(AX), R8														
  relater.go:3097	0x8df1d4		493990b80f0000		CMPQ 0xfb8(R8), DX													
  relater.go:3097	0x8df1db		400f94c7		SETE DI															
  relater.go:3097	0x8df1df		4889d8			MOVQ BX, AX														
  relater.go:3097	0x8df1e2		4889cb			MOVQ CX, BX														
  relater.go:3097	0x8df1e5		89f1			MOVL SI, CX														
  relater.go:3097	0x8df1e7		31f6			XORL SI, SI														
  relater.go:3097	0x8df1e9		e8d270f2ff		CALL github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)						
  relater.go:3097	0x8df1ee		48898424b0000000	MOVQ AX, 0xb0(SP)													
  relater.go:3097	0x8df1f6		48899c24a8000000	MOVQ BX, 0xa8(SP)													
  relater.go:3097	0x8df1fe		884c2449		MOVB CL, 0x49(SP)													
  relater.go:3097	0x8df202		4889842488000000	MOVQ AX, 0x88(SP)													
  relater.go:3097	0x8df20a		48899c2490000000	MOVQ BX, 0x90(SP)													
  relater.go:3098	0x8df212		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3098	0x8df21a		488b5208		MOVQ 0x8(DX), DX													
  relater.go:104	0x8df21e		4889842488000000	MOVQ AX, 0x88(SP)													
  relater.go:104	0x8df226		48899c2490000000	MOVQ BX, 0x90(SP)													
  relater.go:104	0x8df22e		488b1a			MOVQ 0(DX), BX														
  relater.go:104	0x8df231		488d05c88b4e00		LEAQ 0x4e8bc8(IP), AX													
  relater.go:104	0x8df238		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:104	0x8df240		e8db2ab3ff		CALL runtime.mapaccess1(SB)												
  relater.go:104	0x8df245		8b10			MOVL 0(AX), DX														
  relater.go:3098	0x8df247		85d2			TESTL DX, DX														
  relater.go:3098	0x8df249		0f84d8010000		JE 0x8df427														
  relater.go:3092	0x8df24f		440fb6842490020000	MOVZX 0x290(SP), R8													
  relater.go:3092	0x8df258		4584c0			TESTL R8, R8														
  ... [unrelated caller instructions omitted] ...
  relater.go:3116	0x8df430		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3116	0x8df438		4883baa800000000	CMPQ 0xa8(DX), $0x0													
  relater.go:3116	0x8df440		0f8ebc0a0000		JLE 0x8dff02														
  set.go:20		0x8df446		488bb424b0000000	MOVQ 0xb0(SP), SI													
  set.go:20		0x8df44e		4889b424b8000000	MOVQ SI, 0xb8(SP)													
  set.go:20		0x8df456		488bb424a8000000	MOVQ 0xa8(SP), SI													
  set.go:20		0x8df45e		4889b424c0000000	MOVQ SI, 0xc0(SP)													
  set.go:20		0x8df466		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8df46a		488d054f254e00		LEAQ 0x4e254f(IP), AX													
  set.go:20		0x8df471		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:20		0x8df479		e8622bb3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8df47e		6690			NOPW															
  set.go:20		0x8df480		84db			TESTL BL, BL														
  relater.go:3121	0x8df482		0f85670a0000		JNE 0x8dfeef														
  relater.go:3097	0x8df488		0fb6542449		MOVZX 0x49(SP), DX													
  relater.go:3097	0x8df48d		84d2			TESTL DL, DL														
  relater.go:3127	0x8df48f		0f8483000000		JE 0x8df518														
  relater.go:3128	0x8df495		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3128	0x8df49d		4c8b4208		MOVQ 0x8(DX), R8													
  relater.go:3128	0x8df4a1		488b12			MOVQ 0(DX), DX														
  relater.go:3128	0x8df4a4		4c3982b80f0000		CMPQ 0xfb8(DX), R8													
  relater.go:3128	0x8df4ab		400f94c7		SETE DI															
  relater.go:3128	0x8df4af		488b842480020000	MOVQ 0x280(SP), AX													
  relater.go:3128	0x8df4b7		488b9c2488020000	MOVQ 0x288(SP), BX													
  relater.go:3128	0x8df4bf		8b8c2494020000		MOVL 0x294(SP), CX													
  relater.go:3128	0x8df4c6		be01000000		MOVL $0x1, SI														
  relater.go:3128	0x8df4cb		e8f06df2ff		CALL github.com/microsoft/typescript-go/internal/checker.getRelationKey(SB)						
  relater.go:3128	0x8df4d0		4889842488000000	MOVQ AX, 0x88(SP)													
  relater.go:3128	0x8df4d8		48899c2490000000	MOVQ BX, 0x90(SP)													
  set.go:20		0x8df4e0		48898424b8000000	MOVQ AX, 0xb8(SP)													
  set.go:20		0x8df4e8		48899c24c0000000	MOVQ BX, 0xc0(SP)													
  set.go:20		0x8df4f0		488b942478020000	MOVQ 0x278(SP), DX													
  set.go:20		0x8df4f8		488b5a50		MOVQ 0x50(DX), BX													
  set.go:20		0x8df4fc		488d05bd244e00		LEAQ 0x4e24bd(IP), AX													
  set.go:20		0x8df503		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:20		0x8df50b		e8d02ab3ff		CALL runtime.mapaccess2(SB)												
  set.go:20		0x8df510		84db			TESTL BL, BL														
  relater.go:3129	0x8df512		0f85c4090000		JNE 0x8dfedc														
  relater.go:3133	0x8df518		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3133	0x8df520		48837a6064		CMPQ 0x60(DX), $0x64													
  relater.go:3133	0x8df525		0f849a090000		JE 0x8dfec5														
  ... [unrelated caller instructions omitted] ...
  relater.go:3200	0x8df593		488b9c24a0000000	MOVQ 0xa0(SP), BX													
  relater.go:3138	0x8df59b		4c894240		MOVQ R8, 0x40(DX)													
  relater.go:3138	0x8df59f		498d70ff		LEAQ -0x1(R8), SI													
  relater.go:3138	0x8df5a3		48c1e604		SHLQ $0x4, SI														
  relater.go:3138	0x8df5a7		488bbc24b0000000	MOVQ 0xb0(SP), DI													
  relater.go:3138	0x8df5af		48893c30		MOVQ DI, 0(AX)(SI*1)													
  relater.go:3138	0x8df5b3		4c8b8424a8000000	MOVQ 0xa8(SP), R8													
  relater.go:3138	0x8df5bb		4c89443008		MOVQ R8, 0x8(AX)(SI*1)													
  set.go:25		0x8df5c0		48837a5000		CMPQ 0x50(DX), $0x0													
  set.go:25		0x8df5c5		7544			JNE 0x8df60b														
  set.go:26		0x8df5c7		e8f486baff		CALL runtime.makemap_small(SB)												
  set.go:26		0x8df5cc		833d3d4f610100		CMPL runtime.writeBarrier(SB), $0x0											
  set.go:26		0x8df5d3		750a			JNE 0x8df5df														
  set.go:26		0x8df5d5		488b942478020000	MOVQ 0x278(SP), DX													
  set.go:26		0x8df5dd		eb18			JMP 0x8df5f7														
  set.go:26		0x8df5df		488b942478020000	MOVQ 0x278(SP), DX													
  ... [unrelated caller instructions omitted] ...
  set.go:26		0x8df5f0		498903			MOVQ AX, 0(R11)														
  set.go:26		0x8df5f3		49897308		MOVQ SI, 0x8(R11)													
  set.go:26		0x8df5f7		48894250		MOVQ AX, 0x50(DX)													
  set.go:28		0x8df5fb		488bbc24b0000000	MOVQ 0xb0(SP), DI													
  set.go:28		0x8df603		4c8b8424a8000000	MOVQ 0xa8(SP), R8													
  set.go:28		0x8df60b		4889bc24b8000000	MOVQ DI, 0xb8(SP)													
  set.go:28		0x8df613		4c898424c0000000	MOVQ R8, 0xc0(SP)													
  set.go:28		0x8df61b		488b5a50		MOVQ 0x50(DX), BX													
  set.go:28		0x8df61f		488d059a234e00		LEAQ 0x4e239a(IP), AX													
  set.go:28		0x8df626		488d8c24b8000000	LEAQ 0xb8(SP), CX													
  set.go:28		0x8df62e		e8ad2cb3ff		CALL runtime.mapassign(SB)												
  set.go:28		0x8df633		8400			TESTB AL, 0(AX)														
  relater.go:3140	0x8df635		488b842478020000	MOVQ 0x278(SP), AX													
  relater.go:3140	0x8df63d		0fb690a0000000		MOVZX 0xa0(AX), DX													
  relater.go:3140	0x8df644		88542447		MOVB DL, 0x47(SP)													
  relater.go:3141	0x8df648		8bb42498020000		MOVL 0x298(SP), SI													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8df98b		e870b1baff		CALL runtime.rand(SB)													
  relater.go:3158	0x8df990		4889842438020000	MOVQ AX, 0x238(SP)													
  relater.go:3158	0x8df998		488b842480020000	MOVQ 0x280(SP), AX													
  relater.go:3158	0x8df9a0		8b4008			MOVL 0x8(AX), AX													
  relater.go:3158	0x8df9a3		e87808b4ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8df9a8		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8df9b0		488d0589564e00		LEAQ 0x4e5689(IP), AX													
  relater.go:3158	0x8df9b7		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8df9bf		488d0d19107200		LEAQ 0x721019(IP), CX													
  relater.go:3158	0x8df9c6		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8df9cb		e85048b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8df9d0		488d0d290b4800		LEAQ 0x480b29(IP), CX													
  relater.go:3158	0x8df9d7		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8df9da		833d2f4b610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8df9e1		750a			JNE 0x8df9ed														
  relater.go:3158	0x8df9e3		488b942408010000	MOVQ 0x108(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfa05		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfa09		488b8c2488020000	MOVQ 0x288(SP), CX													
  relater.go:3158	0x8dfa11		8b4108			MOVL 0x8(CX), AX													
  relater.go:3158	0x8dfa14		e80708b4ff		CALL runtime.convT32(SB)												
  relater.go:3158	0x8dfa19		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8dfa21		488d0518564e00		LEAQ 0x4e5618(IP), AX													
  relater.go:3158	0x8dfa28		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8dfa30		488d0db00f7200		LEAQ 0x720fb0(IP), CX													
  relater.go:3158	0x8dfa37		bf08000000		MOVL $0x8, DI														
  relater.go:3158	0x8dfa3c		0f1f4000		NOPL 0(AX)														
  relater.go:3158	0x8dfa40		e8db47b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfa45		488d0db40a4800		LEAQ 0x480ab4(IP), CX													
  relater.go:3158	0x8dfa4c		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfa4f		833dba4a610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfa56		750a			JNE 0x8dfa62														
  relater.go:3158	0x8dfa58		488b942408010000	MOVQ 0x108(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfa76		49894b08		MOVQ CX, 0x8(R11)													
  relater.go:3158	0x8dfa7a		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfa7e		488b8c2478020000	MOVQ 0x278(SP), CX													
  relater.go:3158	0x8dfa86		488b4160		MOVQ 0x60(CX), AX													
  relater.go:3158	0x8dfa8a		e8d17abaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8dfa8f		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8dfa97		488d05a2554e00		LEAQ 0x4e55a2(IP), AX													
  relater.go:3158	0x8dfa9e		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8dfaa6		488d0dcef07100		LEAQ 0x71f0ce(IP), CX													
  relater.go:3158	0x8dfaad		bf05000000		MOVL $0x5, DI														
  relater.go:3158	0x8dfab2		e86947b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfab7		488d0d02fe4700		LEAQ 0x47fe02(IP), CX													
  relater.go:3158	0x8dfabe		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfac1		833d484a610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfac8		750a			JNE 0x8dfad4														
  relater.go:3158	0x8dfaca		488b942408010000	MOVQ 0x108(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3158	0x8dfaec		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3158	0x8dfaf0		488b8c2478020000	MOVQ 0x278(SP), CX													
  relater.go:3158	0x8dfaf8		488b4178		MOVQ 0x78(CX), AX													
  relater.go:3158	0x8dfafc		0f1f4000		NOPL 0(AX)														
  relater.go:3158	0x8dfb00		e85b7abaff		CALL runtime.convT64(SB)												
  relater.go:3158	0x8dfb05		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3158	0x8dfb0d		488d052c554e00		LEAQ 0x4e552c(IP), AX													
  relater.go:3158	0x8dfb14		488d9c2430020000	LEAQ 0x230(SP), BX													
  relater.go:3158	0x8dfb1c		488d0dbf307200		LEAQ 0x7230bf(IP), CX													
  relater.go:3158	0x8dfb23		bf0b000000		MOVL $0xb, DI														
  relater.go:3158	0x8dfb28		e8f346b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3158	0x8dfb2d		488d0d8cfd4700		LEAQ 0x47fd8c(IP), CX													
  relater.go:3158	0x8dfb34		488908			MOVQ CX, 0(AX)														
  relater.go:3158	0x8dfb37		833dd249610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3158	0x8dfb3e		6690			NOPW															
  relater.go:3158	0x8dfb40		750a			JNE 0x8dfb4c														
  ... [unrelated caller instructions omitted] ...
  relater.go:3168	0x8dfba9		448b4c244c		MOVL 0x4c(SP), R9													
  relater.go:3160	0x8dfbae		b903000000		MOVL $0x3, CX														
  relater.go:3160	0x8dfbb3		31db			XORL BX, BX														
  relater.go:3167	0x8dfbb5		e9a6010000		JMP 0x8dfd60														
  relater.go:3162	0x8dfbba		4c8b00			MOVQ 0(AX), R8														
  relater.go:3162	0x8dfbbd		418400			TESTB AL, 0(R8)														
  relater.go:3162	0x8dfbc0		4d8b8088120000		MOVQ 0x1288(R8), R8													
  relater.go:3162	0x8dfbc7		4c898424e0000000	MOVQ R8, 0xe0(SP)													
  relater.go:3162	0x8dfbcf		4d85c0			TESTQ R8, R8														
  relater.go:3162	0x8dfbd2		0f8446010000		JE 0x8dfd1e														
  relater.go:3163	0x8dfbd8		e8e380baff		CALL runtime.makemap_small(SB)												
  relater.go:3163	0x8dfbdd		4889842400010000	MOVQ AX, 0x100(SP)													
  relater.go:3163	0x8dfbe5		488b842480020000	MOVQ 0x280(SP), AX													
  relater.go:3163	0x8dfbed		8b4008			MOVL 0x8(AX), AX													
  relater.go:3163	0x8dfbf0		e82b06b4ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8dfbf5		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3163	0x8dfbfd		488d053c544e00		LEAQ 0x4e543c(IP), AX													
  relater.go:3163	0x8dfc04		488b9c2400010000	MOVQ 0x100(SP), BX													
  relater.go:3163	0x8dfc0c		488d0dcc0d7200		LEAQ 0x720dcc(IP), CX													
  relater.go:3163	0x8dfc13		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8dfc18		e80346b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8dfc1d		488d0ddc084800		LEAQ 0x4808dc(IP), CX													
  relater.go:3163	0x8dfc24		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8dfc27		833de248610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8dfc2e		750a			JNE 0x8dfc3a														
  relater.go:3163	0x8dfc30		488b942408010000	MOVQ 0x108(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3163	0x8dfc50		49894b08		MOVQ CX, 0x8(R11)													
  relater.go:3163	0x8dfc54		48895008		MOVQ DX, 0x8(AX)													
  relater.go:3163	0x8dfc58		488b8c2488020000	MOVQ 0x288(SP), CX													
  relater.go:3163	0x8dfc60		8b4108			MOVL 0x8(CX), AX													
  relater.go:3163	0x8dfc63		e8b805b4ff		CALL runtime.convT32(SB)												
  relater.go:3163	0x8dfc68		4889842408010000	MOVQ AX, 0x108(SP)													
  relater.go:3163	0x8dfc70		488d05c9534e00		LEAQ 0x4e53c9(IP), AX													
  relater.go:3163	0x8dfc77		488b9c2400010000	MOVQ 0x100(SP), BX													
  relater.go:3163	0x8dfc7f		488d0d610d7200		LEAQ 0x720d61(IP), CX													
  relater.go:3163	0x8dfc86		bf08000000		MOVL $0x8, DI														
  relater.go:3163	0x8dfc8b		e89045b3ff		CALL runtime.mapassign_faststr(SB)											
  relater.go:3163	0x8dfc90		488d0d69084800		LEAQ 0x480869(IP), CX													
  relater.go:3163	0x8dfc97		488908			MOVQ CX, 0(AX)														
  relater.go:3163	0x8dfc9a		833d6f48610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:3163	0x8dfca1		750a			JNE 0x8dfcad														
  relater.go:3163	0x8dfca3		4c8b942408010000	MOVQ 0x108(SP), R10													
  ... [unrelated caller instructions omitted] ...
  relater.go:3178	0x8dfdf6		80f903			CMPL CL, $0x3														
  relater.go:3178	0x8dfdf9		750d			JNE 0x8dfe08														
  relater.go:3200	0x8dfdfb		488b9424a0000000	MOVQ 0xa0(SP), DX													
  relater.go:3200	0x8dfe03		e9a3020000		JMP 0x8e00ab														
  relater.go:3200	0x8dfe08		488b9424a0000000	MOVQ 0xa0(SP), DX													
  relater.go:3200	0x8dfe10		e910020000		JMP 0x8e0025														
  relater.go:3192	0x8dfe15		488b5008		MOVQ 0x8(AX), DX													
  relater.go:108	0x8dfe19		48833a00		CMPQ 0(DX), $0x0													
  relater.go:108	0x8dfe1d		753f			JNE 0x8dfe5e														
  relater.go:3192	0x8dfe1f		48899424f8000000	MOVQ DX, 0xf8(SP)													
  relater.go:109	0x8dfe27		e8947ebaff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8dfe2c		833ddd46610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8dfe33		750a			JNE 0x8dfe3f														
  relater.go:109	0x8dfe35		488b9424f8000000	MOVQ 0xf8(SP), DX													
  relater.go:109	0x8dfe3d		eb17			JMP 0x8dfe56														
  relater.go:109	0x8dfe3f		488b9424f8000000	MOVQ 0xf8(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3192	0x8dfe59		448b442458		MOVL 0x58(SP), R8													
  relater.go:111	0x8dfe5e		488bb424b0000000	MOVQ 0xb0(SP), SI													
  relater.go:111	0x8dfe66		4889b42488000000	MOVQ SI, 0x88(SP)													
  relater.go:111	0x8dfe6e		488bb424a8000000	MOVQ 0xa8(SP), SI													
  relater.go:111	0x8dfe76		4889b42490000000	MOVQ SI, 0x90(SP)													
  relater.go:3192	0x8dfe7e		4183c802		ORL $0x2, R8														
  relater.go:3192	0x8dfe82		4489442454		MOVL R8, 0x54(SP)													
  relater.go:111	0x8dfe87		488b1a			MOVQ 0(DX), BX														
  relater.go:111	0x8dfe8a		488d056f7f4e00		LEAQ 0x4e7f6f(IP), AX													
  relater.go:111	0x8dfe91		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:111	0x8dfe99		e84224b3ff		CALL runtime.mapassign(SB)												
  relater.go:111	0x8dfe9e		8b542454		MOVL 0x54(SP), DX													
  relater.go:111	0x8dfea2		8910			MOVL DX, 0(AX)														
  relater.go:3193	0x8dfea4		488b942478020000	MOVQ 0x278(SP), DX													
  relater.go:3193	0x8dfeac		48ff8aa8000000		DECQ 0xa8(DX)														
  relater.go:3194	0x8dfeb3		90			NOPL															
  ... [unrelated caller instructions omitted] ...
  relater.go:3183	0x8e0040		e94dffffff		JMP 0x8dff92														
  relater.go:3207	0x8e0045		e85618bbff		CALL runtime.panicBounds(SB)												
  relater.go:111	0x8e004a		4c89942488000000	MOVQ R10, 0x88(SP)													
  relater.go:111	0x8e0052		4c89842490000000	MOVQ R8, 0x90(SP)													
  relater.go:3203	0x8e005a		8b542458		MOVL 0x58(SP), DX													
  relater.go:3203	0x8e005e		83ca01			ORL $0x1, DX														
  relater.go:3203	0x8e0061		89542450		MOVL DX, 0x50(SP)													
  relater.go:111	0x8e0065		488b1e			MOVQ 0(SI), BX														
  relater.go:111	0x8e0068		488d05917d4e00		LEAQ 0x4e7d91(IP), AX													
  relater.go:111	0x8e006f		488d8c2488000000	LEAQ 0x88(SP), CX													
  relater.go:111	0x8e0077		e86422b3ff		CALL runtime.mapassign(SB)												
  relater.go:111	0x8e007c		8b542450		MOVL 0x50(SP), DX													
  relater.go:111	0x8e0080		8910			MOVL DX, 0(AX)														
  relater.go:3204	0x8e0082		488b842478020000	MOVQ 0x278(SP), AX													
  relater.go:3204	0x8e008a		48ff88a8000000		DECQ 0xa8(AX)														
  relater.go:3200	0x8e0091		488b942480000000	MOVQ 0x80(SP), DX													
  ... [unrelated caller instructions omitted] ...
  relater.go:3203	0x8e0129		488b7208		MOVQ 0x8(DX), SI													
  relater.go:3203	0x8e012d		4c8b4238		MOVQ 0x38(DX), R8													
  relater.go:3203	0x8e0131		4c8b8c2498000000	MOVQ 0x98(SP), R9													
  relater.go:3203	0x8e0139		4f8b1401		MOVQ 0(R9)(R8*1), R10													
  relater.go:3203	0x8e013d		4f8b440108		MOVQ 0x8(R9)(R8*1), R8													
  relater.go:108	0x8e0142		48833e00		CMPQ 0(SI), $0x0													
  relater.go:108	0x8e0146		0f85fefeffff		JNE 0x8e004a														
  relater.go:3203	0x8e014c		4889b424f0000000	MOVQ SI, 0xf0(SP)													
  relater.go:3203	0x8e0154		4c899424b0000000	MOVQ R10, 0xb0(SP)													
  relater.go:3203	0x8e015c		4c898424a8000000	MOVQ R8, 0xa8(SP)													
  relater.go:109	0x8e0164		e8577bbaff		CALL runtime.makemap_small(SB)												
  relater.go:109	0x8e0169		833da043610100		CMPL runtime.writeBarrier(SB), $0x0											
  relater.go:109	0x8e0170		750a			JNE 0x8e017c														
  relater.go:109	0x8e0172		488b9424f0000000	MOVQ 0xf0(SP), DX													
  relater.go:109	0x8e017a		eb17			JMP 0x8e0193														
  relater.go:109	0x8e017c		488b9424f0000000	MOVQ 0xf0(SP), DX													
