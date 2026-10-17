TEXT github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB) github.com/microsoft/typescript-go/internal/core/pointerlinkstore.go
  pointerlinkstore.go:93	0x903e20		493b6610		CMPQ SP, 0x10(R14)																												
  pointerlinkstore.go:93	0x903e24		764f			JBE 0x903e75																													
  pointerlinkstore.go:93	0x903e26		55			PUSHQ BP																													
  pointerlinkstore.go:93	0x903e27		4889e5			MOVQ SP, BP																													
  pointerlinkstore.go:93	0x903e2a		4883ec20		SUBQ $0x20, SP																													
  pointerlinkstore.go:95	0x903e2e		4883780800		CMPQ 0x8(AX), $0x0																												
  pointerlinkstore.go:95	0x903e33		7504			JNE 0x903e39																													
  pointerlinkstore.go:95	0x903e35		31d2			XORL DX, DX																													
  pointerlinkstore.go:95	0x903e37		eb2a			JMP 0x903e63																													
  pointerlinkstore.go:95	0x903e39		4889442430		MOVQ AX, 0x30(SP)																												
  pointerlinkstore.go:95	0x903e3e		48895c2438		MOVQ BX, 0x38(SP)																												
  pointerlinkstore.go:95	0x903e43		48894c2440		MOVQ CX, 0x40(SP)																												
  pointerlinkstore.go:96	0x903e48		488b5b28		MOVQ 0x28(BX), BX																												
  pointerlinkstore.go:96	0x903e4c		e86f040000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)		
  pointerlinkstore.go:98	0x903e51		488b4c2440		MOVQ 0x40(SP), CX																												
  pointerlinkstore.go:98	0x903e56		488b5c2438		MOVQ 0x38(SP), BX																												
  pointerlinkstore.go:98	0x903e5b		4889c2			MOVQ AX, DX																													
  pointerlinkstore.go:98	0x903e5e		488b442430		MOVQ 0x30(SP), AX																												
  pointerlinkstore.go:98	0x903e63		488b5b28		MOVQ 0x28(BX), BX																												
  pointerlinkstore.go:98	0x903e67		4889d7			MOVQ DX, DI																													
  pointerlinkstore.go:98	0x903e6a		e8f1000000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).insertAt(SB)	
  pointerlinkstore.go:98	0x903e6f		4883c420		ADDQ $0x20, SP																													
  pointerlinkstore.go:98	0x903e73		5d			POPQ BP																														
  pointerlinkstore.go:98	0x903e74		c3			RET																														
  pointerlinkstore.go:93	0x903e75		4889442408		MOVQ AX, 0x8(SP)																												
  pointerlinkstore.go:93	0x903e7a		48895c2410		MOVQ BX, 0x10(SP)																												
  pointerlinkstore.go:93	0x903e7f		48894c2418		MOVQ CX, 0x18(SP)																												
  pointerlinkstore.go:93	0x903e84		e877bbb8ff		CALL runtime.morestack_noctxt.abi0(SB)																										
  pointerlinkstore.go:93	0x903e89		488b442408		MOVQ 0x8(SP), AX																												
  pointerlinkstore.go:93	0x903e8e		488b5c2410		MOVQ 0x10(SP), BX																												
  pointerlinkstore.go:93	0x903e93		488b4c2418		MOVQ 0x18(SP), CX																												
  pointerlinkstore.go:93	0x903e98		eb86			JMP github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB)		

