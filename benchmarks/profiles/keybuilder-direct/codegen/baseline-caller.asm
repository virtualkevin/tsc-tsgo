  ... [unrelated caller instructions omitted] ...
TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:22001	0x823f80		4c8da424f0fdffff	LEAQ 0xfffffdf0(SP), R12														
  checker.go:22001	0x823f88		4d3b6610		CMPQ R12, 0x10(R14)															
  checker.go:22001	0x823f8c		0f86bc080000		JBE 0x82484e																
  checker.go:22001	0x823f92		55			PUSHQ BP																
  checker.go:22001	0x823f93		4889e5			MOVQ SP, BP																
  checker.go:22001	0x823f96		4881ec88020000		SUBQ $0x288, SP																
  checker.go:22001	0x823f9d		0f1f00			NOPL 0(AX)																
  checker.go:22005	0x823fa0		4885db			TESTQ BX, BX																
  checker.go:22005	0x823fa3		0f849e000000		JE 0x824047																
  checker.go:22005	0x823fa9		4885c9			TESTQ CX, CX																
  checker.go:22005	0x823fac		0f8495000000		JE 0x824047																
  checker.go:22005	0x823fb2		4889842498020000	MOVQ AX, 0x298(SP)															
  checker.go:22005	0x823fba		48899c24a0020000	MOVQ BX, 0x2a0(SP)															
  ... [unrelated caller instructions omitted] ...
  core.go:248		0x824084		4c8b9424a8020000	MOVQ 0x2a8(SP), R10															
  core.go:248		0x82408c		e962020000		JMP 0x8242f3																
  checker.go:22012	0x824091		4c8b8a88120000		MOVQ 0x1288(DX), R9															
  checker.go:22012	0x824098		0f1f840000000000	NOPL 0(AX)(AX*1)															
  checker.go:22012	0x8240a0		4d85c9			TESTQ R9, R9																
  checker.go:22012	0x8240a3		0f840a020000		JE 0x8242b3																
  checker.go:22012	0x8240a9		4c898c2488000000	MOVQ R9, 0x88(SP)															
  checker.go:22013	0x8240b1		488d842450020000	LEAQ 0x250(SP), AX															
  checker.go:22013	0x8240b9		440f1138		MOVUPS X15, 0(AX)															
  checker.go:22013	0x8240bd		440f117810		MOVUPS X15, 0x10(AX)															
  checker.go:22013	0x8240c2		440f117820		MOVUPS X15, 0x20(AX)															
  checker.go:22013	0x8240c7		488d842448010000	LEAQ 0x148(SP), AX															
  checker.go:22013	0x8240cf		b904000000		MOVL $0x4, CX																
  checker.go:22013	0x8240d4		440f1138		MOVUPS X15, 0(AX)															
  checker.go:22013	0x8240d8		440f117810		MOVUPS X15, 0x10(AX)															
  checker.go:22013	0x8240dd		440f117820		MOVUPS X15, 0x20(AX)															
  checker.go:22013	0x8240e2		440f117830		MOVUPS X15, 0x30(AX)															
  checker.go:22013	0x8240e7		4883c040		ADDQ $0x40, AX																
  checker.go:22013	0x8240eb		ffc9			DECL CX																	
  checker.go:22013	0x8240ed		75e5			JNE 0x8240d4																
  checker.go:22013	0x8240ef		440f1178f8		MOVUPS X15, -0x8(AX)															
  checker.go:22013	0x8240f4		48b88080808080808080	MOVQ $0x8080808080808080, AX														
  checker.go:22013	0x8240fe		4889842448010000	MOVQ AX, 0x148(SP)															
  checker.go:22013	0x824106		488d842448010000	LEAQ 0x148(SP), AX															
  checker.go:22013	0x82410e		4889842460020000	MOVQ AX, 0x260(SP)															
  checker.go:22013	0x824116		e8e569c6ff		CALL runtime.rand(SB)															
  checker.go:22013	0x82411b		4889842458020000	MOVQ AX, 0x258(SP)															
  checker.go:22013	0x824123		488b8424a0020000	MOVQ 0x2a0(SP), AX															
  ... [unrelated caller instructions omitted] ...
  checker.go:22054	0x824510		498903			MOVQ AX, 0(R11)																
  checker.go:22054	0x824513		49895308		MOVQ DX, 0x8(R11)															
  checker.go:22054	0x824517		488944def8		MOVQ AX, -0x8(SI)(BX*8)															
  checker.go:17307	0x82451c		488b8424a0020000	MOVQ 0x2a0(SP), AX															
  checker.go:22026	0x824524		4889ca			MOVQ CX, DX																
  checker.go:22019	0x824527		4c8b4c2448		MOVQ 0x48(SP), R9															
  checker.go:22033	0x82452c		4c8b9424a8020000	MOVQ 0x2a8(SP), R10															
  checker.go:22022	0x824534		488d9424a0000000	LEAQ 0xa0(SP), DX															
  checker.go:22022	0x82453c		440f113a		MOVUPS X15, 0(DX)															
  checker.go:22022	0x824540		440f117a10		MOVUPS X15, 0x10(DX)															
  checker.go:22022	0x824545		440f117a20		MOVUPS X15, 0x20(DX)															
  checker.go:22022	0x82454a		440f117a30		MOVUPS X15, 0x30(DX)															
  checker.go:22022	0x82454f		440f117a40		MOVUPS X15, 0x40(DX)															
  checker.go:22022	0x824554		440f117a50		MOVUPS X15, 0x50(DX)															
  checker.go:22022	0x824559		440f117a60		MOVUPS X15, 0x60(DX)															
  checker.go:22022	0x82455e		440f117a70		MOVUPS X15, 0x70(DX)															
  checker.go:22022	0x824563		440f11ba80000000	MOVUPS X15, 0x80(DX)															
  checker.go:17307	0x82456b		8b7008			MOVL 0x8(AX), SI															
  checker.go:22023	0x82456e		90			NOPL																	
  keybuilder.go:60	0x82456f		90			NOPL																	
  binary.go:98		0x824570		89742444		MOVL SI, 0x44(SP)															
  keybuilder.go:61	0x824574		4889d0			MOVQ DX, AX																
  keybuilder.go:61	0x824577		488d5c2444		LEAQ 0x44(SP), BX															
  keybuilder.go:61	0x82457c		b904000000		MOVL $0x4, CX																
  keybuilder.go:61	0x824581		4889cf			MOVQ CX, DI																
  keybuilder.go:61	0x824584		e8978c0700		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeBytes(SB)							
  checker.go:22024	0x824589		488d8424a0000000	LEAQ 0xa0(SP), AX															
  checker.go:22024	0x824591		488b9c24b0020000	MOVQ 0x2b0(SP), BX															
  checker.go:22024	0x824599		e8620bfeff		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).writeAlias(SB)							
  checker.go:22025	0x82459e		488d8424a0000000	LEAQ 0xa0(SP), AX															
  checker.go:22025	0x8245a6		e8358b0700		CALL github.com/microsoft/typescript-go/internal/checker.(*keyBuilder).hash(SB)								
  checker.go:22026	0x8245ab		488b942498020000	MOVQ 0x298(SP), DX															
  checker.go:22026	0x8245b3		488bb210120000		MOVQ 0x1210(DX), SI															
  checker.go:22019	0x8245ba		4c8b442448		MOVQ 0x48(SP), R8															
  checker.go:22019	0x8245bf		90			NOPL																	
  checker.go:22019	0x8245c0		4983f8ff		CMPQ R8, $-0x1																
  core.go:403		0x8245c4		7405			JE 0x8245cb																
  checker.go:22018	0x8245c6		4c89c1			MOVQ R8, CX																
