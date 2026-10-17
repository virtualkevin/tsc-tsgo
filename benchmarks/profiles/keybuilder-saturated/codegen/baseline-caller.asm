  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:22001	0x823e00		4c8da424f8fdffff	LEAQ 0xfffffdf8(SP), R12														
  checker.go:22001	0x823e08		4d3b6610		CMPQ R12, 0x10(R14)															
  checker.go:22001	0x823e0c		0f8693080000		JBE 0x8246a5																
  checker.go:22001	0x823e12		55			PUSHQ BP																
  checker.go:22001	0x823e13		4889e5			MOVQ SP, BP																
  checker.go:22001	0x823e16		4881ec80020000		SUBQ $0x280, SP																
  checker.go:22001	0x823e1d		0f1f00			NOPL 0(AX)																
  checker.go:22005	0x823e20		4885db			TESTQ BX, BX																
  checker.go:22005	0x823e23		0f849e000000		JE 0x823ec7																
  checker.go:22005	0x823e29		4885c9			TESTQ CX, CX																
  checker.go:22005	0x823e2c		0f8495000000		JE 0x823ec7																
  checker.go:22005	0x823e32		4889842490020000	MOVQ AX, 0x290(SP)															
  checker.go:22005	0x823e3a		48899c2498020000	MOVQ BX, 0x298(SP)															
  ... [unrelated caller instructions omitted] ...
  core.go:248		0x823f04		4c8b9424a0020000	MOVQ 0x2a0(SP), R10															
  core.go:248		0x823f0c		e962020000		JMP 0x824173																
  checker.go:22012	0x823f11		4c8b8a88120000		MOVQ 0x1288(DX), R9															
  checker.go:22012	0x823f18		0f1f840000000000	NOPL 0(AX)(AX*1)															
  checker.go:22012	0x823f20		4d85c9			TESTQ R9, R9																
  checker.go:22012	0x823f23		0f840a020000		JE 0x824133																
  checker.go:22012	0x823f29		4c898c2480000000	MOVQ R9, 0x80(SP)															
  checker.go:22013	0x823f31		488d842450020000	LEAQ 0x250(SP), AX															
  checker.go:22013	0x823f39		440f1138		MOVUPS X15, 0(AX)															
  checker.go:22013	0x823f3d		440f117810		MOVUPS X15, 0x10(AX)															
  checker.go:22013	0x823f42		440f117820		MOVUPS X15, 0x20(AX)															
  checker.go:22013	0x823f47		488d842448010000	LEAQ 0x148(SP), AX															
  checker.go:22013	0x823f4f		b904000000		MOVL $0x4, CX																
  checker.go:22013	0x823f54		440f1138		MOVUPS X15, 0(AX)															
  checker.go:22013	0x823f58		440f117810		MOVUPS X15, 0x10(AX)															
  checker.go:22013	0x823f5d		440f117820		MOVUPS X15, 0x20(AX)															
  checker.go:22013	0x823f62		440f117830		MOVUPS X15, 0x30(AX)															
  checker.go:22013	0x823f67		4883c040		ADDQ $0x40, AX																
  checker.go:22013	0x823f6b		ffc9			DECL CX																	
  checker.go:22013	0x823f6d		75e5			JNE 0x823f54																
  checker.go:22013	0x823f6f		440f1178f8		MOVUPS X15, -0x8(AX)															
  checker.go:22013	0x823f74		48b88080808080808080	MOVQ $0x8080808080808080, AX														
  checker.go:22013	0x823f7e		4889842448010000	MOVQ AX, 0x148(SP)															
  checker.go:22013	0x823f86		488d842448010000	LEAQ 0x148(SP), AX															
  checker.go:22013	0x823f8e		4889842460020000	MOVQ AX, 0x260(SP)															
  checker.go:22013	0x823f96		e8656bc6ff		CALL runtime.rand(SB)															
  checker.go:22013	0x823f9b		4889842458020000	MOVQ AX, 0x258(SP)															
  checker.go:22013	0x823fa3		488b842498020000	MOVQ 0x298(SP), AX															
  ... [unrelated caller instructions omitted] ...
  checker.go:22054	0x824390		498903			MOVQ AX, 0(R11)																
  checker.go:22054	0x824393		49895308		MOVQ DX, 0x8(R11)															
  checker.go:22054	0x824397		488944def8		MOVQ AX, -0x8(SI)(BX*8)															
  checker.go:17307	0x82439c		488b842498020000	MOVQ 0x298(SP), AX															
  checker.go:22026	0x8243a4		4889ca			MOVQ CX, DX																
  checker.go:22019	0x8243a7		4c8b4c2440		MOVQ 0x40(SP), R9															
  checker.go:22033	0x8243ac		4c8b9424a0020000	MOVQ 0x2a0(SP), R10															
  checker.go:22022	0x8243b4		488d8c2498000000	LEAQ 0x98(SP), CX															
  checker.go:22022	0x8243bc		440f1139		MOVUPS X15, 0(CX)															
  checker.go:22022	0x8243c0		440f117910		MOVUPS X15, 0x10(CX)															
  checker.go:22022	0x8243c5		440f117920		MOVUPS X15, 0x20(CX)															
  checker.go:22022	0x8243ca		440f117930		MOVUPS X15, 0x30(CX)															
  checker.go:22022	0x8243cf		440f117940		MOVUPS X15, 0x40(CX)															
  checker.go:22022	0x8243d4		440f117950		MOVUPS X15, 0x50(CX)															
  checker.go:22022	0x8243d9		440f117960		MOVUPS X15, 0x60(CX)															
  checker.go:22022	0x8243de		440f117970		MOVUPS X15, 0x70(CX)															
  checker.go:22022	0x8243e3		440f11b980000000	MOVUPS X15, 0x80(CX)															
  checker.go:17307	0x8243eb		8b5808			MOVL 0x8(AX), BX															
  checker.go:22023	0x8243ee		90			NOPL																	
  checker.go:17307	0x8243ef		4889c8			MOVQ CX, AX																
  checker.go:17307	0x8243f2		e8698d0700		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeUint32(SB)							
  checker.go:22024	0x8243f7		488d842498000000	LEAQ 0x98(SP), AX															
  checker.go:22024	0x8243ff		488b9c24a8020000	MOVQ 0x2a8(SP), BX															
  checker.go:22024	0x824407		e8b40cfeff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)							
  checker.go:22025	0x82440c		488d842498000000	LEAQ 0x98(SP), AX															
  checker.go:22025	0x824414		e8a78a0700		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)								
  checker.go:22026	0x824419		488b8c2490020000	MOVQ 0x290(SP), CX															
  checker.go:22026	0x824421		488b9110120000		MOVQ 0x1210(CX), DX															
  checker.go:22019	0x824428		488b742440		MOVQ 0x40(SP), SI															
  checker.go:22019	0x82442d		4883feff		CMPQ SI, $-0x1																
  core.go:403		0x824431		7405			JE 0x824438																
  checker.go:22018	0x824433		4889f7			MOVQ SI, DI																
  checker.go:22026	0x824436		eb0a			JMP 0x824442																