TEXT github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB) github.com/microsoft/typescript-go/internal/core/pointerlinkstore.go
  pointerlinkstore.go:80	0x903ea0		493b6610		CMPQ SP, 0x10(R14)																												
  pointerlinkstore.go:80	0x903ea4		0f867c000000		JBE 0x903f26																													
  pointerlinkstore.go:80	0x903eaa		55			PUSHQ BP																													
  pointerlinkstore.go:80	0x903eab		4889e5			MOVQ SP, BP																													
  pointerlinkstore.go:80	0x903eae		4883ec20		SUBQ $0x20, SP																													
  pointerlinkstore.go:82	0x903eb2		4883780800		CMPQ 0x8(AX), $0x0																												
  pointerlinkstore.go:82	0x903eb7		7505			JNE 0x903ebe																													
  pointerlinkstore.go:82	0x903eb9		4531c0			XORL R8, R8																													
  pointerlinkstore.go:82	0x903ebc		eb48			JMP 0x903f06																													
  pointerlinkstore.go:82	0x903ebe		4889442430		MOVQ AX, 0x30(SP)																												
  pointerlinkstore.go:82	0x903ec3		48895c2438		MOVQ BX, 0x38(SP)																												
  pointerlinkstore.go:82	0x903ec8		48894c2440		MOVQ CX, 0x40(SP)																												
  pointerlinkstore.go:83	0x903ecd		488b5b20		MOVQ 0x20(BX), BX																												
  pointerlinkstore.go:83	0x903ed1		e8ea030000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)		
  pointerlinkstore.go:84	0x903ed6		488b542430		MOVQ 0x30(SP), DX																												
  pointerlinkstore.go:84	0x903edb		488b7208		MOVQ 0x8(DX), SI																												
  pointerlinkstore.go:84	0x903edf		90			NOPL																														
  pointerlinkstore.go:84	0x903ee0		4839f0			CMPQ AX, SI																													
  pointerlinkstore.go:84	0x903ee3		7339			JAE 0x903f1e																													
  pointerlinkstore.go:84	0x903ee5		488b32			MOVQ 0(DX), SI																													
  pointerlinkstore.go:84	0x903ee8		4989c0			MOVQ AX, R8																													
  pointerlinkstore.go:84	0x903eeb		48c1e004		SHLQ $0x4, AX																													
  pointerlinkstore.go:84	0x903eef		488b440608		MOVQ 0x8(SI)(AX*1), AX																												
  pointerlinkstore.go:84	0x903ef4		4885c0			TESTQ AX, AX																													
  pointerlinkstore.go:84	0x903ef7		751f			JNE 0x903f18																													
  pointerlinkstore.go:88	0x903ef9		4889d0			MOVQ DX, AX																													
  pointerlinkstore.go:88	0x903efc		488b4c2440		MOVQ 0x40(SP), CX																												
  pointerlinkstore.go:88	0x903f01		488b5c2438		MOVQ 0x38(SP), BX																												
  pointerlinkstore.go:88	0x903f06		488b5b20		MOVQ 0x20(BX), BX																												
  pointerlinkstore.go:88	0x903f0a		4c89c7			MOVQ R8, DI																													
  pointerlinkstore.go:88	0x903f0d		e84e000000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).insertAt(SB)	
  pointerlinkstore.go:88	0x903f12		4883c420		ADDQ $0x20, SP																													
  pointerlinkstore.go:88	0x903f16		5d			POPQ BP																														
  pointerlinkstore.go:88	0x903f17		c3			RET																														
  pointerlinkstore.go:85	0x903f18		4883c420		ADDQ $0x20, SP																													
  pointerlinkstore.go:85	0x903f1c		5d			POPQ BP																														
  pointerlinkstore.go:85	0x903f1d		c3			RET																														
  pointerlinkstore.go:84	0x903f1e		6690			NOPW																														
  pointerlinkstore.go:84	0x903f20		e87bd9b8ff		CALL runtime.panicBounds(SB)																											
  pointerlinkstore.go:84	0x903f25		90			NOPL																														
  pointerlinkstore.go:80	0x903f26		4889442408		MOVQ AX, 0x8(SP)																												
  pointerlinkstore.go:80	0x903f2b		48895c2410		MOVQ BX, 0x10(SP)																												
  pointerlinkstore.go:80	0x903f30		48894c2418		MOVQ CX, 0x18(SP)																												
  pointerlinkstore.go:80	0x903f35		e8c6bab8ff		CALL runtime.morestack_noctxt.abi0(SB)																										
  pointerlinkstore.go:80	0x903f3a		488b442408		MOVQ 0x8(SP), AX																												
  pointerlinkstore.go:80	0x903f3f		488b5c2410		MOVQ 0x10(SP), BX																												
  pointerlinkstore.go:80	0x903f44		488b4c2418		MOVQ 0x18(SP), CX																												
  pointerlinkstore.go:80	0x903f49		e952ffffff		JMP github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)		

