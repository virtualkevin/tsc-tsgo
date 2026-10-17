TEXT github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).get(SB) github.com/microsoft/typescript-go/internal/checker/relation_results.go
  relation_results.go:18	0x8ee980		493b6610		CMPQ SP, 0x10(R14)									
  relation_results.go:18	0x8ee984		0f8626010000		JBE 0x8eeab0										
  relation_results.go:18	0x8ee98a		55			PUSHQ BP										
  relation_results.go:18	0x8ee98b		4889e5			MOVQ SP, BP										
  relation_results.go:18	0x8ee98e		4883ec18		SUBQ $0x18, SP										
  relation_results.go:18	0x8ee992		48895c2430		MOVQ BX, 0x30(SP)									
  relation_results.go:18	0x8ee997		48894c2438		MOVQ CX, 0x38(SP)									
  relation_results.go:18	0x8ee99c		0f1f4000		NOPL 0(AX)										
  relation_results.go:19	0x8ee9a0		4885c0			TESTQ AX, AX										
  relation_results.go:19	0x8ee9a3		745c			JE 0x8eea01										
  relation_results.go:22	0x8ee9a5		488b5050		MOVQ 0x50(AX), DX									
  relation_results.go:22	0x8ee9a9		4885d2			TESTQ DX, DX										
  relation_results.go:22	0x8ee9ac		7537			JNE 0x8ee9e5										
  relation_results.go:45	0x8ee9ae		488b5008		MOVQ 0x8(AX), DX									
  relation_results.go:45	0x8ee9b2		4885d2			TESTQ DX, DX										
  relation_results.go:45	0x8ee9b5		7423			JE 0x8ee9da										
  relation_results.go:48	0x8ee9b7		488d72ff		LEAQ -0x1(DX), SI									
  relation_results.go:45	0x8ee9bb		488b38			MOVQ 0(AX), DI										
  relation_results.go:49	0x8ee9be		4989f0			MOVQ SI, R8										
  relation_results.go:49	0x8ee9c1		4821ce			ANDQ CX, SI										
  relation_results.go:50	0x8ee9c4		4883fa40		CMPQ DX, $0x40										
  relation_results.go:50	0x8ee9c8		41b940000000		MOVL $0x40, R9										
  relation_results.go:50	0x8ee9ce		4989d2			MOVQ DX, R10										
  relation_results.go:50	0x8ee9d1		490f4fd1		CMOVG R9, DX										
  relation_results.go:50	0x8ee9d5		4531c9			XORL R9, R9										
  relation_results.go:50	0x8ee9d8		eb5f			JMP 0x8eea39										
  relation_results.go:50	0x8ee9da		31c9			XORL CX, CX										
  relation_results.go:50	0x8ee9dc		48c7c2ffffffff		MOVQ $-0x1, DX										
  relation_results.go:25	0x8ee9e3		eb24			JMP 0x8eea09										
  relation_results.go:23	0x8ee9e5		488d0514a64d00		LEAQ 0x4da614(IP), AX									
  relation_results.go:23	0x8ee9ec		4889d3			MOVQ DX, BX										
  relation_results.go:23	0x8ee9ef		488d4c2430		LEAQ 0x30(SP), CX									
  relation_results.go:23	0x8ee9f4		e82733b2ff		CALL runtime.mapaccess1(SB)								
  relation_results.go:23	0x8ee9f9		8b00			MOVL 0(AX), AX										
  relation_results.go:23	0x8ee9fb		4883c418		ADDQ $0x18, SP										
  relation_results.go:23	0x8ee9ff		5d			POPQ BP											
  relation_results.go:23	0x8eea00		c3			RET											
  relation_results.go:20	0x8eea01		31c0			XORL AX, AX										
  relation_results.go:20	0x8eea03		4883c418		ADDQ $0x18, SP										
  relation_results.go:20	0x8eea07		5d			POPQ BP											
  relation_results.go:20	0x8eea08		c3			RET											
  relation_results.go:25	0x8eea09		84c9			TESTL CL, CL										
  relation_results.go:25	0x8eea0b		7416			JE 0x8eea23										
  relation_results.go:26	0x8eea0d		488b4820		MOVQ 0x20(AX), CX									
  relation_results.go:26	0x8eea11		4839ca			CMPQ DX, CX										
  relation_results.go:26	0x8eea14		7315			JAE 0x8eea2b										
  relation_results.go:26	0x8eea16		488b4818		MOVQ 0x18(AX), CX									
  relation_results.go:26	0x8eea1a		8b0491			MOVL 0(CX)(DX*4), AX									
  relation_results.go:26	0x8eea1d		4883c418		ADDQ $0x18, SP										
  relation_results.go:26	0x8eea21		5d			POPQ BP											
  relation_results.go:26	0x8eea22		c3			RET											
  relation_results.go:28	0x8eea23		31c0			XORL AX, AX										
  relation_results.go:28	0x8eea25		4883c418		ADDQ $0x18, SP										
  relation_results.go:28	0x8eea29		5d			POPQ BP											
  relation_results.go:28	0x8eea2a		c3			RET											
  relation_results.go:26	0x8eea2b		e8702ebaff		CALL runtime.panicBounds(SB)								
  relation_results.go:57	0x8eea30		48ffc6			INCQ SI											
  relation_results.go:57	0x8eea33		4c21c6			ANDQ R8, SI										
  relation_results.go:50	0x8eea36		49ffc1			INCQ R9											
  relation_results.go:50	0x8eea39		4939d1			CMPQ R9, DX										
  relation_results.go:50	0x8eea3c		7d55			JGE 0x8eea93										
  relation_results.go:39	0x8eea3e		4c8b5838		MOVQ 0x38(AX), R11									
  relation_results.go:39	0x8eea42		4989f4			MOVQ SI, R12										
  relation_results.go:39	0x8eea45		48c1fe06		SARQ $0x6, SI										
  relation_results.go:39	0x8eea49		4939f3			CMPQ R11, SI										
  relation_results.go:39	0x8eea4c		765c			JBE 0x8eeaaa										
  relation_results.go:39	0x8eea4e		4c8b5830		MOVQ 0x30(AX), R11									
  relation_results.go:39	0x8eea52		498b34f3		MOVQ 0(R11)(SI*8), SI									
  relation_results.go:39	0x8eea56		4c0fa3e6		BTQ R12, SI										
  relation_results.go:51	0x8eea5a		732d			JAE 0x8eea89										
  relation_results.go:51	0x8eea5c		0f1f4000		NOPL 0(AX)										
  relation_results.go:54	0x8eea60		4d39d4			CMPQ R12, R10										
  relation_results.go:54	0x8eea63		7340			JAE 0x8eeaa5										
  relation_results.go:54	0x8eea65		4c89e6			MOVQ R12, SI										
  relation_results.go:54	0x8eea68		49c1e404		SHLQ $0x4, R12										
  relation_results.go:54	0x8eea6c		4e8b1c27		MOVQ 0(DI)(R12*1), R11									
  relation_results.go:54	0x8eea70		4939db			CMPQ R11, BX										
  relation_results.go:54	0x8eea73		75bb			JNE 0x8eea30										
  relation_results.go:54	0x8eea75		4e8b5c2708		MOVQ 0x8(DI)(R12*1), R11								
  relation_results.go:54	0x8eea7a		4939cb			CMPQ R11, CX										
  relation_results.go:54	0x8eea7d		75b1			JNE 0x8eea30										
  relation_results.go:54	0x8eea7f		b901000000		MOVL $0x1, CX										
  relation_results.go:25	0x8eea84		4889f2			MOVQ SI, DX										
  relation_results.go:25	0x8eea87		eb80			JMP 0x8eea09										
  relation_results.go:25	0x8eea89		31c9			XORL CX, CX										
  relation_results.go:25	0x8eea8b		4c89e2			MOVQ R12, DX										
  relation_results.go:25	0x8eea8e		e976ffffff		JMP 0x8eea09										
  relation_results.go:25	0x8eea93		31c9			XORL CX, CX										
  relation_results.go:25	0x8eea95		48c7c2ffffffff		MOVQ $-0x1, DX										
  relation_results.go:25	0x8eea9c		0f1f4000		NOPL 0(AX)										
  relation_results.go:25	0x8eeaa0		e964ffffff		JMP 0x8eea09										
  relation_results.go:54	0x8eeaa5		e8f62dbaff		CALL runtime.panicBounds(SB)								
  relation_results.go:39	0x8eeaaa		e8f12dbaff		CALL runtime.panicBounds(SB)								
  relation_results.go:39	0x8eeaaf		90			NOPL											
  relation_results.go:18	0x8eeab0		4889442408		MOVQ AX, 0x8(SP)									
  relation_results.go:18	0x8eeab5		48895c2410		MOVQ BX, 0x10(SP)									
  relation_results.go:18	0x8eeaba		48894c2418		MOVQ CX, 0x18(SP)									
  relation_results.go:18	0x8eeabf		90			NOPL											
  relation_results.go:18	0x8eeac0		e83b0fbaff		CALL runtime.morestack_noctxt.abi0(SB)							
  relation_results.go:18	0x8eeac5		488b442408		MOVQ 0x8(SP), AX									
  relation_results.go:18	0x8eeaca		488b5c2410		MOVQ 0x10(SP), BX									
  relation_results.go:18	0x8eeacf		488b4c2418		MOVQ 0x18(SP), CX									
  relation_results.go:18	0x8eead4		e9a7feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).get(SB)	

