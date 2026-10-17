  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:22041	0x824020		4c8da424e8f9ffff	LEAQ 0xfffff9e8(SP), R12															
  checker.go:22041	0x824028		4d3b6610		CMPQ R12, 0x10(R14)																
  checker.go:22041	0x82402c		0f869c080000		JBE 0x8248ce																	
  checker.go:22041	0x824032		55			PUSHQ BP																	
  checker.go:22041	0x824033		4889e5			MOVQ SP, BP																	
  checker.go:22041	0x824036		4881ec90060000		SUBQ $0x690, SP																	
  checker.go:22041	0x82403d		0f1f00			NOPL 0(AX)																	
  checker.go:22045	0x824040		4885db			TESTQ BX, BX																	
  checker.go:22045	0x824043		0f849e000000		JE 0x8240e7																	
  checker.go:22045	0x824049		4885c9			TESTQ CX, CX																	
  checker.go:22045	0x82404c		0f8495000000		JE 0x8240e7																	
  checker.go:22045	0x824052		48898424a0060000	MOVQ AX, 0x6a0(SP)																
  checker.go:22045	0x82405a		48899c24a8060000	MOVQ BX, 0x6a8(SP)																
  ... [unrelated caller instructions omitted] ...
  core.go:248		0x824124		4c8b9424b0060000	MOVQ 0x6b0(SP), R10																
  core.go:248		0x82412c		e962020000		JMP 0x824393																	
  checker.go:22052	0x824131		4c8b8a88120000		MOVQ 0x1288(DX), R9																
  checker.go:22052	0x824138		0f1f840000000000	NOPL 0(AX)(AX*1)																
  checker.go:22052	0x824140		4d85c9			TESTQ R9, R9																	
  checker.go:22052	0x824143		0f840a020000		JE 0x824353																	
  checker.go:22052	0x824149		4c898c2480000000	MOVQ R9, 0x80(SP)																
  checker.go:22053	0x824151		488d842460060000	LEAQ 0x660(SP), AX																
  checker.go:22053	0x824159		440f1138		MOVUPS X15, 0(AX)																
  checker.go:22053	0x82415d		440f117810		MOVUPS X15, 0x10(AX)																
  checker.go:22053	0x824162		440f117820		MOVUPS X15, 0x20(AX)																
  checker.go:22053	0x824167		488d842458050000	LEAQ 0x558(SP), AX																
  checker.go:22053	0x82416f		b904000000		MOVL $0x4, CX																	
  checker.go:22053	0x824174		440f1138		MOVUPS X15, 0(AX)																
  checker.go:22053	0x824178		440f117810		MOVUPS X15, 0x10(AX)																
  checker.go:22053	0x82417d		440f117820		MOVUPS X15, 0x20(AX)																
  checker.go:22053	0x824182		440f117830		MOVUPS X15, 0x30(AX)																
  checker.go:22053	0x824187		4883c040		ADDQ $0x40, AX																	
  checker.go:22053	0x82418b		ffc9			DECL CX																		
  checker.go:22053	0x82418d		75e5			JNE 0x824174																	
  checker.go:22053	0x82418f		440f1178f8		MOVUPS X15, -0x8(AX)																
  checker.go:22053	0x824194		48b88080808080808080	MOVQ $0x8080808080808080, AX															
  checker.go:22053	0x82419e		4889842458050000	MOVQ AX, 0x558(SP)																
  checker.go:22053	0x8241a6		488d842458050000	LEAQ 0x558(SP), AX																
  checker.go:22053	0x8241ae		4889842470060000	MOVQ AX, 0x670(SP)																
  checker.go:22053	0x8241b6		e84569c6ff		CALL runtime.rand(SB)																
  checker.go:22053	0x8241bb		4889842468060000	MOVQ AX, 0x668(SP)																
  checker.go:22053	0x8241c3		488b8424a8060000	MOVQ 0x6a8(SP), AX																
  ... [unrelated caller instructions omitted] ...
  checker.go:22094	0x8245b3		49895308		MOVQ DX, 0x8(R11)																
  checker.go:22094	0x8245b7		488944def8		MOVQ AX, -0x8(SI)(BX*8)																
  checker.go:17347	0x8245bc		488b8424a8060000	MOVQ 0x6a8(SP), AX																
  checker.go:22066	0x8245c4		4889ca			MOVQ CX, DX																	
  checker.go:22059	0x8245c7		4c8b4c2440		MOVQ 0x40(SP), R9																
  checker.go:22073	0x8245cc		4c8b9424b0060000	MOVQ 0x6b0(SP), R10																
  checker.go:22062	0x8245d4		488d942498000000	LEAQ 0x98(SP), DX																
  checker.go:22062	0x8245dc		be12000000		MOVL $0x12, SI																	
  checker.go:22062	0x8245e1		440f113a		MOVUPS X15, 0(DX)																
  checker.go:22062	0x8245e5		440f117a10		MOVUPS X15, 0x10(DX)																
  checker.go:22062	0x8245ea		440f117a20		MOVUPS X15, 0x20(DX)																
  checker.go:22062	0x8245ef		440f117a30		MOVUPS X15, 0x30(DX)																
  checker.go:22062	0x8245f4		4883c240		ADDQ $0x40, DX																	
  checker.go:22062	0x8245f8		ffce			DECL SI																		
  checker.go:22062	0x8245fa		75e5			JNE 0x8245e1																	
  checker.go:22062	0x8245fc		440f113a		MOVUPS X15, 0(DX)																
  checker.go:22062	0x824600		440f117a10		MOVUPS X15, 0x10(DX)																
  checker.go:17347	0x824605		8b4808			MOVL 0x8(AX), CX																
  checker.go:22063	0x824608		90			NOPL																		
  checker.go:17347	0x824609		488d0580f3cf00		LEAQ github.com/microsoft/typescript-go/internal/checker..dict.hashWrite32[github.com/microsoft/typescript-go/internal/checker.TypeId](SB), AX	
  checker.go:17347	0x824610		488d9c2498000000	LEAQ 0x98(SP), BX																
  checker.go:17347	0x824618		e8234c0e00		CALL github.com/microsoft/typescript-go/internal/checker.hashWrite32[go.shape.uint32](SB)							
  checker.go:22064	0x82461d		488d842498000000	LEAQ 0x98(SP), AX																
  checker.go:22064	0x824625		488b9c24b8060000	MOVQ 0x6b8(SP), BX																
  checker.go:22064	0x82462d		e8ce0afeff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)								
  checker.go:22065	0x824632		90			NOPL																		
  checker.go:17327	0x824633		488d842498000000	LEAQ 0x98(SP), AX																
  checker.go:17327	0x82463b		0f1f440000		NOPL 0(AX)(AX*1)																
  checker.go:17327	0x824640		e81b04d8ff		CALL github.com/zeebo/xxh3.(*Hasher).Sum128(SB)													
  checker.go:22066	0x824645		488b9424a0060000	MOVQ 0x6a0(SP), DX																
  checker.go:22066	0x82464d		488bb210120000		MOVQ 0x1210(DX), SI																
  checker.go:22059	0x824654		488b7c2440		MOVQ 0x40(SP), DI																
  checker.go:22059	0x824659		4883ffff		CMPQ DI, $-0x1																	
  core.go:403		0x82465d		7405			JE 0x824664																	
  checker.go:22058	0x82465f		4889f9			MOVQ DI, CX																	
  checker.go:22066	0x824662		eb0a			JMP 0x82466e																	