TEXT github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).insertAt(SB) github.com/microsoft/typescript-go/internal/core/pointerlinkstore.go
  pointerlinkstore.go:64	0x903f60		493b6610		CMPQ SP, 0x10(R14)																												
  pointerlinkstore.go:64	0x903f64		0f8650010000		JBE 0x9040ba																													
  pointerlinkstore.go:64	0x903f6a		55			PUSHQ BP																													
  pointerlinkstore.go:64	0x903f6b		4889e5			MOVQ SP, BP																													
  pointerlinkstore.go:64	0x903f6e		4883ec20		SUBQ $0x20, SP																													
  pointerlinkstore.go:65	0x903f72		4889442430		MOVQ AX, 0x30(SP)																												
  pointerlinkstore.go:65	0x903f77		48895c2438		MOVQ BX, 0x38(SP)																												
  pointerlinkstore.go:65	0x903f7c		48894c2440		MOVQ CX, 0x40(SP)																												
  pointerlinkstore.go:65	0x903f81		488b5008		MOVQ 0x8(AX), DX																												
  pointerlinkstore.go:65	0x903f85		4885d2			TESTQ DX, DX																													
  pointerlinkstore.go:65	0x903f88		7468			JE 0x903ff2																													
  pointerlinkstore.go:68	0x903f8a		4839d7			CMPQ DI, DX																													
  pointerlinkstore.go:68	0x903f8d		0f8321010000		JAE 0x9040b4																													
  pointerlinkstore.go:65	0x903f93		488b30			MOVQ 0(AX), SI																													
  pointerlinkstore.go:68	0x903f96		4989f8			MOVQ DI, R8																													
  pointerlinkstore.go:68	0x903f99		48c1e704		SHLQ $0x4, DI																													
  pointerlinkstore.go:68	0x903f9d		488b743708		MOVQ 0x8(DI)(SI*1), SI																												
  pointerlinkstore.go:68	0x903fa2		4885f6			TESTQ SI, SI																													
  pointerlinkstore.go:68	0x903fa5		7579			JNE 0x904020																													
  pointerlinkstore.go:68	0x903fa7		488b7018		MOVQ 0x18(AX), SI																												
  pointerlinkstore.go:68	0x903fab		48ffc6			INCQ SI																														
  pointerlinkstore.go:68	0x903fae		4889d7			MOVQ DX, DI																													
  pointerlinkstore.go:68	0x903fb1		48c1ea02		SHRQ $0x2, DX																													
  pointerlinkstore.go:68	0x903fb5		4829d7			SUBQ DX, DI																													
  pointerlinkstore.go:68	0x903fb8		4839f7			CMPQ DI, SI																													
  pointerlinkstore.go:68	0x903fbb		7d63			JGE 0x904020																													
  pointerlinkstore.go:69	0x903fbd		488b5b10		MOVQ 0x10(BX), BX																												
  pointerlinkstore.go:69	0x903fc1		e83a010000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).grow(SB)		
  pointerlinkstore.go:70	0x903fc6		488b4c2438		MOVQ 0x38(SP), CX																												
  pointerlinkstore.go:70	0x903fcb		488b5910		MOVQ 0x10(CX), BX																												
  pointerlinkstore.go:70	0x903fcf		488b442430		MOVQ 0x30(SP), AX																												
  pointerlinkstore.go:70	0x903fd4		488b4c2440		MOVQ 0x40(SP), CX																												
  pointerlinkstore.go:70	0x903fd9		e8e2020000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)		
  pointerlinkstore.go:76	0x903fde		488b4c2440		MOVQ 0x40(SP), CX																												
  pointerlinkstore.go:72	0x903fe3		488b5c2438		MOVQ 0x38(SP), BX																												
  pointerlinkstore.go:72	0x903fe8		4989c0			MOVQ AX, R8																													
  pointerlinkstore.go:72	0x903feb		488b442430		MOVQ 0x30(SP), AX																												
  pointerlinkstore.go:70	0x903ff0		eb2e			JMP 0x904020																													
  pointerlinkstore.go:66	0x903ff2		488b5b10		MOVQ 0x10(BX), BX																												
  pointerlinkstore.go:66	0x903ff6		e805010000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).grow(SB)		
  pointerlinkstore.go:67	0x903ffb		488b4c2438		MOVQ 0x38(SP), CX																												
  pointerlinkstore.go:67	0x904000		488b5910		MOVQ 0x10(CX), BX																												
  pointerlinkstore.go:67	0x904004		488b442430		MOVQ 0x30(SP), AX																												
  pointerlinkstore.go:67	0x904009		488b4c2440		MOVQ 0x40(SP), CX																												
  pointerlinkstore.go:67	0x90400e		e8ad020000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)		
  pointerlinkstore.go:72	0x904013		488b5c2438		MOVQ 0x38(SP), BX																												
  pointerlinkstore.go:72	0x904018		4989c0			MOVQ AX, R8																													
  pointerlinkstore.go:72	0x90401b		488b442430		MOVQ 0x30(SP), AX																												
  pointerlinkstore.go:72	0x904020		4c89442418		MOVQ R8, 0x18(SP)																												
  pointerlinkstore.go:72	0x904025		4883c020		ADDQ $0x20, AX																													
  pointerlinkstore.go:72	0x904029		488b5b18		MOVQ 0x18(BX), BX																												
  pointerlinkstore.go:72	0x90402d		e86e030000		CALL github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB)												
  pointerlinkstore.go:73	0x904032		488b4c2430		MOVQ 0x30(SP), CX																												
  pointerlinkstore.go:73	0x904037		488b5108		MOVQ 0x8(CX), DX																												
  pointerlinkstore.go:73	0x90403b		488b742418		MOVQ 0x18(SP), SI																												
  pointerlinkstore.go:73	0x904040		4839d6			CMPQ SI, DX																													
  pointerlinkstore.go:73	0x904043		736a			JAE 0x9040af																													
  pointerlinkstore.go:73	0x904045		488b11			MOVQ 0(CX), DX																													
  pointerlinkstore.go:73	0x904048		4889f3			MOVQ SI, BX																													
  pointerlinkstore.go:73	0x90404b		48c1e604		SHLQ $0x4, SI																													
  pointerlinkstore.go:73	0x90404f		488b541608		MOVQ 0x8(SI)(DX*1), DX																												
  pointerlinkstore.go:73	0x904054		4885d2			TESTQ DX, DX																													
  pointerlinkstore.go:73	0x904057		7504			JNE 0x90405d																													
  pointerlinkstore.go:74	0x904059		48ff4118		INCQ 0x18(CX)																													
  pointerlinkstore.go:76	0x90405d		488b5108		MOVQ 0x8(CX), DX																												
  pointerlinkstore.go:76	0x904061		4839d3			CMPQ BX, DX																													
  pointerlinkstore.go:76	0x904064		7344			JAE 0x9040aa																													
  pointerlinkstore.go:76	0x904066		488b09			MOVQ 0(CX), CX																													
  pointerlinkstore.go:76	0x904069		833da0045f0100		CMPL runtime.writeBarrier(SB), $0x0																										
  pointerlinkstore.go:76	0x904070		7507			JNE 0x904079																													
  pointerlinkstore.go:76	0x904072		488b7c2440		MOVQ 0x40(SP), DI																												
  pointerlinkstore.go:76	0x904077		eb22			JMP 0x90409b																													
  pointerlinkstore.go:76	0x904079		488b1431		MOVQ 0(CX)(SI*1), DX																												
  pointerlinkstore.go:76	0x90407d		488b5c3108		MOVQ 0x8(CX)(SI*1), BX																												
  pointerlinkstore.go:76	0x904082		e8b9d4b8ff		CALL runtime.gcWriteBarrier4(SB)																										
  pointerlinkstore.go:76	0x904087		488b7c2440		MOVQ 0x40(SP), DI																												
  pointerlinkstore.go:76	0x90408c		49893b			MOVQ DI, 0(R11)																													
  pointerlinkstore.go:76	0x90408f		49895308		MOVQ DX, 0x8(R11)																												
  pointerlinkstore.go:76	0x904093		49894310		MOVQ AX, 0x10(R11)																												
  pointerlinkstore.go:76	0x904097		49895b18		MOVQ BX, 0x18(R11)																												
  pointerlinkstore.go:76	0x90409b		48893c31		MOVQ DI, 0(CX)(SI*1)																												
  pointerlinkstore.go:76	0x90409f		4889443108		MOVQ AX, 0x8(CX)(SI*1)																												
  pointerlinkstore.go:77	0x9040a4		4883c420		ADDQ $0x20, SP																													
  pointerlinkstore.go:77	0x9040a8		5d			POPQ BP																														
  pointerlinkstore.go:77	0x9040a9		c3			RET																														
  pointerlinkstore.go:76	0x9040aa		e8f1d7b8ff		CALL runtime.panicBounds(SB)																											
  pointerlinkstore.go:73	0x9040af		e8ecd7b8ff		CALL runtime.panicBounds(SB)																											
  pointerlinkstore.go:68	0x9040b4		e8e7d7b8ff		CALL runtime.panicBounds(SB)																											
  pointerlinkstore.go:68	0x9040b9		90			NOPL																														
  pointerlinkstore.go:64	0x9040ba		4889442408		MOVQ AX, 0x8(SP)																												
  pointerlinkstore.go:64	0x9040bf		48895c2410		MOVQ BX, 0x10(SP)																												
  pointerlinkstore.go:64	0x9040c4		48894c2418		MOVQ CX, 0x18(SP)																												
  pointerlinkstore.go:64	0x9040c9		48897c2420		MOVQ DI, 0x20(SP)																												
  pointerlinkstore.go:64	0x9040ce		e82db9b8ff		CALL runtime.morestack_noctxt.abi0(SB)																										
  pointerlinkstore.go:64	0x9040d3		488b442408		MOVQ 0x8(SP), AX																												
  pointerlinkstore.go:64	0x9040d8		488b5c2410		MOVQ 0x10(SP), BX																												
  pointerlinkstore.go:64	0x9040dd		488b4c2418		MOVQ 0x18(SP), CX																												
  pointerlinkstore.go:64	0x9040e2		488b7c2420		MOVQ 0x20(SP), DI																												
  pointerlinkstore.go:64	0x9040e7		e974feffff		JMP github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).insertAt(SB)	