TEXT github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).set(SB) github.com/microsoft/typescript-go/internal/checker/relation_results.go
  relation_results.go:71	0x8eeae0		4c8d6424a0			LEAQ -0x60(SP), R12										
  relation_results.go:71	0x8eeae5		4d3b6610			CMPQ R12, 0x10(R14)										
  relation_results.go:71	0x8eeae9		0f863c070000			JBE 0x8ef22b											
  relation_results.go:71	0x8eeaef		55				PUSHQ BP											
  relation_results.go:71	0x8eeaf0		4889e5				MOVQ SP, BP											
  relation_results.go:71	0x8eeaf3		4881ecd8000000			SUBQ $0xd8, SP											
  relation_results.go:72	0x8eeafa		48898424e8000000		MOVQ AX, 0xe8(SP)										
  relation_results.go:72	0x8eeb02		89bc2400010000			MOVL DI, 0x100(SP)										
  relation_results.go:71	0x8eeb09		48899c24f0000000		MOVQ BX, 0xf0(SP)										
  relation_results.go:71	0x8eeb11		48898c24f8000000		MOVQ CX, 0xf8(SP)										
  relation_results.go:72	0x8eeb19		488b5850			MOVQ 0x50(AX), BX										
  relation_results.go:72	0x8eeb1d		0f1f00				NOPL 0(AX)											
  relation_results.go:72	0x8eeb20		4885db				TESTQ BX, BX											
  relation_results.go:72	0x8eeb23		0f8590010000			JNE 0x8eecb9											
  relation_results.go:77	0x8eeb29		4883780800			CMPQ 0x8(AX), $0x0										
  relation_results.go:77	0x8eeb2e		0f8542010000			JNE 0x8eec76											
  relation_results.go:114	0x8eeb34		488d0525f35400			LEAQ 0x54f325(IP), AX										
  relation_results.go:114	0x8eeb3b		bb08000000			MOVL $0x8, BX											
  relation_results.go:114	0x8eeb40		4889d9				MOVQ BX, CX											
  relation_results.go:114	0x8eeb43		e838d5b9ff			CALL runtime.makeslice(SB)									
  relation_results.go:114	0x8eeb48		48898424d0000000		MOVQ AX, 0xd0(SP)										
  relation_results.go:115	0x8eeb50		488d05292e4700			LEAQ 0x472e29(IP), AX										
  relation_results.go:115	0x8eeb57		bb08000000			MOVL $0x8, BX											
  relation_results.go:115	0x8eeb5c		4889d9				MOVQ BX, CX											
  relation_results.go:115	0x8eeb5f		90				NOPL												
  relation_results.go:115	0x8eeb60		e81bd5b9ff			CALL runtime.makeslice(SB)									
  relation_results.go:115	0x8eeb65		48898424c8000000		MOVQ AX, 0xc8(SP)										
  relation_results.go:116	0x8eeb6d		488d054c1e4700			LEAQ 0x471e4c(IP), AX										
  relation_results.go:116	0x8eeb74		bb01000000			MOVL $0x1, BX											
  relation_results.go:116	0x8eeb79		4889d9				MOVQ BX, CX											
  relation_results.go:116	0x8eeb7c		0f1f4000			NOPL 0(AX)											
  relation_results.go:116	0x8eeb80		e8fbd4b9ff			CALL runtime.makeslice(SB)									
  relation_results.go:78	0x8eeb85		488d4c2460			LEAQ 0x60(SP), CX										
  relation_results.go:78	0x8eeb8a		440f1139			MOVUPS X15, 0(CX)										
  relation_results.go:78	0x8eeb8e		440f117910			MOVUPS X15, 0x10(CX)										
  relation_results.go:78	0x8eeb93		440f117920			MOVUPS X15, 0x20(CX)										
  relation_results.go:78	0x8eeb98		440f117930			MOVUPS X15, 0x30(CX)										
  relation_results.go:78	0x8eeb9d		440f117940			MOVUPS X15, 0x40(CX)										
  relation_results.go:78	0x8eeba2		440f117948			MOVUPS X15, 0x48(CX)										
  relation_results.go:114	0x8eeba7		488b9424d0000000		MOVQ 0xd0(SP), DX										
  relation_results.go:114	0x8eebaf		4889542460			MOVQ DX, 0x60(SP)										
  relation_results.go:114	0x8eebb4		48c744246808000000		MOVQ $0x8, 0x68(SP)										
  relation_results.go:114	0x8eebbd		48c744247008000000		MOVQ $0x8, 0x70(SP)										
  relation_results.go:115	0x8eebc6		488b9424c8000000		MOVQ 0xc8(SP), DX										
  relation_results.go:115	0x8eebce		4889542478			MOVQ DX, 0x78(SP)										
  relation_results.go:115	0x8eebd3		48c784248000000008000000	MOVQ $0x8, 0x80(SP)										
  relation_results.go:115	0x8eebdf		48c784248800000008000000	MOVQ $0x8, 0x88(SP)										
  relation_results.go:116	0x8eebeb		4889842490000000		MOVQ AX, 0x90(SP)										
  relation_results.go:116	0x8eebf3		48c784249800000001000000	MOVQ $0x1, 0x98(SP)										
  relation_results.go:116	0x8eebff		48c78424a000000001000000	MOVQ $0x1, 0xa0(SP)										
  relation_results.go:78	0x8eec0b		833dfe78600100			CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:78	0x8eec12		7419				JE 0x8eec2d											
  relation_results.go:78	0x8eec14		488d0525385900			LEAQ 0x593825(IP), AX										
  relation_results.go:78	0x8eec1b		488b9c24e8000000		MOVQ 0xe8(SP), BX										
  relation_results.go:78	0x8eec23		e8f85ab3ff			CALL runtime.wbMove(SB)										
  relation_results.go:78	0x8eec28		488d4c2460			LEAQ 0x60(SP), CX										
  relation_results.go:78	0x8eec2d		488b8424e8000000		MOVQ 0xe8(SP), AX										
  relation_results.go:78	0x8eec35		440f1031			MOVUPS 0(CX), X14										
  relation_results.go:78	0x8eec39		440f1130			MOVUPS X14, 0(AX)										
  relation_results.go:78	0x8eec3d		440f107110			MOVUPS 0x10(CX), X14										
  relation_results.go:78	0x8eec42		440f117010			MOVUPS X14, 0x10(AX)										
  relation_results.go:78	0x8eec47		440f107120			MOVUPS 0x20(CX), X14										
  relation_results.go:78	0x8eec4c		440f117020			MOVUPS X14, 0x20(AX)										
  relation_results.go:78	0x8eec51		440f107130			MOVUPS 0x30(CX), X14										
  relation_results.go:78	0x8eec56		440f117030			MOVUPS X14, 0x30(AX)										
  relation_results.go:78	0x8eec5b		440f107140			MOVUPS 0x40(CX), X14										
  relation_results.go:78	0x8eec60		440f117040			MOVUPS X14, 0x40(AX)										
  relation_results.go:78	0x8eec65		440f107148			MOVUPS 0x48(CX), X14										
  relation_results.go:78	0x8eec6a		440f117048			MOVUPS X14, 0x48(AX)										
  relation_results.go:83	0x8eec6f		8bbc2400010000			MOVL 0x100(SP), DI										
  relation_results.go:45	0x8eec76		488b5008			MOVQ 0x8(AX), DX										
  relation_results.go:45	0x8eec7a		4885d2				TESTQ DX, DX											
  relation_results.go:45	0x8eec7d		742f				JE 0x8eecae											
  relation_results.go:80	0x8eec7f		4c8b8424f8000000		MOVQ 0xf8(SP), R8										
  relation_results.go:48	0x8eec87		4c8d4aff			LEAQ -0x1(DX), R9										
  relation_results.go:80	0x8eec8b		4c8b9424f0000000		MOVQ 0xf0(SP), R10										
  relation_results.go:49	0x8eec93		4d89c3				MOVQ R8, R11											
  relation_results.go:49	0x8eec96		4d21c8				ANDQ R9, R8											
  relation_results.go:50	0x8eec99		4883fa40			CMPQ DX, $0x40											
  relation_results.go:50	0x8eec9d		41bc40000000			MOVL $0x40, R12											
  relation_results.go:50	0x8eeca3		490f4fd4			CMOVG R12, DX											
  relation_results.go:50	0x8eeca7		31c9				XORL CX, CX											
  relation_results.go:50	0x8eeca9		e9f6040000			JMP 0x8ef1a4											
  relation_results.go:50	0x8eecae		31c9				XORL CX, CX											
  relation_results.go:50	0x8eecb0		48c7c2ffffffff			MOVQ $-0x1, DX											
  relation_results.go:80	0x8eecb7		eb47				JMP 0x8eed00											
  relation_results.go:73	0x8eecb9		488d0540a34d00			LEAQ 0x4da340(IP), AX										
  relation_results.go:73	0x8eecc0		488d8c24f0000000		LEAQ 0xf0(SP), CX										
  relation_results.go:73	0x8eecc8		e81336b2ff			CALL runtime.mapassign(SB)									
  relation_results.go:73	0x8eeccd		8b942400010000			MOVL 0x100(SP), DX										
  relation_results.go:73	0x8eecd4		8910				MOVL DX, 0(AX)											
  relation_results.go:74	0x8eecd6		488b9424e8000000		MOVQ 0xe8(SP), DX										
  relation_results.go:74	0x8eecde		488b7250			MOVQ 0x50(DX), SI										
  relation_results.go:74	0x8eece2		4885f6				TESTQ SI, SI											
  relation_results.go:74	0x8eece5		7405				JE 0x8eecec											
  relation_results.go:74	0x8eece7		488b06				MOVQ 0(SI), AX											
  relation_results.go:74	0x8eecea		eb02				JMP 0x8eecee											
  relation_results.go:74	0x8eecec		31c0				XORL AX, AX											
  relation_results.go:74	0x8eecee		48894248			MOVQ AX, 0x48(DX)										
  relation_results.go:75	0x8eecf2		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:75	0x8eecf9		5d				POPQ BP												
  relation_results.go:75	0x8eecfa		c3				RET												
  relation_results.go:75	0x8eecfb		0f1f440000			NOPL 0(AX)(AX*1)										
  relation_results.go:80	0x8eed00		84c9				TESTL CL, CL											
  relation_results.go:81	0x8eed02		0f8581010000			JNE 0x8eee89											
  relation_results.go:86	0x8eed08		4885d2				TESTQ DX, DX											
  relation_results.go:86	0x8eed0b		0f8c29010000			JL 0x8eee3a											
  relation_results.go:90	0x8eed11		488b5848			MOVQ 0x48(AX), BX										
  relation_results.go:90	0x8eed15		4c8b4008			MOVQ 0x8(AX), R8										
  relation_results.go:90	0x8eed19		4d89c1				MOVQ R8, R9											
  relation_results.go:90	0x8eed1c		49c1e802			SHRQ $0x2, R8											
  relation_results.go:90	0x8eed20		4d89ca				MOVQ R9, R10											
  relation_results.go:90	0x8eed23		4d29c1				SUBQ R8, R9											
  relation_results.go:90	0x8eed26		4c39cb				CMPQ BX, R9											
  relation_results.go:90	0x8eed29		0f8c94000000			JL 0x8eedc3											
  relation_results.go:91	0x8eed2f		90				NOPL												
  relation_results.go:106	0x8eed30		4983fa08			CMPQ R10, $0x8											
  relation_results.go:106	0x8eed34		7c18				JL 0x8eed4e											
  relation_results.go:106	0x8eed36		498d52ff			LEAQ -0x1(R10), DX										
  relation_results.go:106	0x8eed3a		4985d2				TESTQ DX, R10											
  relation_results.go:106	0x8eed3d		750f				JNE 0x8eed4e											
  relation_results.go:106	0x8eed3f		48baffffffffffffff03		MOVQ $0x3ffffffffffffff, DX									
  relation_results.go:106	0x8eed49		4939d2				CMPQ R10, DX											
  relation_results.go:106	0x8eed4c		7e4e				JLE 0x8eed9c											
  relation_results.go:144	0x8eed4e		48ffc3				INCQ BX												
  relation_results.go:93	0x8eed51		488b9424f0000000		MOVQ 0xf0(SP), DX										
  relation_results.go:93	0x8eed59		4889542430			MOVQ DX, 0x30(SP)										
  relation_results.go:93	0x8eed5e		488b9424f8000000		MOVQ 0xf8(SP), DX										
  relation_results.go:93	0x8eed66		4889542458			MOVQ DX, 0x58(SP)										
  relation_results.go:144	0x8eed6b		488d058ea24d00			LEAQ 0x4da28e(IP), AX										
  relation_results.go:144	0x8eed72		31c9				XORL CX, CX											
  relation_results.go:144	0x8eed74		e8878fb9ff			CALL runtime.makemap(SB)									
  relation_results.go:144	0x8eed79		48898424b8000000		MOVQ AX, 0xb8(SP)										
  relation_results.go:145	0x8eed81		488b9424e8000000		MOVQ 0xe8(SP), DX										
  relation_results.go:145	0x8eed89		488b32				MOVQ 0(DX), SI											
  relation_results.go:145	0x8eed8c		488b7a08			MOVQ 0x8(DX), DI										
  relation_results.go:145	0x8eed90		48897c2450			MOVQ DI, 0x50(SP)										
  relation_results.go:145	0x8eed95		31c9				XORL CX, CX											
  relation_results.go:145	0x8eed97		e996020000			JMP 0x8ef032											
  relation_results.go:96	0x8eed9c		488b8c24f0000000		MOVQ 0xf0(SP), CX										
  relation_results.go:96	0x8eeda4		488b9424f8000000		MOVQ 0xf8(SP), DX										
  relation_results.go:109	0x8eedac		4b8d1c12			LEAQ 0(R10)(R10*1), BX										
  relation_results.go:96	0x8eedb0		89fe				MOVL DI, SI											
  relation_results.go:96	0x8eedb2		4889d7				MOVQ DX, DI											
  relation_results.go:96	0x8eedb5		e8a6040000			CALL github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).rebuild(SB)	
  relation_results.go:97	0x8eedba		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:97	0x8eedc1		5d				POPQ BP												
  relation_results.go:97	0x8eedc2		c3				RET												
  relation_results.go:64	0x8eedc3		4c39d2				CMPQ DX, R10											
  relation_results.go:64	0x8eedc6		0f8359020000			JAE 0x8ef025											
  relation_results.go:90	0x8eedcc		488b08				MOVQ 0(AX), CX											
  relation_results.go:99	0x8eedcf		488b9c24f0000000		MOVQ 0xf0(SP), BX										
  relation_results.go:99	0x8eedd7		488bb424f8000000		MOVQ 0xf8(SP), SI										
  relation_results.go:64	0x8eeddf		4989d0				MOVQ DX, R8											
  relation_results.go:64	0x8eede2		48c1e204			SHLQ $0x4, DX											
  relation_results.go:64	0x8eede6		48891c11			MOVQ BX, 0(CX)(DX*1)										
  relation_results.go:64	0x8eedea		4889741108			MOVQ SI, 0x8(CX)(DX*1)										
  relation_results.go:65	0x8eedef		488b4838			MOVQ 0x38(AX), CX										
  relation_results.go:65	0x8eedf3		4c89c2				MOVQ R8, DX											
  relation_results.go:65	0x8eedf6		49c1e806			SHRQ $0x6, R8											
  relation_results.go:65	0x8eedfa		660f1f440000			NOPW 0(AX)(AX*1)										
  relation_results.go:65	0x8eee00		4c39c1				CMPQ CX, R8											
  relation_results.go:65	0x8eee03		0f8614020000			JBE 0x8ef01d											
  relation_results.go:65	0x8eee09		488b4830			MOVQ 0x30(AX), CX										
  relation_results.go:65	0x8eee0d		4a8b1cc1			MOVQ 0(CX)(R8*8), BX										
  relation_results.go:65	0x8eee11		480fabd3			BTSQ DX, BX											
  relation_results.go:65	0x8eee15		4a891cc1			MOVQ BX, 0(CX)(R8*8)										
  relation_results.go:66	0x8eee19		48ff4048			INCQ 0x48(AX)											
  relation_results.go:68	0x8eee1d		488b4820			MOVQ 0x20(AX), CX										
  relation_results.go:68	0x8eee21		4839ca				CMPQ DX, CX											
  relation_results.go:68	0x8eee24		0f83ee010000			JAE 0x8ef018											
  relation_results.go:68	0x8eee2a		488b4018			MOVQ 0x18(AX), AX										
  relation_results.go:68	0x8eee2e		893c90				MOVL DI, 0(AX)(DX*4)										
  relation_results.go:100	0x8eee31		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:100	0x8eee38		5d				POPQ BP												
  relation_results.go:100	0x8eee39		c3				RET												
  relation_results.go:144	0x8eee3a		488b5848			MOVQ 0x48(AX), BX										
  relation_results.go:144	0x8eee3e		48ffc3				INCQ BX												
  relation_results.go:87	0x8eee41		488b9424f0000000		MOVQ 0xf0(SP), DX										
  relation_results.go:87	0x8eee49		4889542430			MOVQ DX, 0x30(SP)										
  relation_results.go:87	0x8eee4e		488b9424f8000000		MOVQ 0xf8(SP), DX										
  relation_results.go:87	0x8eee56		4889542458			MOVQ DX, 0x58(SP)										
  relation_results.go:144	0x8eee5b		488d059ea14d00			LEAQ 0x4da19e(IP), AX										
  relation_results.go:144	0x8eee62		31c9				XORL CX, CX											
  relation_results.go:144	0x8eee64		e8978eb9ff			CALL runtime.makemap(SB)									
  relation_results.go:144	0x8eee69		48898424c0000000		MOVQ AX, 0xc0(SP)										
  relation_results.go:145	0x8eee71		488b9424e8000000		MOVQ 0xe8(SP), DX										
  relation_results.go:145	0x8eee79		488b32				MOVQ 0(DX), SI											
  relation_results.go:145	0x8eee7c		488b7a08			MOVQ 0x8(DX), DI										
  relation_results.go:145	0x8eee80		48897c2450			MOVQ DI, 0x50(SP)										
  relation_results.go:145	0x8eee85		31c9				XORL CX, CX											
  relation_results.go:145	0x8eee87		eb26				JMP 0x8eeeaf											
  relation_results.go:83	0x8eee89		488b4820			MOVQ 0x20(AX), CX										
  relation_results.go:83	0x8eee8d		4839ca				CMPQ DX, CX											
  relation_results.go:83	0x8eee90		7310				JAE 0x8eeea2											
  relation_results.go:83	0x8eee92		488b4018			MOVQ 0x18(AX), AX										
  relation_results.go:83	0x8eee96		893c90				MOVL DI, 0(AX)(DX*4)										
  relation_results.go:84	0x8eee99		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:84	0x8eeea0		5d				POPQ BP												
  relation_results.go:84	0x8eeea1		c3				RET												
  relation_results.go:83	0x8eeea2		e8f929baff			CALL runtime.panicBounds(SB)									
  relation_results.go:145	0x8eeea7		4883c610			ADDQ $0x10, SI											
  relation_results.go:145	0x8eeeab		498d4901			LEAQ 0x1(R9), CX										
  relation_results.go:145	0x8eeeaf		4839f9				CMPQ CX, DI											
  relation_results.go:145	0x8eeeb2		0f8d9a000000			JGE 0x8eef52											
  relation_results.go:39	0x8eeeb8		4c8b4238			MOVQ 0x38(DX), R8										
  relation_results.go:39	0x8eeebc		4989c9				MOVQ CX, R9											
  relation_results.go:39	0x8eeebf		48c1e906			SHRQ $0x6, CX											
  relation_results.go:39	0x8eeec3		4939c8				CMPQ R8, CX											
  relation_results.go:39	0x8eeec6		0f8647010000			JBE 0x8ef013											
  relation_results.go:39	0x8eeecc		4c8b4230			MOVQ 0x30(DX), R8										
  relation_results.go:39	0x8eeed0		4d8b04c8			MOVQ 0(R8)(CX*8), R8										
  relation_results.go:39	0x8eeed4		4d0fa3c8			BTQ R9, R8											
  relation_results.go:146	0x8eeed8		73cd				JAE 0x8eeea7											
  relation_results.go:145	0x8eeeda		4c8b06				MOVQ 0(SI), R8											
  relation_results.go:145	0x8eeedd		4c8b5608			MOVQ 0x8(SI), R10										
  relation_results.go:147	0x8eeee1		4c89442438			MOVQ R8, 0x38(SP)										
  relation_results.go:147	0x8eeee6		4c89542440			MOVQ R10, 0x40(SP)										
  relation_results.go:147	0x8eeeeb		4c8b4220			MOVQ 0x20(DX), R8										
  relation_results.go:147	0x8eeeef		4d39c1				CMPQ R9, R8											
  relation_results.go:147	0x8eeef2		0f8316010000			JAE 0x8ef00e											
  relation_results.go:145	0x8eeef8		4c894c2448			MOVQ R9, 0x48(SP)										
  relation_results.go:145	0x8eeefd		4889b424d0000000		MOVQ SI, 0xd0(SP)										
  relation_results.go:147	0x8eef05		488b5218			MOVQ 0x18(DX), DX										
  relation_results.go:147	0x8eef09		428b148a			MOVL 0(DX)(R9*4), DX										
  relation_results.go:147	0x8eef0d		8954242c			MOVL DX, 0x2c(SP)										
  relation_results.go:147	0x8eef11		4889c3				MOVQ AX, BX											
  relation_results.go:147	0x8eef14		488d4c2438			LEAQ 0x38(SP), CX										
  relation_results.go:147	0x8eef19		488d05e0a04d00			LEAQ 0x4da0e0(IP), AX										
  relation_results.go:147	0x8eef20		e8bb33b2ff			CALL runtime.mapassign(SB)									
  relation_results.go:147	0x8eef25		8b54242c			MOVL 0x2c(SP), DX										
  relation_results.go:147	0x8eef29		8910				MOVL DX, 0(AX)											
  relation_results.go:150	0x8eef2b		488b8424c0000000		MOVQ 0xc0(SP), AX										
  relation_results.go:39	0x8eef33		488b9424e8000000		MOVQ 0xe8(SP), DX										
  relation_results.go:145	0x8eef3b		488bb424d0000000		MOVQ 0xd0(SP), SI										
  relation_results.go:145	0x8eef43		488b7c2450			MOVQ 0x50(SP), DI										
  relation_results.go:145	0x8eef48		4c8b4c2448			MOVQ 0x48(SP), R9										
  relation_results.go:147	0x8eef4d		e955ffffff			JMP 0x8eeea7											
  relation_results.go:150	0x8eef52		488b542430			MOVQ 0x30(SP), DX										
  relation_results.go:150	0x8eef57		4889542438			MOVQ DX, 0x38(SP)										
  relation_results.go:150	0x8eef5c		488b542458			MOVQ 0x58(SP), DX										
  relation_results.go:150	0x8eef61		4889542440			MOVQ DX, 0x40(SP)										
  relation_results.go:150	0x8eef66		4889c3				MOVQ AX, BX											
  relation_results.go:150	0x8eef69		488d4c2438			LEAQ 0x38(SP), CX										
  relation_results.go:150	0x8eef6e		488d058ba04d00			LEAQ 0x4da08b(IP), AX										
  relation_results.go:150	0x8eef75		e86633b2ff			CALL runtime.mapassign(SB)									
  relation_results.go:150	0x8eef7a		8b942400010000			MOVL 0x100(SP), DX										
  relation_results.go:150	0x8eef81		8910				MOVL DX, 0(AX)											
  relation_results.go:151	0x8eef83		488b9424c0000000		MOVQ 0xc0(SP), DX										
  relation_results.go:151	0x8eef8b		4885d2				TESTQ DX, DX											
  relation_results.go:151	0x8eef8e		7405				JE 0x8eef95											
  relation_results.go:151	0x8eef90		488b0a				MOVQ 0(DX), CX											
  relation_results.go:151	0x8eef93		eb02				JMP 0x8eef97											
  relation_results.go:151	0x8eef95		31c9				XORL CX, CX											
  relation_results.go:151	0x8eef97		833d7275600100			CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:151	0x8eef9e		6690				NOPW												
  relation_results.go:151	0x8eefa0		7436				JE 0x8eefd8											
  relation_results.go:151	0x8eefa2		48894c2450			MOVQ CX, 0x50(SP)										
  relation_results.go:151	0x8eefa7		488b9c24e8000000		MOVQ 0xe8(SP), BX										
  relation_results.go:151	0x8eefaf		488b4b50			MOVQ 0x50(BX), CX										
  relation_results.go:151	0x8eefb3		e84825baff			CALL runtime.gcWriteBarrier2(SB)								
  relation_results.go:151	0x8eefb8		498913				MOVQ DX, 0(R11)											
  relation_results.go:151	0x8eefbb		49894b08			MOVQ CX, 0x8(R11)										
  relation_results.go:151	0x8eefbf		488d057a345900			LEAQ 0x59347a(IP), AX										
  relation_results.go:151	0x8eefc6		e83557b3ff			CALL runtime.wbZero(SB)										
  relation_results.go:151	0x8eefcb		488b4c2450			MOVQ 0x50(SP), CX										
  relation_results.go:151	0x8eefd0		488b9424c0000000		MOVQ 0xc0(SP), DX										
  relation_results.go:151	0x8eefd8		488b8424e8000000		MOVQ 0xe8(SP), AX										
  relation_results.go:151	0x8eefe0		440f1138			MOVUPS X15, 0(AX)										
  relation_results.go:151	0x8eefe4		440f117810			MOVUPS X15, 0x10(AX)										
  relation_results.go:151	0x8eefe9		440f117820			MOVUPS X15, 0x20(AX)										
  relation_results.go:151	0x8eefee		440f117830			MOVUPS X15, 0x30(AX)										
  relation_results.go:151	0x8eeff3		440f117840			MOVUPS X15, 0x40(AX)										
  relation_results.go:151	0x8eeff8		440f117848			MOVUPS X15, 0x48(AX)										
  relation_results.go:151	0x8eeffd		48895050			MOVQ DX, 0x50(AX)										
  relation_results.go:151	0x8ef001		48894848			MOVQ CX, 0x48(AX)										
  relation_results.go:88	0x8ef005		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:88	0x8ef00c		5d				POPQ BP												
  relation_results.go:88	0x8ef00d		c3				RET												
  relation_results.go:147	0x8ef00e		e88d28baff			CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef013		e88828baff			CALL runtime.panicBounds(SB)									
  relation_results.go:68	0x8ef018		e88328baff			CALL runtime.panicBounds(SB)									
  relation_results.go:65	0x8ef01d		0f1f00				NOPL 0(AX)											
  relation_results.go:65	0x8ef020		e87b28baff			CALL runtime.panicBounds(SB)									
  relation_results.go:64	0x8ef025		e87628baff			CALL runtime.panicBounds(SB)									
  relation_results.go:145	0x8ef02a		4883c610			ADDQ $0x10, SI											
  relation_results.go:145	0x8ef02e		498d4901			LEAQ 0x1(R9), CX										
  relation_results.go:145	0x8ef032		4839f9				CMPQ CX, DI											
  relation_results.go:145	0x8ef035		0f8d9a000000			JGE 0x8ef0d5											
  relation_results.go:39	0x8ef03b		4c8b4238			MOVQ 0x38(DX), R8										
  relation_results.go:39	0x8ef03f		4989c9				MOVQ CX, R9											
  relation_results.go:39	0x8ef042		48c1e906			SHRQ $0x6, CX											
  relation_results.go:39	0x8ef046		4939c8				CMPQ R8, CX											
  relation_results.go:39	0x8ef049		0f8645010000			JBE 0x8ef194											
  relation_results.go:39	0x8ef04f		4c8b4230			MOVQ 0x30(DX), R8										
  relation_results.go:39	0x8ef053		4d8b04c8			MOVQ 0(R8)(CX*8), R8										
  relation_results.go:39	0x8ef057		4d0fa3c8			BTQ R9, R8											
  relation_results.go:146	0x8ef05b		73cd				JAE 0x8ef02a											
  relation_results.go:145	0x8ef05d		4c8b06				MOVQ 0(SI), R8											
  relation_results.go:145	0x8ef060		4c8b5608			MOVQ 0x8(SI), R10										
  relation_results.go:147	0x8ef064		4c89442438			MOVQ R8, 0x38(SP)										
  relation_results.go:147	0x8ef069		4c89542440			MOVQ R10, 0x40(SP)										
  relation_results.go:147	0x8ef06e		4c8b4220			MOVQ 0x20(DX), R8										
  relation_results.go:147	0x8ef072		4d39c1				CMPQ R9, R8											
  relation_results.go:147	0x8ef075		0f8314010000			JAE 0x8ef18f											
  relation_results.go:145	0x8ef07b		4c894c2448			MOVQ R9, 0x48(SP)										
  relation_results.go:145	0x8ef080		4889b424d0000000		MOVQ SI, 0xd0(SP)										
  relation_results.go:147	0x8ef088		488b5218			MOVQ 0x18(DX), DX										
  relation_results.go:147	0x8ef08c		428b148a			MOVL 0(DX)(R9*4), DX										
  relation_results.go:147	0x8ef090		8954242c			MOVL DX, 0x2c(SP)										
  relation_results.go:147	0x8ef094		4889c3				MOVQ AX, BX											
  relation_results.go:147	0x8ef097		488d4c2438			LEAQ 0x38(SP), CX										
  relation_results.go:147	0x8ef09c		488d055d9f4d00			LEAQ 0x4d9f5d(IP), AX										
  relation_results.go:147	0x8ef0a3		e83832b2ff			CALL runtime.mapassign(SB)									
  relation_results.go:147	0x8ef0a8		8b54242c			MOVL 0x2c(SP), DX										
  relation_results.go:147	0x8ef0ac		8910				MOVL DX, 0(AX)											
  relation_results.go:150	0x8ef0ae		488b8424b8000000		MOVQ 0xb8(SP), AX										
  relation_results.go:39	0x8ef0b6		488b9424e8000000		MOVQ 0xe8(SP), DX										
  relation_results.go:145	0x8ef0be		488bb424d0000000		MOVQ 0xd0(SP), SI										
  relation_results.go:145	0x8ef0c6		488b7c2450			MOVQ 0x50(SP), DI										
  relation_results.go:145	0x8ef0cb		4c8b4c2448			MOVQ 0x48(SP), R9										
  relation_results.go:147	0x8ef0d0		e955ffffff			JMP 0x8ef02a											
  relation_results.go:150	0x8ef0d5		488b542430			MOVQ 0x30(SP), DX										
  relation_results.go:150	0x8ef0da		4889542438			MOVQ DX, 0x38(SP)										
  relation_results.go:150	0x8ef0df		488b542458			MOVQ 0x58(SP), DX										
  relation_results.go:150	0x8ef0e4		4889542440			MOVQ DX, 0x40(SP)										
  relation_results.go:150	0x8ef0e9		4889c3				MOVQ AX, BX											
  relation_results.go:150	0x8ef0ec		488d4c2438			LEAQ 0x38(SP), CX										
  relation_results.go:150	0x8ef0f1		488d05089f4d00			LEAQ 0x4d9f08(IP), AX										
  relation_results.go:150	0x8ef0f8		e8e331b2ff			CALL runtime.mapassign(SB)									
  relation_results.go:150	0x8ef0fd		8b942400010000			MOVL 0x100(SP), DX										
  relation_results.go:150	0x8ef104		8910				MOVL DX, 0(AX)											
  relation_results.go:151	0x8ef106		488b9424b8000000		MOVQ 0xb8(SP), DX										
  relation_results.go:151	0x8ef10e		4885d2				TESTQ DX, DX											
  relation_results.go:151	0x8ef111		7405				JE 0x8ef118											
  relation_results.go:151	0x8ef113		488b0a				MOVQ 0(DX), CX											
  relation_results.go:151	0x8ef116		eb02				JMP 0x8ef11a											
  relation_results.go:151	0x8ef118		31c9				XORL CX, CX											
  relation_results.go:151	0x8ef11a		833def73600100			CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:151	0x8ef121		7436				JE 0x8ef159											
  relation_results.go:151	0x8ef123		48894c2450			MOVQ CX, 0x50(SP)										
  relation_results.go:151	0x8ef128		488b9c24e8000000		MOVQ 0xe8(SP), BX										
  relation_results.go:151	0x8ef130		488b4b50			MOVQ 0x50(BX), CX										
  relation_results.go:151	0x8ef134		e8c723baff			CALL runtime.gcWriteBarrier2(SB)								
  relation_results.go:151	0x8ef139		498913				MOVQ DX, 0(R11)											
  relation_results.go:151	0x8ef13c		49894b08			MOVQ CX, 0x8(R11)										
  relation_results.go:151	0x8ef140		488d05f9325900			LEAQ 0x5932f9(IP), AX										
  relation_results.go:151	0x8ef147		e8b455b3ff			CALL runtime.wbZero(SB)										
  relation_results.go:151	0x8ef14c		488b4c2450			MOVQ 0x50(SP), CX										
  relation_results.go:151	0x8ef151		488b9424b8000000		MOVQ 0xb8(SP), DX										
  relation_results.go:151	0x8ef159		488b8424e8000000		MOVQ 0xe8(SP), AX										
  relation_results.go:151	0x8ef161		440f1138			MOVUPS X15, 0(AX)										
  relation_results.go:151	0x8ef165		440f117810			MOVUPS X15, 0x10(AX)										
  relation_results.go:151	0x8ef16a		440f117820			MOVUPS X15, 0x20(AX)										
  relation_results.go:151	0x8ef16f		440f117830			MOVUPS X15, 0x30(AX)										
  relation_results.go:151	0x8ef174		440f117840			MOVUPS X15, 0x40(AX)										
  relation_results.go:151	0x8ef179		440f117848			MOVUPS X15, 0x48(AX)										
  relation_results.go:151	0x8ef17e		48895050			MOVQ DX, 0x50(AX)										
  relation_results.go:151	0x8ef182		48894848			MOVQ CX, 0x48(AX)										
  relation_results.go:94	0x8ef186		4881c4d8000000			ADDQ $0xd8, SP											
  relation_results.go:94	0x8ef18d		5d				POPQ BP												
  relation_results.go:94	0x8ef18e		c3				RET												
  relation_results.go:147	0x8ef18f		e80c27baff			CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef194		e80727baff			CALL runtime.panicBounds(SB)									
  relation_results.go:57	0x8ef199		4d8d442401			LEAQ 0x1(R12), R8										
  relation_results.go:57	0x8ef19e		4d21c8				ANDQ R9, R8											
  relation_results.go:50	0x8ef1a1		48ffc1				INCQ CX												
  relation_results.go:50	0x8ef1a4		4839d1				CMPQ CX, DX											
  relation_results.go:50	0x8ef1a7		7d66				JGE 0x8ef20f											
  relation_results.go:39	0x8ef1a9		4c8b6038			MOVQ 0x38(AX), R12										
  relation_results.go:39	0x8ef1ad		4d89c5				MOVQ R8, R13											
  relation_results.go:39	0x8ef1b0		49c1f806			SARQ $0x6, R8											
  relation_results.go:39	0x8ef1b4		4d39c4				CMPQ R12, R8											
  relation_results.go:39	0x8ef1b7		766c				JBE 0x8ef225											
  relation_results.go:39	0x8ef1b9		4c8b6030			MOVQ 0x30(AX), R12										
  relation_results.go:39	0x8ef1bd		4f8b04c4			MOVQ 0(R12)(R8*8), R8										
  relation_results.go:39	0x8ef1c1		4d0fa3e8			BTQ R13, R8											
  relation_results.go:51	0x8ef1c5		733e				JAE 0x8ef205											
  relation_results.go:54	0x8ef1c7		4c89542438			MOVQ R10, 0x38(SP)										
  relation_results.go:54	0x8ef1cc		4c895c2440			MOVQ R11, 0x40(SP)										
  relation_results.go:54	0x8ef1d1		4c8b4008			MOVQ 0x8(AX), R8										
  relation_results.go:54	0x8ef1d5		4d39c5				CMPQ R13, R8											
  relation_results.go:54	0x8ef1d8		7343				JAE 0x8ef21d											
  relation_results.go:54	0x8ef1da		4c8b00				MOVQ 0(AX), R8											
  relation_results.go:54	0x8ef1dd		4d89ec				MOVQ R13, R12											
  relation_results.go:54	0x8ef1e0		49c1e504			SHLQ $0x4, R13											
  relation_results.go:54	0x8ef1e4		4f8b3c28			MOVQ 0(R8)(R13*1), R15										
  relation_results.go:54	0x8ef1e8		4d39d7				CMPQ R15, R10											
  relation_results.go:54	0x8ef1eb		75ac				JNE 0x8ef199											
  relation_results.go:54	0x8ef1ed		4f8b442808			MOVQ 0x8(R8)(R13*1), R8										
  relation_results.go:54	0x8ef1f2		4d39d8				CMPQ R8, R11											
  relation_results.go:54	0x8ef1f5		75a2				JNE 0x8ef199											
  relation_results.go:54	0x8ef1f7		b901000000			MOVL $0x1, CX											
  relation_results.go:80	0x8ef1fc		4c89e2				MOVQ R12, DX											
  relation_results.go:80	0x8ef1ff		90				NOPL												
  relation_results.go:80	0x8ef200		e9fbfaffff			JMP 0x8eed00											
  relation_results.go:80	0x8ef205		31c9				XORL CX, CX											
  relation_results.go:80	0x8ef207		4c89ea				MOVQ R13, DX											
  relation_results.go:80	0x8ef20a		e9f1faffff			JMP 0x8eed00											
  relation_results.go:80	0x8ef20f		31c9				XORL CX, CX											
  relation_results.go:80	0x8ef211		48c7c2ffffffff			MOVQ $-0x1, DX											
  relation_results.go:80	0x8ef218		e9e3faffff			JMP 0x8eed00											
  relation_results.go:54	0x8ef21d		0f1f00				NOPL 0(AX)											
  relation_results.go:54	0x8ef220		e87b26baff			CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef225		e87626baff			CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef22a		90				NOPL												
  relation_results.go:71	0x8ef22b		4889442408			MOVQ AX, 0x8(SP)										
  relation_results.go:71	0x8ef230		48895c2410			MOVQ BX, 0x10(SP)										
  relation_results.go:71	0x8ef235		48894c2418			MOVQ CX, 0x18(SP)										
  relation_results.go:71	0x8ef23a		897c2420			MOVL DI, 0x20(SP)										
  relation_results.go:71	0x8ef23e		6690				NOPW												
  relation_results.go:71	0x8ef240		e8bb07baff			CALL runtime.morestack_noctxt.abi0(SB)								
  relation_results.go:71	0x8ef245		488b442408			MOVQ 0x8(SP), AX										
  relation_results.go:71	0x8ef24a		488b5c2410			MOVQ 0x10(SP), BX										
  relation_results.go:71	0x8ef24f		488b4c2418			MOVQ 0x18(SP), CX										
  relation_results.go:71	0x8ef254		8b7c2420			MOVL 0x20(SP), DI										
  relation_results.go:71	0x8ef258		e983f8ffff			JMP github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).set(SB)		

TEXT github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).rebuild(SB) github.com/microsoft/typescript-go/internal/checker/relation_results.go
  relation_results.go:122	0x8ef260		4c8da42450ffffff	LEAQ 0xffffff50(SP), R12									
  relation_results.go:122	0x8ef268		4d3b6610		CMPQ R12, 0x10(R14)										
  relation_results.go:122	0x8ef26c		0f86cd080000		JBE 0x8efb3f											
  relation_results.go:122	0x8ef272		55			PUSHQ BP											
  relation_results.go:122	0x8ef273		4889e5			MOVQ SP, BP											
  relation_results.go:122	0x8ef276		4881ec28010000		SUBQ $0x128, SP											
  relation_results.go:124	0x8ef27d		4889842438010000	MOVQ AX, 0x138(SP)										
  relation_results.go:124	0x8ef285		48899c2440010000	MOVQ BX, 0x140(SP)										
  relation_results.go:124	0x8ef28d		89b42458010000		MOVL SI, 0x158(SP)										
  relation_results.go:124	0x8ef294		48897c2450		MOVQ DI, 0x50(SP)										
  relation_results.go:124	0x8ef299		48894c2448		MOVQ CX, 0x48(SP)										
  relation_results.go:116	0x8ef29e		488d533f		LEAQ 0x3f(BX), DX										
  relation_results.go:116	0x8ef2a2		48c1fa3f		SARQ $0x3f, DX											
  relation_results.go:116	0x8ef2a6		48c1ea3a		SHRQ $0x3a, DX											
  relation_results.go:116	0x8ef2aa		488d1413		LEAQ 0(BX)(DX*1), DX										
  relation_results.go:116	0x8ef2ae		488d523f		LEAQ 0x3f(DX), DX										
  relation_results.go:116	0x8ef2b2		48c1fa06		SARQ $0x6, DX											
  relation_results.go:116	0x8ef2b6		4889542440		MOVQ DX, 0x40(SP)										
  relation_results.go:114	0x8ef2bb		488d059eeb5400		LEAQ 0x54eb9e(IP), AX										
  relation_results.go:114	0x8ef2c2		4889d9			MOVQ BX, CX											
  relation_results.go:114	0x8ef2c5		e8b6cdb9ff		CALL runtime.makeslice(SB)									
  relation_results.go:114	0x8ef2ca		4889842420010000	MOVQ AX, 0x120(SP)										
  relation_results.go:115	0x8ef2d2		488d05a7264700		LEAQ 0x4726a7(IP), AX										
  relation_results.go:115	0x8ef2d9		488b9c2440010000	MOVQ 0x140(SP), BX										
  relation_results.go:115	0x8ef2e1		4889d9			MOVQ BX, CX											
  relation_results.go:115	0x8ef2e4		e897cdb9ff		CALL runtime.makeslice(SB)									
  relation_results.go:115	0x8ef2e9		4889842418010000	MOVQ AX, 0x118(SP)										
  relation_results.go:116	0x8ef2f1		488d05c8164700		LEAQ 0x4716c8(IP), AX										
  relation_results.go:116	0x8ef2f8		488b5c2440		MOVQ 0x40(SP), BX										
  relation_results.go:116	0x8ef2fd		4889d9			MOVQ BX, CX											
  relation_results.go:116	0x8ef300		e87bcdb9ff		CALL runtime.makeslice(SB)									
  relation_results.go:123	0x8ef305		488d542458		LEAQ 0x58(SP), DX										
  relation_results.go:123	0x8ef30a		440f113a		MOVUPS X15, 0(DX)										
  relation_results.go:123	0x8ef30e		440f117a10		MOVUPS X15, 0x10(DX)										
  relation_results.go:123	0x8ef313		440f117a20		MOVUPS X15, 0x20(DX)										
  relation_results.go:123	0x8ef318		440f117a30		MOVUPS X15, 0x30(DX)										
  relation_results.go:123	0x8ef31d		440f117a40		MOVUPS X15, 0x40(DX)										
  relation_results.go:123	0x8ef322		440f117a48		MOVUPS X15, 0x48(DX)										
  relation_results.go:114	0x8ef327		488bb42420010000	MOVQ 0x120(SP), SI										
  relation_results.go:114	0x8ef32f		4889742458		MOVQ SI, 0x58(SP)										
  relation_results.go:114	0x8ef334		488bb42440010000	MOVQ 0x140(SP), SI										
  relation_results.go:114	0x8ef33c		4889742460		MOVQ SI, 0x60(SP)										
  relation_results.go:114	0x8ef341		4889742468		MOVQ SI, 0x68(SP)										
  relation_results.go:115	0x8ef346		488bbc2418010000	MOVQ 0x118(SP), DI										
  relation_results.go:115	0x8ef34e		48897c2470		MOVQ DI, 0x70(SP)										
  relation_results.go:115	0x8ef353		4889742478		MOVQ SI, 0x78(SP)										
  relation_results.go:115	0x8ef358		4889b42480000000	MOVQ SI, 0x80(SP)										
  relation_results.go:116	0x8ef360		4889842488000000	MOVQ AX, 0x88(SP)										
  relation_results.go:116	0x8ef368		488b742440		MOVQ 0x40(SP), SI										
  relation_results.go:116	0x8ef36d		4889b42490000000	MOVQ SI, 0x90(SP)										
  relation_results.go:116	0x8ef375		4889b42498000000	MOVQ SI, 0x98(SP)										
  relation_results.go:123	0x8ef37d		488d8c24b0000000	LEAQ 0xb0(SP), CX										
  relation_results.go:123	0x8ef385		440f1032		MOVUPS 0(DX), X14										
  relation_results.go:123	0x8ef389		440f1131		MOVUPS X14, 0(CX)										
  relation_results.go:123	0x8ef38d		440f107210		MOVUPS 0x10(DX), X14										
  relation_results.go:123	0x8ef392		440f117110		MOVUPS X14, 0x10(CX)										
  relation_results.go:123	0x8ef397		440f107220		MOVUPS 0x20(DX), X14										
  relation_results.go:123	0x8ef39c		440f117120		MOVUPS X14, 0x20(CX)										
  relation_results.go:123	0x8ef3a1		440f107230		MOVUPS 0x30(DX), X14										
  relation_results.go:123	0x8ef3a6		440f117130		MOVUPS X14, 0x30(CX)										
  relation_results.go:123	0x8ef3ab		440f107240		MOVUPS 0x40(DX), X14										
  relation_results.go:123	0x8ef3b0		440f117140		MOVUPS X14, 0x40(CX)										
  relation_results.go:123	0x8ef3b5		440f107248		MOVUPS 0x48(DX), X14										
  relation_results.go:123	0x8ef3ba		440f117148		MOVUPS X14, 0x48(CX)										
  relation_results.go:124	0x8ef3bf		488b9c2438010000	MOVQ 0x138(SP), BX										
  relation_results.go:124	0x8ef3c7		488b13			MOVQ 0(BX), DX											
  relation_results.go:124	0x8ef3ca		488b7308		MOVQ 0x8(BX), SI										
  relation_results.go:124	0x8ef3ce		31c0			XORL AX, AX											
  relation_results.go:124	0x8ef3d0		eb08			JMP 0x8ef3da											
  relation_results.go:124	0x8ef3d2		4883c210		ADDQ $0x10, DX											
  relation_results.go:124	0x8ef3d6		498d4001		LEAQ 0x1(R8), AX										
  relation_results.go:124	0x8ef3da		4839f0			CMPQ AX, SI											
  relation_results.go:124	0x8ef3dd		7d66			JGE 0x8ef445											
  relation_results.go:39	0x8ef3df		488b7b38		MOVQ 0x38(BX), DI										
  relation_results.go:39	0x8ef3e3		4989c0			MOVQ AX, R8											
  relation_results.go:39	0x8ef3e6		48c1e806		SHRQ $0x6, AX											
  relation_results.go:39	0x8ef3ea		4839c7			CMPQ DI, AX											
  relation_results.go:39	0x8ef3ed		0f8646070000		JBE 0x8efb39											
  relation_results.go:39	0x8ef3f3		488b7b30		MOVQ 0x30(BX), DI										
  relation_results.go:39	0x8ef3f7		488b3cc7		MOVQ 0(DI)(AX*8), DI										
  relation_results.go:39	0x8ef3fb		4c0fa3c7		BTQ R8, DI											
  relation_results.go:39	0x8ef3ff		90			NOPL												
  relation_results.go:125	0x8ef400		73d0			JAE 0x8ef3d2											
  relation_results.go:45	0x8ef402		488bbc24b8000000	MOVQ 0xb8(SP), DI										
  relation_results.go:124	0x8ef40a		4c8b4a08		MOVQ 0x8(DX), R9										
  relation_results.go:124	0x8ef40e		4c8b12			MOVQ 0(DX), R10											
  relation_results.go:45	0x8ef411		4885ff			TESTQ DI, DI											
  relation_results.go:45	0x8ef414		750f			JNE 0x8ef425											
  relation_results.go:45	0x8ef416		49c7c7ffffffff		MOVQ $-0x1, R15											
  relation_results.go:45	0x8ef41d		31c0			XORL AX, AX											
  relation_results.go:45	0x8ef41f		90			NOPL												
  relation_results.go:126	0x8ef420		e99b040000		JMP 0x8ef8c0											
  relation_results.go:48	0x8ef425		4c8d5fff		LEAQ -0x1(DI), R11										
  relation_results.go:49	0x8ef429		4d89dc			MOVQ R11, R12											
  relation_results.go:49	0x8ef42c		4d21cb			ANDQ R9, R11											
  relation_results.go:50	0x8ef42f		4883ff40		CMPQ DI, $0x40											
  relation_results.go:50	0x8ef433		41bd40000000		MOVL $0x40, R13											
  relation_results.go:50	0x8ef439		490f4ffd		CMOVG R13, DI											
  relation_results.go:50	0x8ef43d		31c0			XORL AX, AX											
  relation_results.go:50	0x8ef43f		90			NOPL												
  relation_results.go:50	0x8ef440		e9c7030000		JMP 0x8ef80c											
  relation_results.go:45	0x8ef445		488b9424b8000000	MOVQ 0xb8(SP), DX										
  relation_results.go:45	0x8ef44d		4885d2			TESTQ DX, DX											
  relation_results.go:45	0x8ef450		7429			JE 0x8ef47b											
  relation_results.go:48	0x8ef452		488d72ff		LEAQ -0x1(DX), SI										
  relation_results.go:49	0x8ef456		488b7c2450		MOVQ 0x50(SP), DI										
  relation_results.go:49	0x8ef45b		4989f8			MOVQ DI, R8											
  relation_results.go:49	0x8ef45e		4821f7			ANDQ SI, DI											
  relation_results.go:50	0x8ef461		4883fa40		CMPQ DX, $0x40											
  relation_results.go:50	0x8ef465		41b940000000		MOVL $0x40, R9											
  relation_results.go:50	0x8ef46b		490f4fd1		CMOVG R9, DX											
  relation_results.go:50	0x8ef46f		4c8b4c2448		MOVQ 0x48(SP), R9										
  relation_results.go:50	0x8ef474		31c0			XORL AX, AX											
  relation_results.go:50	0x8ef476		e9e7020000		JMP 0x8ef762											
  relation_results.go:50	0x8ef47b		48c7c0ffffffff		MOVQ $-0x1, AX											
  relation_results.go:50	0x8ef482		31d2			XORL DX, DX											
  relation_results.go:135	0x8ef484		4885c0			TESTQ AX, AX											
  relation_results.go:135	0x8ef487		7d3c			JGE 0x8ef4c5											
  relation_results.go:144	0x8ef489		488b5b48		MOVQ 0x48(BX), BX										
  relation_results.go:144	0x8ef48d		48ffc3			INCQ BX												
  relation_results.go:136	0x8ef490		90			NOPL												
  relation_results.go:144	0x8ef491		488d05689b4d00		LEAQ 0x4d9b68(IP), AX										
  relation_results.go:144	0x8ef498		31c9			XORL CX, CX											
  relation_results.go:144	0x8ef49a		e86188b9ff		CALL runtime.makemap(SB)									
  relation_results.go:144	0x8ef49f		4889842408010000	MOVQ AX, 0x108(SP)										
  relation_results.go:145	0x8ef4a7		488b942438010000	MOVQ 0x138(SP), DX										
  relation_results.go:145	0x8ef4af		488b32			MOVQ 0(DX), SI											
  relation_results.go:145	0x8ef4b2		488b7a08		MOVQ 0x8(DX), DI										
  relation_results.go:145	0x8ef4b6		48897c2440		MOVQ DI, 0x40(SP)										
  relation_results.go:145	0x8ef4bb		31c9			XORL CX, CX											
  relation_results.go:145	0x8ef4bd		0f1f00			NOPL 0(AX)											
  relation_results.go:145	0x8ef4c0		e91e010000		JMP 0x8ef5e3											
  relation_results.go:139	0x8ef4c5		90			NOPL												
  relation_results.go:134	0x8ef4c6		84d2			TESTL DL, DL											
  relation_results.go:63	0x8ef4c8		7405			JE 0x8ef4cf											
  relation_results.go:68	0x8ef4ca		4889c7			MOVQ AX, DI											
  relation_results.go:63	0x8ef4cd		eb76			JMP 0x8ef545											
  relation_results.go:64	0x8ef4cf		488b9424b8000000	MOVQ 0xb8(SP), DX										
  relation_results.go:64	0x8ef4d7		660f1f840000000000	NOPW 0(AX)(AX*1)										
  relation_results.go:64	0x8ef4e0		4839d0			CMPQ AX, DX											
  relation_results.go:64	0x8ef4e3		0f83ed000000		JAE 0x8ef5d6											
  relation_results.go:64	0x8ef4e9		488b9424b0000000	MOVQ 0xb0(SP), DX										
  relation_results.go:64	0x8ef4f1		4889c6			MOVQ AX, SI											
  relation_results.go:64	0x8ef4f4		48c1e004		SHLQ $0x4, AX											
  relation_results.go:64	0x8ef4f8		488b7c2448		MOVQ 0x48(SP), DI										
  relation_results.go:64	0x8ef4fd		48893c02		MOVQ DI, 0(DX)(AX*1)										
  relation_results.go:64	0x8ef501		488b7c2450		MOVQ 0x50(SP), DI										
  relation_results.go:64	0x8ef506		48897c0208		MOVQ DI, 0x8(DX)(AX*1)										
  relation_results.go:65	0x8ef50b		488b9424e8000000	MOVQ 0xe8(SP), DX										
  relation_results.go:65	0x8ef513		4889f7			MOVQ SI, DI											
  relation_results.go:65	0x8ef516		48c1ee06		SHRQ $0x6, SI											
  relation_results.go:65	0x8ef51a		660f1f440000		NOPW 0(AX)(AX*1)										
  relation_results.go:65	0x8ef520		4839f2			CMPQ DX, SI											
  relation_results.go:65	0x8ef523		0f86a8000000		JBE 0x8ef5d1											
  relation_results.go:65	0x8ef529		488b9424e0000000	MOVQ 0xe0(SP), DX										
  relation_results.go:65	0x8ef531		4c8b04f2		MOVQ 0(DX)(SI*8), R8										
  relation_results.go:65	0x8ef535		490fabf8		BTSQ DI, R8											
  relation_results.go:65	0x8ef539		4c8904f2		MOVQ R8, 0(DX)(SI*8)										
  relation_results.go:66	0x8ef53d		48ff8424f8000000	INCQ 0xf8(SP)											
  relation_results.go:68	0x8ef545		488b9424d0000000	MOVQ 0xd0(SP), DX										
  relation_results.go:68	0x8ef54d		4839d7			CMPQ DI, DX											
  relation_results.go:68	0x8ef550		737a			JAE 0x8ef5cc											
  relation_results.go:68	0x8ef552		488b9424c8000000	MOVQ 0xc8(SP), DX										
  relation_results.go:68	0x8ef55a		8bb42458010000		MOVL 0x158(SP), SI										
  relation_results.go:68	0x8ef561		8934ba			MOVL SI, 0(DX)(DI*4)										
  relation_results.go:140	0x8ef564		833da56f600100		CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:140	0x8ef56b		741c			JE 0x8ef589											
  relation_results.go:140	0x8ef56d		488d05cc2e5900		LEAQ 0x592ecc(IP), AX										
  relation_results.go:140	0x8ef574		e8a751b3ff		CALL runtime.wbMove(SB)										
  relation_results.go:123	0x8ef579		488d8c24b0000000	LEAQ 0xb0(SP), CX										
  relation_results.go:140	0x8ef581		488b9c2438010000	MOVQ 0x138(SP), BX										
  relation_results.go:140	0x8ef589		440f1031		MOVUPS 0(CX), X14										
  relation_results.go:140	0x8ef58d		440f1133		MOVUPS X14, 0(BX)										
  relation_results.go:140	0x8ef591		440f107110		MOVUPS 0x10(CX), X14										
  relation_results.go:140	0x8ef596		440f117310		MOVUPS X14, 0x10(BX)										
  relation_results.go:140	0x8ef59b		440f107120		MOVUPS 0x20(CX), X14										
  relation_results.go:140	0x8ef5a0		440f117320		MOVUPS X14, 0x20(BX)										
  relation_results.go:140	0x8ef5a5		440f107130		MOVUPS 0x30(CX), X14										
  relation_results.go:140	0x8ef5aa		440f117330		MOVUPS X14, 0x30(BX)										
  relation_results.go:140	0x8ef5af		440f107140		MOVUPS 0x40(CX), X14										
  relation_results.go:140	0x8ef5b4		440f117340		MOVUPS X14, 0x40(BX)										
  relation_results.go:140	0x8ef5b9		440f107148		MOVUPS 0x48(CX), X14										
  relation_results.go:140	0x8ef5be		440f117348		MOVUPS X14, 0x48(BX)										
  relation_results.go:141	0x8ef5c3		4881c428010000		ADDQ $0x128, SP											
  relation_results.go:141	0x8ef5ca		5d			POPQ BP												
  relation_results.go:141	0x8ef5cb		c3			RET												
  relation_results.go:68	0x8ef5cc		e8cf22baff		CALL runtime.panicBounds(SB)									
  relation_results.go:65	0x8ef5d1		e8ca22baff		CALL runtime.panicBounds(SB)									
  relation_results.go:64	0x8ef5d6		e8c522baff		CALL runtime.panicBounds(SB)									
  relation_results.go:145	0x8ef5db		4883c610		ADDQ $0x10, SI											
  relation_results.go:145	0x8ef5df		498d4901		LEAQ 0x1(R9), CX										
  relation_results.go:145	0x8ef5e3		4839f9			CMPQ CX, DI											
  relation_results.go:145	0x8ef5e6		0f8da6000000		JGE 0x8ef692											
  relation_results.go:39	0x8ef5ec		4c8b4238		MOVQ 0x38(DX), R8										
  relation_results.go:39	0x8ef5f0		4989c9			MOVQ CX, R9											
  relation_results.go:39	0x8ef5f3		48c1e906		SHRQ $0x6, CX											
  relation_results.go:39	0x8ef5f7		660f1f840000000000	NOPW 0(AX)(AX*1)										
  relation_results.go:39	0x8ef600		4939c8			CMPQ R8, CX											
  relation_results.go:39	0x8ef603		0f864a010000		JBE 0x8ef753											
  relation_results.go:39	0x8ef609		4c8b4230		MOVQ 0x30(DX), R8										
  relation_results.go:39	0x8ef60d		4d8b04c8		MOVQ 0(R8)(CX*8), R8										
  relation_results.go:39	0x8ef611		4d0fa3c8		BTQ R9, R8											
  relation_results.go:146	0x8ef615		73c4			JAE 0x8ef5db											
  relation_results.go:145	0x8ef617		4c8b06			MOVQ 0(SI), R8											
  relation_results.go:145	0x8ef61a		4c8b5608		MOVQ 0x8(SI), R10										
  relation_results.go:147	0x8ef61e		4c89442428		MOVQ R8, 0x28(SP)										
  relation_results.go:147	0x8ef623		4c89542430		MOVQ R10, 0x30(SP)										
  relation_results.go:147	0x8ef628		4c8b4220		MOVQ 0x20(DX), R8										
  relation_results.go:147	0x8ef62c		4d39c1			CMPQ R9, R8											
  relation_results.go:147	0x8ef62f		0f8319010000		JAE 0x8ef74e											
  relation_results.go:145	0x8ef635		4c894c2438		MOVQ R9, 0x38(SP)										
  relation_results.go:145	0x8ef63a		4889b42420010000	MOVQ SI, 0x120(SP)										
  relation_results.go:147	0x8ef642		488b5218		MOVQ 0x18(DX), DX										
  relation_results.go:147	0x8ef646		428b148a		MOVL 0(DX)(R9*4), DX										
  relation_results.go:147	0x8ef64a		8954241c		MOVL DX, 0x1c(SP)										
  relation_results.go:147	0x8ef64e		4889c3			MOVQ AX, BX											
  relation_results.go:147	0x8ef651		488d4c2428		LEAQ 0x28(SP), CX										
  relation_results.go:147	0x8ef656		488d05a3994d00		LEAQ 0x4d99a3(IP), AX										
  relation_results.go:147	0x8ef65d		0f1f00			NOPL 0(AX)											
  relation_results.go:147	0x8ef660		e87b2cb2ff		CALL runtime.mapassign(SB)									
  relation_results.go:147	0x8ef665		8b54241c		MOVL 0x1c(SP), DX										
  relation_results.go:147	0x8ef669		8910			MOVL DX, 0(AX)											
  relation_results.go:150	0x8ef66b		488b842408010000	MOVQ 0x108(SP), AX										
  relation_results.go:39	0x8ef673		488b942438010000	MOVQ 0x138(SP), DX										
  relation_results.go:145	0x8ef67b		488bb42420010000	MOVQ 0x120(SP), SI										
  relation_results.go:145	0x8ef683		488b7c2440		MOVQ 0x40(SP), DI										
  relation_results.go:145	0x8ef688		4c8b4c2438		MOVQ 0x38(SP), R9										
  relation_results.go:147	0x8ef68d		e949ffffff		JMP 0x8ef5db											
  relation_results.go:150	0x8ef692		488b542448		MOVQ 0x48(SP), DX										
  relation_results.go:150	0x8ef697		4889542428		MOVQ DX, 0x28(SP)										
  relation_results.go:150	0x8ef69c		488b542450		MOVQ 0x50(SP), DX										
  relation_results.go:150	0x8ef6a1		4889542430		MOVQ DX, 0x30(SP)										
  relation_results.go:150	0x8ef6a6		4889c3			MOVQ AX, BX											
  relation_results.go:150	0x8ef6a9		488d4c2428		LEAQ 0x28(SP), CX										
  relation_results.go:150	0x8ef6ae		488d054b994d00		LEAQ 0x4d994b(IP), AX										
  relation_results.go:150	0x8ef6b5		e8262cb2ff		CALL runtime.mapassign(SB)									
  relation_results.go:150	0x8ef6ba		8b942458010000		MOVL 0x158(SP), DX										
  relation_results.go:150	0x8ef6c1		8910			MOVL DX, 0(AX)											
  relation_results.go:151	0x8ef6c3		488b942408010000	MOVQ 0x108(SP), DX										
  relation_results.go:151	0x8ef6cb		4885d2			TESTQ DX, DX											
  relation_results.go:151	0x8ef6ce		7405			JE 0x8ef6d5											
  relation_results.go:151	0x8ef6d0		488b0a			MOVQ 0(DX), CX											
  relation_results.go:151	0x8ef6d3		eb02			JMP 0x8ef6d7											
  relation_results.go:151	0x8ef6d5		31c9			XORL CX, CX											
  relation_results.go:151	0x8ef6d7		833d326e600100		CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:151	0x8ef6de		6690			NOPW												
  relation_results.go:151	0x8ef6e0		7436			JE 0x8ef718											
  relation_results.go:151	0x8ef6e2		48894c2440		MOVQ CX, 0x40(SP)										
  relation_results.go:151	0x8ef6e7		488b9c2438010000	MOVQ 0x138(SP), BX										
  relation_results.go:151	0x8ef6ef		488b4b50		MOVQ 0x50(BX), CX										
  relation_results.go:151	0x8ef6f3		e8081ebaff		CALL runtime.gcWriteBarrier2(SB)								
  relation_results.go:151	0x8ef6f8		498913			MOVQ DX, 0(R11)											
  relation_results.go:151	0x8ef6fb		49894b08		MOVQ CX, 0x8(R11)										
  relation_results.go:151	0x8ef6ff		488d053a2d5900		LEAQ 0x592d3a(IP), AX										
  relation_results.go:151	0x8ef706		e8f54fb3ff		CALL runtime.wbZero(SB)										
  relation_results.go:151	0x8ef70b		488b4c2440		MOVQ 0x40(SP), CX										
  relation_results.go:151	0x8ef710		488b942408010000	MOVQ 0x108(SP), DX										
  relation_results.go:151	0x8ef718		488b842438010000	MOVQ 0x138(SP), AX										
  relation_results.go:151	0x8ef720		440f1138		MOVUPS X15, 0(AX)										
  relation_results.go:151	0x8ef724		440f117810		MOVUPS X15, 0x10(AX)										
  relation_results.go:151	0x8ef729		440f117820		MOVUPS X15, 0x20(AX)										
  relation_results.go:151	0x8ef72e		440f117830		MOVUPS X15, 0x30(AX)										
  relation_results.go:151	0x8ef733		440f117840		MOVUPS X15, 0x40(AX)										
  relation_results.go:151	0x8ef738		440f117848		MOVUPS X15, 0x48(AX)										
  relation_results.go:151	0x8ef73d		48895050		MOVQ DX, 0x50(AX)										
  relation_results.go:151	0x8ef741		48894848		MOVQ CX, 0x48(AX)										
  relation_results.go:137	0x8ef745		4881c428010000		ADDQ $0x128, SP											
  relation_results.go:137	0x8ef74c		5d			POPQ BP												
  relation_results.go:137	0x8ef74d		c3			RET												
  relation_results.go:147	0x8ef74e		e84d21baff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef753		e84821baff		CALL runtime.panicBounds(SB)									
  relation_results.go:57	0x8ef758		498d7a01		LEAQ 0x1(R10), DI										
  relation_results.go:57	0x8ef75c		4821f7			ANDQ SI, DI											
  relation_results.go:50	0x8ef75f		48ffc0			INCQ AX												
  relation_results.go:50	0x8ef762		4839d0			CMPQ AX, DX											
  relation_results.go:50	0x8ef765		7d77			JGE 0x8ef7de											
  relation_results.go:39	0x8ef767		4c8b9424e8000000	MOVQ 0xe8(SP), R10										
  relation_results.go:39	0x8ef76f		4989fb			MOVQ DI, R11											
  relation_results.go:39	0x8ef772		48c1ff06		SARQ $0x6, DI											
  relation_results.go:39	0x8ef776		4939fa			CMPQ R10, DI											
  relation_results.go:39	0x8ef779		7676			JBE 0x8ef7f1											
  relation_results.go:39	0x8ef77b		4c8b9424e0000000	MOVQ 0xe0(SP), R10										
  relation_results.go:39	0x8ef783		498b3cfa		MOVQ 0(R10)(DI*8), DI										
  relation_results.go:39	0x8ef787		4c0fa3df		BTQ R11, DI											
  relation_results.go:51	0x8ef78b		7347			JAE 0x8ef7d4											
  relation_results.go:54	0x8ef78d		4c894c2428		MOVQ R9, 0x28(SP)										
  relation_results.go:54	0x8ef792		4c89442430		MOVQ R8, 0x30(SP)										
  relation_results.go:54	0x8ef797		488bbc24b8000000	MOVQ 0xb8(SP), DI										
  relation_results.go:54	0x8ef79f		90			NOPL												
  relation_results.go:54	0x8ef7a0		4939fb			CMPQ R11, DI											
  relation_results.go:54	0x8ef7a3		7347			JAE 0x8ef7ec											
  relation_results.go:54	0x8ef7a5		488bbc24b0000000	MOVQ 0xb0(SP), DI										
  relation_results.go:54	0x8ef7ad		4d89da			MOVQ R11, R10											
  relation_results.go:54	0x8ef7b0		49c1e304		SHLQ $0x4, R11											
  relation_results.go:54	0x8ef7b4		4d8b243b		MOVQ 0(R11)(DI*1), R12										
  relation_results.go:54	0x8ef7b8		4d39cc			CMPQ R12, R9											
  relation_results.go:54	0x8ef7bb		759b			JNE 0x8ef758											
  relation_results.go:54	0x8ef7bd		498b7c3b08		MOVQ 0x8(R11)(DI*1), DI										
  relation_results.go:54	0x8ef7c2		4c39c7			CMPQ DI, R8											
  relation_results.go:54	0x8ef7c5		7591			JNE 0x8ef758											
  relation_results.go:134	0x8ef7c7		4c89d0			MOVQ R10, AX											
  relation_results.go:134	0x8ef7ca		ba01000000		MOVL $0x1, DX											
  relation_results.go:134	0x8ef7cf		e9b0fcffff		JMP 0x8ef484											
  relation_results.go:134	0x8ef7d4		4c89d8			MOVQ R11, AX											
  relation_results.go:134	0x8ef7d7		31d2			XORL DX, DX											
  relation_results.go:134	0x8ef7d9		e9a6fcffff		JMP 0x8ef484											
  relation_results.go:134	0x8ef7de		48c7c0ffffffff		MOVQ $-0x1, AX											
  relation_results.go:134	0x8ef7e5		31d2			XORL DX, DX											
  relation_results.go:134	0x8ef7e7		e998fcffff		JMP 0x8ef484											
  relation_results.go:54	0x8ef7ec		e8af20baff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8ef7f1		e8aa20baff		CALL runtime.panicBounds(SB)									
  relation_results.go:57	0x8ef7f6		4c8b5c2420		MOVQ 0x20(SP), R11										
  relation_results.go:57	0x8ef7fb		49ffc3			INCQ R11											
  relation_results.go:57	0x8ef7fe		4d21e3			ANDQ R12, R11											
  relation_results.go:50	0x8ef801		48ffc0			INCQ AX												
  relation_results.go:123	0x8ef804		488d8c24b0000000	LEAQ 0xb0(SP), CX										
  relation_results.go:50	0x8ef80c		4839f8			CMPQ AX, DI											
  relation_results.go:50	0x8ef80f		0f8d9a000000		JGE 0x8ef8af											
  relation_results.go:50	0x8ef815		4c895c2420		MOVQ R11, 0x20(SP)										
  relation_results.go:39	0x8ef81a		4c8bbc24e8000000	MOVQ 0xe8(SP), R15										
  relation_results.go:39	0x8ef822		49c1fb06		SARQ $0x6, R11											
  relation_results.go:39	0x8ef826		4d39df			CMPQ R15, R11											
  relation_results.go:39	0x8ef829		0f8605030000		JBE 0x8efb34											
  relation_results.go:39	0x8ef82f		4c8bbc24e0000000	MOVQ 0xe0(SP), R15										
  relation_results.go:39	0x8ef837		4f8b1cdf		MOVQ 0(R15)(R11*8), R11										
  relation_results.go:39	0x8ef83b		4c8b7c2420		MOVQ 0x20(SP), R15										
  relation_results.go:39	0x8ef840		4d0fa3fb		BTQ R15, R11											
  relation_results.go:51	0x8ef844		7365			JAE 0x8ef8ab											
  relation_results.go:54	0x8ef846		4c89542428		MOVQ R10, 0x28(SP)										
  relation_results.go:54	0x8ef84b		4c894c2430		MOVQ R9, 0x30(SP)										
  relation_results.go:54	0x8ef850		4c8b9c24b8000000	MOVQ 0xb8(SP), R11										
  relation_results.go:54	0x8ef858		0f1f840000000000	NOPL 0(AX)(AX*1)										
  relation_results.go:54	0x8ef860		4d39df			CMPQ R15, R11											
  relation_results.go:54	0x8ef863		0f83c6020000		JAE 0x8efb2f											
  relation_results.go:54	0x8ef869		4c8b9c24b0000000	MOVQ 0xb0(SP), R11										
  relation_results.go:54	0x8ef871		49c1e704		SHLQ $0x4, R15											
  relation_results.go:54	0x8ef875		4b8b0c1f		MOVQ 0(R15)(R11*1), CX										
  relation_results.go:54	0x8ef879		0f1f8000000000		NOPL 0(AX)											
  relation_results.go:54	0x8ef880		4c39d1			CMPQ CX, R10											
  relation_results.go:54	0x8ef883		0f856dffffff		JNE 0x8ef7f6											
  relation_results.go:54	0x8ef889		4f8b5c1f08		MOVQ 0x8(R15)(R11*1), R11									
  relation_results.go:54	0x8ef88e		4d39cb			CMPQ R11, R9											
  relation_results.go:54	0x8ef891		0f855fffffff		JNE 0x8ef7f6											
  relation_results.go:123	0x8ef897		488d8c24b0000000	LEAQ 0xb0(SP), CX										
  relation_results.go:126	0x8ef89f		4c8b7c2420		MOVQ 0x20(SP), R15										
  relation_results.go:126	0x8ef8a4		b801000000		MOVL $0x1, AX											
  relation_results.go:126	0x8ef8a9		eb15			JMP 0x8ef8c0											
  relation_results.go:126	0x8ef8ab		31c0			XORL AX, AX											
  relation_results.go:126	0x8ef8ad		eb11			JMP 0x8ef8c0											
  relation_results.go:126	0x8ef8af		49c7c7ffffffff		MOVQ $-0x1, R15											
  relation_results.go:126	0x8ef8b6		31c0			XORL AX, AX											
  relation_results.go:126	0x8ef8b8		0f1f840000000000	NOPL 0(AX)(AX*1)										
  relation_results.go:127	0x8ef8c0		4d85ff			TESTQ R15, R15											
  relation_results.go:127	0x8ef8c3		0f8c9f000000		JL 0x8ef968											
  relation_results.go:131	0x8ef8c9		488b7b20		MOVQ 0x20(BX), DI										
  relation_results.go:131	0x8ef8cd		4939f8			CMPQ R8, DI											
  relation_results.go:131	0x8ef8d0		0f8354020000		JAE 0x8efb2a											
  relation_results.go:131	0x8ef8d6		488b7b18		MOVQ 0x18(BX), DI										
  relation_results.go:131	0x8ef8da		428b3c87		MOVL 0(DI)(R8*4), DI										
  relation_results.go:131	0x8ef8de		6690			NOPW												
  relation_results.go:126	0x8ef8e0		84c0			TESTL AL, AL											
  relation_results.go:63	0x8ef8e2		7405			JE 0x8ef8e9											
  relation_results.go:68	0x8ef8e4		4d89fa			MOVQ R15, R10											
  relation_results.go:63	0x8ef8e7		eb5d			JMP 0x8ef946											
  relation_results.go:64	0x8ef8e9		4c8b9c24b8000000	MOVQ 0xb8(SP), R11										
  relation_results.go:64	0x8ef8f1		4d39df			CMPQ R15, R11											
  relation_results.go:64	0x8ef8f4		0f832b020000		JAE 0x8efb25											
  relation_results.go:64	0x8ef8fa		4c8b9c24b0000000	MOVQ 0xb0(SP), R11										
  relation_results.go:64	0x8ef902		4d89fc			MOVQ R15, R12											
  relation_results.go:64	0x8ef905		49c1e704		SHLQ $0x4, R15											
  relation_results.go:64	0x8ef909		4f89143b		MOVQ R10, 0(R11)(R15*1)										
  relation_results.go:64	0x8ef90d		4f894c3b08		MOVQ R9, 0x8(R11)(R15*1)									
  relation_results.go:65	0x8ef912		4c8b8c24e8000000	MOVQ 0xe8(SP), R9										
  relation_results.go:65	0x8ef91a		4d89e2			MOVQ R12, R10											
  relation_results.go:65	0x8ef91d		49c1ec06		SHRQ $0x6, R12											
  relation_results.go:65	0x8ef921		4d39e1			CMPQ R9, R12											
  relation_results.go:65	0x8ef924		0f86f3010000		JBE 0x8efb1d											
  relation_results.go:65	0x8ef92a		4c8b8c24e0000000	MOVQ 0xe0(SP), R9										
  relation_results.go:65	0x8ef932		4f8b1ce1		MOVQ 0(R9)(R12*8), R11										
  relation_results.go:65	0x8ef936		4d0fabd3		BTSQ R10, R11											
  relation_results.go:65	0x8ef93a		4f891ce1		MOVQ R11, 0(R9)(R12*8)										
  relation_results.go:66	0x8ef93e		48ff8424f8000000	INCQ 0xf8(SP)											
  relation_results.go:68	0x8ef946		4c8b8c24d0000000	MOVQ 0xd0(SP), R9										
  relation_results.go:68	0x8ef94e		4d39ca			CMPQ R10, R9											
  relation_results.go:68	0x8ef951		0f83c1010000		JAE 0x8efb18											
  relation_results.go:68	0x8ef957		4c8b8c24c8000000	MOVQ 0xc8(SP), R9										
  relation_results.go:68	0x8ef95f		43893c91		MOVL DI, 0(R9)(R10*4)										
  relation_results.go:131	0x8ef963		e96afaffff		JMP 0x8ef3d2											
  relation_results.go:144	0x8ef968		488b5b48		MOVQ 0x48(BX), BX										
  relation_results.go:144	0x8ef96c		48ffc3			INCQ BX												
  relation_results.go:128	0x8ef96f		90			NOPL												
  relation_results.go:144	0x8ef970		488d0589964d00		LEAQ 0x4d9689(IP), AX										
  relation_results.go:144	0x8ef977		31c9			XORL CX, CX											
  relation_results.go:144	0x8ef979		e88283b9ff		CALL runtime.makemap(SB)									
  relation_results.go:144	0x8ef97e		4889842410010000	MOVQ AX, 0x110(SP)										
  relation_results.go:145	0x8ef986		488b942438010000	MOVQ 0x138(SP), DX										
  relation_results.go:145	0x8ef98e		488b32			MOVQ 0(DX), SI											
  relation_results.go:145	0x8ef991		488b7a08		MOVQ 0x8(DX), DI										
  relation_results.go:145	0x8ef995		48897c2440		MOVQ DI, 0x40(SP)										
  relation_results.go:145	0x8ef99a		31c9			XORL CX, CX											
  relation_results.go:145	0x8ef99c		eb08			JMP 0x8ef9a6											
  relation_results.go:145	0x8ef99e		4883c610		ADDQ $0x10, SI											
  relation_results.go:145	0x8ef9a2		498d4901		LEAQ 0x1(R9), CX										
  relation_results.go:145	0x8ef9a6		4839f9			CMPQ CX, DI											
  relation_results.go:145	0x8ef9a9		0f8da3000000		JGE 0x8efa52											
  relation_results.go:39	0x8ef9af		4c8b4238		MOVQ 0x38(DX), R8										
  relation_results.go:39	0x8ef9b3		4989c9			MOVQ CX, R9											
  relation_results.go:39	0x8ef9b6		48c1e906		SHRQ $0x6, CX											
  relation_results.go:39	0x8ef9ba		660f1f440000		NOPW 0(AX)(AX*1)										
  relation_results.go:39	0x8ef9c0		4939c8			CMPQ R8, CX											
  relation_results.go:39	0x8ef9c3		0f864a010000		JBE 0x8efb13											
  relation_results.go:39	0x8ef9c9		4c8b4230		MOVQ 0x30(DX), R8										
  relation_results.go:39	0x8ef9cd		4d8b04c8		MOVQ 0(R8)(CX*8), R8										
  relation_results.go:39	0x8ef9d1		4d0fa3c8		BTQ R9, R8											
  relation_results.go:146	0x8ef9d5		73c7			JAE 0x8ef99e											
  relation_results.go:145	0x8ef9d7		4c8b06			MOVQ 0(SI), R8											
  relation_results.go:145	0x8ef9da		4c8b5608		MOVQ 0x8(SI), R10										
  relation_results.go:147	0x8ef9de		4c89442428		MOVQ R8, 0x28(SP)										
  relation_results.go:147	0x8ef9e3		4c89542430		MOVQ R10, 0x30(SP)										
  relation_results.go:147	0x8ef9e8		4c8b4220		MOVQ 0x20(DX), R8										
  relation_results.go:147	0x8ef9ec		4d39c1			CMPQ R9, R8											
  relation_results.go:147	0x8ef9ef		0f8319010000		JAE 0x8efb0e											
  relation_results.go:145	0x8ef9f5		4c894c2438		MOVQ R9, 0x38(SP)										
  relation_results.go:145	0x8ef9fa		4889b42420010000	MOVQ SI, 0x120(SP)										
  relation_results.go:147	0x8efa02		488b5218		MOVQ 0x18(DX), DX										
  relation_results.go:147	0x8efa06		428b148a		MOVL 0(DX)(R9*4), DX										
  relation_results.go:147	0x8efa0a		8954241c		MOVL DX, 0x1c(SP)										
  relation_results.go:147	0x8efa0e		4889c3			MOVQ AX, BX											
  relation_results.go:147	0x8efa11		488d4c2428		LEAQ 0x28(SP), CX										
  relation_results.go:147	0x8efa16		488d05e3954d00		LEAQ 0x4d95e3(IP), AX										
  relation_results.go:147	0x8efa1d		0f1f00			NOPL 0(AX)											
  relation_results.go:147	0x8efa20		e8bb28b2ff		CALL runtime.mapassign(SB)									
  relation_results.go:147	0x8efa25		8b54241c		MOVL 0x1c(SP), DX										
  relation_results.go:147	0x8efa29		8910			MOVL DX, 0(AX)											
  relation_results.go:150	0x8efa2b		488b842410010000	MOVQ 0x110(SP), AX										
  relation_results.go:39	0x8efa33		488b942438010000	MOVQ 0x138(SP), DX										
  relation_results.go:145	0x8efa3b		488bb42420010000	MOVQ 0x120(SP), SI										
  relation_results.go:145	0x8efa43		488b7c2440		MOVQ 0x40(SP), DI										
  relation_results.go:145	0x8efa48		4c8b4c2438		MOVQ 0x38(SP), R9										
  relation_results.go:147	0x8efa4d		e94cffffff		JMP 0x8ef99e											
  relation_results.go:150	0x8efa52		488b542448		MOVQ 0x48(SP), DX										
  relation_results.go:150	0x8efa57		4889542428		MOVQ DX, 0x28(SP)										
  relation_results.go:150	0x8efa5c		488b542450		MOVQ 0x50(SP), DX										
  relation_results.go:150	0x8efa61		4889542430		MOVQ DX, 0x30(SP)										
  relation_results.go:150	0x8efa66		4889c3			MOVQ AX, BX											
  relation_results.go:150	0x8efa69		488d4c2428		LEAQ 0x28(SP), CX										
  relation_results.go:150	0x8efa6e		488d058b954d00		LEAQ 0x4d958b(IP), AX										
  relation_results.go:150	0x8efa75		e86628b2ff		CALL runtime.mapassign(SB)									
  relation_results.go:150	0x8efa7a		8b942458010000		MOVL 0x158(SP), DX										
  relation_results.go:150	0x8efa81		8910			MOVL DX, 0(AX)											
  relation_results.go:151	0x8efa83		488b942410010000	MOVQ 0x110(SP), DX										
  relation_results.go:151	0x8efa8b		4885d2			TESTQ DX, DX											
  relation_results.go:151	0x8efa8e		7405			JE 0x8efa95											
  relation_results.go:151	0x8efa90		488b0a			MOVQ 0(DX), CX											
  relation_results.go:151	0x8efa93		eb02			JMP 0x8efa97											
  relation_results.go:151	0x8efa95		31c9			XORL CX, CX											
  relation_results.go:151	0x8efa97		833d726a600100		CMPL runtime.writeBarrier(SB), $0x0								
  relation_results.go:151	0x8efa9e		6690			NOPW												
  relation_results.go:151	0x8efaa0		7436			JE 0x8efad8											
  relation_results.go:151	0x8efaa2		48894c2440		MOVQ CX, 0x40(SP)										
  relation_results.go:151	0x8efaa7		488b9c2438010000	MOVQ 0x138(SP), BX										
  relation_results.go:151	0x8efaaf		488b4b50		MOVQ 0x50(BX), CX										
  relation_results.go:151	0x8efab3		e8481abaff		CALL runtime.gcWriteBarrier2(SB)								
  relation_results.go:151	0x8efab8		498913			MOVQ DX, 0(R11)											
  relation_results.go:151	0x8efabb		49894b08		MOVQ CX, 0x8(R11)										
  relation_results.go:151	0x8efabf		488d057a295900		LEAQ 0x59297a(IP), AX										
  relation_results.go:151	0x8efac6		e8354cb3ff		CALL runtime.wbZero(SB)										
  relation_results.go:151	0x8efacb		488b4c2440		MOVQ 0x40(SP), CX										
  relation_results.go:151	0x8efad0		488b942410010000	MOVQ 0x110(SP), DX										
  relation_results.go:151	0x8efad8		488b842438010000	MOVQ 0x138(SP), AX										
  relation_results.go:151	0x8efae0		440f1138		MOVUPS X15, 0(AX)										
  relation_results.go:151	0x8efae4		440f117810		MOVUPS X15, 0x10(AX)										
  relation_results.go:151	0x8efae9		440f117820		MOVUPS X15, 0x20(AX)										
  relation_results.go:151	0x8efaee		440f117830		MOVUPS X15, 0x30(AX)										
  relation_results.go:151	0x8efaf3		440f117840		MOVUPS X15, 0x40(AX)										
  relation_results.go:151	0x8efaf8		440f117848		MOVUPS X15, 0x48(AX)										
  relation_results.go:151	0x8efafd		48895050		MOVQ DX, 0x50(AX)										
  relation_results.go:151	0x8efb01		48894848		MOVQ CX, 0x48(AX)										
  relation_results.go:129	0x8efb05		4881c428010000		ADDQ $0x128, SP											
  relation_results.go:129	0x8efb0c		5d			POPQ BP												
  relation_results.go:129	0x8efb0d		c3			RET												
  relation_results.go:147	0x8efb0e		e88d1dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8efb13		e8881dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:68	0x8efb18		e8831dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:65	0x8efb1d		0f1f00			NOPL 0(AX)											
  relation_results.go:65	0x8efb20		e87b1dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:64	0x8efb25		e8761dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:131	0x8efb2a		e8711dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:54	0x8efb2f		e86c1dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8efb34		e8671dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8efb39		e8621dbaff		CALL runtime.panicBounds(SB)									
  relation_results.go:39	0x8efb3e		90			NOPL												
  relation_results.go:122	0x8efb3f		4889442408		MOVQ AX, 0x8(SP)										
  relation_results.go:122	0x8efb44		48895c2410		MOVQ BX, 0x10(SP)										
  relation_results.go:122	0x8efb49		48894c2418		MOVQ CX, 0x18(SP)										
  relation_results.go:122	0x8efb4e		48897c2420		MOVQ DI, 0x20(SP)										
  relation_results.go:122	0x8efb53		89742428		MOVL SI, 0x28(SP)										
  relation_results.go:122	0x8efb57		e8a4feb9ff		CALL runtime.morestack_noctxt.abi0(SB)								
  relation_results.go:122	0x8efb5c		488b442408		MOVQ 0x8(SP), AX										
  relation_results.go:122	0x8efb61		488b5c2410		MOVQ 0x10(SP), BX										
  relation_results.go:122	0x8efb66		488b4c2418		MOVQ 0x18(SP), CX										
  relation_results.go:122	0x8efb6b		488b7c2420		MOVQ 0x20(SP), DI										
  relation_results.go:122	0x8efb70		8b742428		MOVL 0x28(SP), SI										
  relation_results.go:122	0x8efb74		e9e7f6ffff		JMP github.com/microsoft/typescript-go/internal/checker.(*relationResultCache).rebuild(SB)	