TEXT github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).grow(SB) github.com/microsoft/typescript-go/internal/core/pointerlinkstore.go
  pointerlinkstore.go:44	0x904100		4c8d6424f8		LEAQ -0x8(SP), R12																											
  pointerlinkstore.go:44	0x904105		4d3b6610		CMPQ R12, 0x10(R14)																											
  pointerlinkstore.go:44	0x904109		0f868c010000		JBE 0x90429b																												
  pointerlinkstore.go:44	0x90410f		55			PUSHQ BP																												
  pointerlinkstore.go:44	0x904110		4889e5			MOVQ SP, BP																												
  pointerlinkstore.go:44	0x904113		4883c480		ADDQ $-0x80, SP																												
  pointerlinkstore.go:46	0x904117		4889842490000000	MOVQ AX, 0x90(SP)																											
  pointerlinkstore.go:45	0x90411f		488b5008		MOVQ 0x8(AX), DX																											
  pointerlinkstore.go:46	0x904123		4885d2			TESTQ DX, DX																												
  pointerlinkstore.go:46	0x904126		7507			JNE 0x90412f																												
  pointerlinkstore.go:46	0x904128		ba10000000		MOVL $0x10, DX																												
  pointerlinkstore.go:46	0x90412d		eb03			JMP 0x904132																												
  pointerlinkstore.go:52	0x90412f		4801d2			ADDQ DX, DX																												
  pointerlinkstore.go:46	0x904132		48899c2498000000	MOVQ BX, 0x98(SP)																											
  pointerlinkstore.go:55	0x90413a		4889542418		MOVQ DX, 0x18(SP)																											
  pointerlinkstore.go:55	0x90413f		488b4370		MOVQ 0x70(BX), AX																											
  pointerlinkstore.go:55	0x904143		4889d3			MOVQ DX, BX																												
  pointerlinkstore.go:55	0x904146		4889d9			MOVQ BX, CX																												
  pointerlinkstore.go:55	0x904149		e8327fb8ff		CALL runtime.makeslice(SB)																										
  pointerlinkstore.go:55	0x90414e		488d542430		LEAQ 0x30(SP), DX																											
  pointerlinkstore.go:55	0x904153		440f113a		MOVUPS X15, 0(DX)																											
  pointerlinkstore.go:55	0x904157		440f117a10		MOVUPS X15, 0x10(DX)																											
  pointerlinkstore.go:55	0x90415c		440f117a20		MOVUPS X15, 0x20(DX)																											
  pointerlinkstore.go:55	0x904161		440f117a28		MOVUPS X15, 0x28(DX)																											
  pointerlinkstore.go:55	0x904166		4889442430		MOVQ AX, 0x30(SP)																											
  pointerlinkstore.go:55	0x90416b		488b742418		MOVQ 0x18(SP), SI																											
  pointerlinkstore.go:55	0x904170		4889742438		MOVQ SI, 0x38(SP)																											
  pointerlinkstore.go:55	0x904175		4889742440		MOVQ SI, 0x40(SP)																											
  pointerlinkstore.go:56	0x90417a		488bb42490000000	MOVQ 0x90(SP), SI																											
  pointerlinkstore.go:56	0x904182		488b3e			MOVQ 0(SI), DI																												
  pointerlinkstore.go:56	0x904185		4c8b4608		MOVQ 0x8(SI), R8																											
  pointerlinkstore.go:56	0x904189		4c89442428		MOVQ R8, 0x28(SP)																											
  pointerlinkstore.go:56	0x90418e		31c0			XORL AX, AX																												
  pointerlinkstore.go:56	0x904190		eb0e			JMP 0x9041a0																												
  pointerlinkstore.go:56	0x904192		4883c710		ADDQ $0x10, DI																												
  pointerlinkstore.go:56	0x904196		48ffc0			INCQ AX																													
  pointerlinkstore.go:56	0x904199		0f1f8000000000		NOPL 0(AX)																												
  pointerlinkstore.go:56	0x9041a0		4c39c0			CMPQ AX, R8																												
  pointerlinkstore.go:56	0x9041a3		0f8db1000000		JGE 0x90425a																												
  pointerlinkstore.go:56	0x9041a9		4c8b4f08		MOVQ 0x8(DI), R9																											
  pointerlinkstore.go:57	0x9041ad		4d85c9			TESTQ R9, R9																												
  pointerlinkstore.go:57	0x9041b0		74e0			JE 0x904192																												
  pointerlinkstore.go:56	0x9041b2		4889442420		MOVQ AX, 0x20(SP)																											
  pointerlinkstore.go:56	0x9041b7		48897c2478		MOVQ DI, 0x78(SP)																											
  pointerlinkstore.go:56	0x9041bc		4c894c2470		MOVQ R9, 0x70(SP)																											
  pointerlinkstore.go:56	0x9041c1		488b0f			MOVQ 0(DI), CX																												
  pointerlinkstore.go:56	0x9041c4		48894c2468		MOVQ CX, 0x68(SP)																											
  pointerlinkstore.go:58	0x9041c9		488bb42498000000	MOVQ 0x98(SP), SI																											
  pointerlinkstore.go:58	0x9041d1		488b5e08		MOVQ 0x8(SI), BX																											
  pointerlinkstore.go:58	0x9041d5		4889d0			MOVQ DX, AX																												
  pointerlinkstore.go:58	0x9041d8		e8e3000000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)	
  pointerlinkstore.go:58	0x9041dd		488b542438		MOVQ 0x38(SP), DX																											
  pointerlinkstore.go:58	0x9041e2		4839d0			CMPQ AX, DX																												
  pointerlinkstore.go:58	0x9041e5		0f83aa000000		JAE 0x904295																												
  pointerlinkstore.go:58	0x9041eb		488b542430		MOVQ 0x30(SP), DX																											
  pointerlinkstore.go:58	0x9041f0		48c1e004		SHLQ $0x4, AX																												
  pointerlinkstore.go:58	0x9041f4		833d15035f0100		CMPL runtime.writeBarrier(SB), $0x0																									
  pointerlinkstore.go:58	0x9041fb		750c			JNE 0x904209																												
  pointerlinkstore.go:58	0x9041fd		488b742470		MOVQ 0x70(SP), SI																											
  pointerlinkstore.go:58	0x904202		4c8b442468		MOVQ 0x68(SP), R8																											
  pointerlinkstore.go:58	0x904207		eb27			JMP 0x904230																												
  pointerlinkstore.go:58	0x904209		488b3402		MOVQ 0(DX)(AX*1), SI																											
  pointerlinkstore.go:58	0x90420d		488b7c0208		MOVQ 0x8(DX)(AX*1), DI																											
  pointerlinkstore.go:58	0x904212		e829d3b8ff		CALL runtime.gcWriteBarrier4(SB)																									
  pointerlinkstore.go:58	0x904217		4c8b442468		MOVQ 0x68(SP), R8																											
  pointerlinkstore.go:58	0x90421c		4d8903			MOVQ R8, 0(R11)																												
  pointerlinkstore.go:58	0x90421f		49897308		MOVQ SI, 0x8(R11)																											
  pointerlinkstore.go:58	0x904223		488b742470		MOVQ 0x70(SP), SI																											
  pointerlinkstore.go:58	0x904228		49897310		MOVQ SI, 0x10(R11)																											
  pointerlinkstore.go:58	0x90422c		49897b18		MOVQ DI, 0x18(R11)																											
  pointerlinkstore.go:58	0x904230		4c890402		MOVQ R8, 0(DX)(AX*1)																											
  pointerlinkstore.go:58	0x904234		4889740208		MOVQ SI, 0x8(DX)(AX*1)																											
  pointerlinkstore.go:56	0x904239		488b442420		MOVQ 0x20(SP), AX																											
  pointerlinkstore.go:55	0x90423e		488d542430		LEAQ 0x30(SP), DX																											
  pointerlinkstore.go:61	0x904243		488bb42490000000	MOVQ 0x90(SP), SI																											
  pointerlinkstore.go:56	0x90424b		488b7c2478		MOVQ 0x78(SP), DI																											
  pointerlinkstore.go:56	0x904250		4c8b442428		MOVQ 0x28(SP), R8																											
  pointerlinkstore.go:58	0x904255		e938ffffff		JMP 0x904192																												
  pointerlinkstore.go:61	0x90425a		488b442438		MOVQ 0x38(SP), AX																											
  pointerlinkstore.go:61	0x90425f		488b4c2440		MOVQ 0x40(SP), CX																											
  pointerlinkstore.go:61	0x904264		488b542430		MOVQ 0x30(SP), DX																											
  pointerlinkstore.go:61	0x904269		48894608		MOVQ AX, 0x8(SI)																											
  pointerlinkstore.go:61	0x90426d		48894e10		MOVQ CX, 0x10(SI)																											
  pointerlinkstore.go:61	0x904271		833d98025f0100		CMPL runtime.writeBarrier(SB), $0x0																									
  pointerlinkstore.go:61	0x904278		7412			JE 0x90428c																												
  pointerlinkstore.go:61	0x90427a		488b06			MOVQ 0(SI), AX																												
  pointerlinkstore.go:61	0x90427d		0f1f00			NOPL 0(AX)																												
  pointerlinkstore.go:61	0x904280		e87bd2b8ff		CALL runtime.gcWriteBarrier2(SB)																									
  pointerlinkstore.go:61	0x904285		498913			MOVQ DX, 0(R11)																												
  pointerlinkstore.go:61	0x904288		49894308		MOVQ AX, 0x8(R11)																											
  pointerlinkstore.go:61	0x90428c		488916			MOVQ DX, 0(SI)																												
  pointerlinkstore.go:62	0x90428f		4883ec80		SUBQ $-0x80, SP																												
  pointerlinkstore.go:62	0x904293		5d			POPQ BP																													
  pointerlinkstore.go:62	0x904294		c3			RET																													
  pointerlinkstore.go:58	0x904295		e806d6b8ff		CALL runtime.panicBounds(SB)																										
  pointerlinkstore.go:58	0x90429a		90			NOPL																													
  pointerlinkstore.go:44	0x90429b		4889442408		MOVQ AX, 0x8(SP)																											
  pointerlinkstore.go:44	0x9042a0		48895c2410		MOVQ BX, 0x10(SP)																											
  pointerlinkstore.go:44	0x9042a5		e856b7b8ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  pointerlinkstore.go:44	0x9042aa		488b442408		MOVQ 0x8(SP), AX																											
  pointerlinkstore.go:44	0x9042af		488b5c2410		MOVQ 0x10(SP), BX																											
  pointerlinkstore.go:44	0x9042b4		e947feffff		JMP github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).grow(SB)	

TEXT github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB) github.com/microsoft/typescript-go/internal/core/pointerlinkstore.go
  pointerlinkstore.go:31	0x9042c0		493b6610		CMPQ SP, 0x10(R14)																											
  pointerlinkstore.go:31	0x9042c4		0f86a8000000		JBE 0x904372																												
  pointerlinkstore.go:31	0x9042ca		55			PUSHQ BP																												
  pointerlinkstore.go:31	0x9042cb		4889e5			MOVQ SP, BP																												
  pointerlinkstore.go:31	0x9042ce		4883ec10		SUBQ $0x10, SP																												
  pointerlinkstore.go:32	0x9042d2		488b5008		MOVQ 0x8(AX), DX																											
  pointerlinkstore.go:32	0x9042d6		488d72ff		LEAQ -0x1(DX), SI																											
  pointerlinkstore.go:25	0x9042da		4889cf			MOVQ CX, DI																												
  pointerlinkstore.go:26	0x9042dd		4989c8			MOVQ CX, R8																												
  pointerlinkstore.go:26	0x9042e0		48c1e91e		SHRQ $0x1e, CX																												
  pointerlinkstore.go:26	0x9042e4		4c31c1			XORQ R8, CX																												
  pointerlinkstore.go:26	0x9042e7		49b8b9e5e41c6d4758bf	MOVQ $0xbf58476d1ce4e5b9, R8																										
  pointerlinkstore.go:26	0x9042f1		4c0fafc1		IMULQ CX, R8																												
  pointerlinkstore.go:27	0x9042f5		4c89c1			MOVQ R8, CX																												
  pointerlinkstore.go:27	0x9042f8		49c1e81b		SHRQ $0x1b, R8																												
  pointerlinkstore.go:27	0x9042fc		4931c8			XORQ CX, R8																												
  pointerlinkstore.go:27	0x9042ff		48b9eb113113bb49d094	MOVQ $0x94d049bb133111eb, CX																										
  pointerlinkstore.go:27	0x904309		490fafc8		IMULQ R8, CX																												
  pointerlinkstore.go:28	0x90430d		4989c8			MOVQ CX, R8																												
  pointerlinkstore.go:28	0x904310		48c1e91f		SHRQ $0x1f, CX																												
  pointerlinkstore.go:28	0x904314		4c31c1			XORQ R8, CX																												
  pointerlinkstore.go:32	0x904317		4c8b00			MOVQ 0(AX), R8																												
  pointerlinkstore.go:33	0x90431a		4821f1			ANDQ SI, CX																												
  pointerlinkstore.go:33	0x90431d		31c0			XORL AX, AX																												
  pointerlinkstore.go:33	0x90431f		90			NOPL																													
  pointerlinkstore.go:34	0x904320		eb0a			JMP 0x90432c																												
  pointerlinkstore.go:39	0x904322		498d4901		LEAQ 0x1(R9), CX																											
  pointerlinkstore.go:39	0x904326		4821f1			ANDQ SI, CX																												
  pointerlinkstore.go:34	0x904329		48ffc0			INCQ AX																													
  pointerlinkstore.go:34	0x90432c		4839d0			CMPQ AX, DX																												
  pointerlinkstore.go:34	0x90432f		7d2d			JGE 0x90435e																												
  pointerlinkstore.go:35	0x904331		4839d1			CMPQ CX, DX																												
  pointerlinkstore.go:35	0x904334		7323			JAE 0x904359																												
  pointerlinkstore.go:35	0x904336		4989c9			MOVQ CX, R9																												
  pointerlinkstore.go:35	0x904339		48c1e104		SHLQ $0x4, CX																												
  pointerlinkstore.go:36	0x90433d		4d8b540808		MOVQ 0x8(R8)(CX*1), R10																											
  pointerlinkstore.go:36	0x904342		4d85d2			TESTQ R10, R10																												
  pointerlinkstore.go:36	0x904345		7409			JE 0x904350																												
  pointerlinkstore.go:36	0x904347		498b0c08		MOVQ 0(R8)(CX*1), CX																											
  pointerlinkstore.go:36	0x90434b		4839f9			CMPQ CX, DI																												
  pointerlinkstore.go:36	0x90434e		75d2			JNE 0x904322																												
  pointerlinkstore.go:37	0x904350		4c89c8			MOVQ R9, AX																												
  pointerlinkstore.go:37	0x904353		4883c410		ADDQ $0x10, SP																												
  pointerlinkstore.go:37	0x904357		5d			POPQ BP																													
  pointerlinkstore.go:37	0x904358		c3			RET																													
  pointerlinkstore.go:35	0x904359		e842d5b8ff		CALL runtime.panicBounds(SB)																										
  pointerlinkstore.go:41	0x90435e		488d051bb34500		LEAQ 0x45b31b(IP), AX																											
  pointerlinkstore.go:41	0x904365		488d1dd4d8c100		LEAQ 0xc1d8d4(IP), BX																											
  pointerlinkstore.go:41	0x90436c		e82f57b8ff		CALL runtime.gopanic(SB)																										
  pointerlinkstore.go:41	0x904371		90			NOPL																													
  pointerlinkstore.go:31	0x904372		4889442408		MOVQ AX, 0x8(SP)																											
  pointerlinkstore.go:31	0x904377		48895c2410		MOVQ BX, 0x10(SP)																											
  pointerlinkstore.go:31	0x90437c		48894c2418		MOVQ CX, 0x18(SP)																											
  pointerlinkstore.go:31	0x904381		e87ab6b8ff		CALL runtime.morestack_noctxt.abi0(SB)																									
  pointerlinkstore.go:31	0x904386		488b442408		MOVQ 0x8(SP), AX																											
  pointerlinkstore.go:31	0x90438b		488b5c2410		MOVQ 0x10(SP), BX																											
  pointerlinkstore.go:31	0x904390		488b4c2418		MOVQ 0x18(SP), CX																											
  pointerlinkstore.go:31	0x904395		e926ffffff		JMP github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.7ef79b8109ca7a73e057574e4a0af0be1984d8606fab799593577d67d88dffe0,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).slot(SB)	
