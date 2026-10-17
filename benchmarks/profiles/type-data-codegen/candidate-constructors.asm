TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:24988	0x839800		493b6610		CMPQ SP, 0x10(R14)
  checker.go:24988	0x839804		0f86d9000000		JBE 0x8398e3
  checker.go:24988	0x83980a		55			PUSHQ BP
  checker.go:24988	0x83980b		4889e5			MOVQ SP, BP
  checker.go:24988	0x83980e		4883ec20		SUBQ $0x20, SP
  checker.go:24989	0x839812		ff4058			INCL 0x58(AX)
  checker.go:24991	0x839815		891f			MOVL BX, 0(DI)
  checker.go:24992	0x839817		81e1ffffc7ff		ANDL $-0x380001, CX
  checker.go:24992	0x83981d		894f04			MOVL CX, 0x4(DI)
  checker.go:24993	0x839820		8b4858			MOVL 0x58(AX), CX
  checker.go:24993	0x839823		894f08			MOVL CX, 0x8(DI)
  checker.go:24994	0x839826		833de3fc6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:24994	0x83982d		741c			JE 0x83984b
  checker.go:24994	0x83982f		488b4f20		MOVQ 0x20(DI), CX
  checker.go:24995	0x839833		488b5728		MOVQ 0x28(DI), DX
  checker.go:24994	0x839837		e8047dc5ff		CALL runtime.gcWriteBarrier4(SB)
  checker.go:24994	0x83983c		498903			MOVQ AX, 0(R11)
  checker.go:24994	0x83983f		49894b08		MOVQ CX, 0x8(R11)
  checker.go:24995	0x839843		49897b10		MOVQ DI, 0x10(R11)
  checker.go:24995	0x839847		49895318		MOVQ DX, 0x18(R11)
  checker.go:24994	0x83984b		48894720		MOVQ AX, 0x20(DI)
  checker.go:24995	0x83984f		48897f28		MOVQ DI, 0x28(DI)
  checker.go:24996	0x839853		4088770c		MOVB SI, 0xc(DI)
  checker.go:24997	0x839857		488b8870120000		MOVQ 0x1270(AX), CX
  checker.go:24997	0x83985e		6690			NOPW
  checker.go:24997	0x839860		4885c9			TESTQ CX, CX
  checker.go:24997	0x839863		7475			JE 0x8398da
  checker.go:24997	0x839865		48897c2440		MOVQ DI, 0x40(SP)
  checker.go:24997	0x83986a		48894c2418		MOVQ CX, 0x18(SP)
  checker.go:24998	0x83986f		90			NOPL
  tracer.go:353		0x839870		488d05897d5e00		LEAQ 0x5e7d89(IP), AX
  tracer.go:353		0x839877		e8c4a6beff		CALL runtime.newobject(SB)
  tracer.go:353		0x83987c		833d8dfc6b0100		CMPL runtime.writeBarrier(SB), $0x0
  tracer.go:353		0x839883		7507			JNE 0x83988c
  tracer.go:353		0x839885		488b542440		MOVQ 0x40(SP), DX
  tracer.go:353		0x83988a		eb0d			JMP 0x839899
  tracer.go:353		0x83988c		e84f7cc5ff		CALL runtime.gcWriteBarrier1(SB)
  tracer.go:353		0x839891		488b542440		MOVQ 0x40(SP), DX
  tracer.go:353		0x839896		498913			MOVQ DX, 0(R11)
  tracer.go:353		0x839899		488910			MOVQ DX, 0(AX)
  tracer.go:353		0x83989c		488b7220		MOVQ 0x20(DX), SI
  tracer.go:353		0x8398a0		833d69fc6b0100		CMPL runtime.writeBarrier(SB), $0x0
  tracer.go:353		0x8398a7		7408			JE 0x8398b1
  tracer.go:353		0x8398a9		e8327cc5ff		CALL runtime.gcWriteBarrier1(SB)
  tracer.go:353		0x8398ae		498933			MOVQ SI, 0(R11)
  tracer.go:353		0x8398b1		48897008		MOVQ SI, 0x8(AX)
  tracer.go:26		0x8398b5		488b542418		MOVQ 0x18(SP), DX
  tracer.go:26		0x8398ba		488b7208		MOVQ 0x8(DX), SI
  tracer.go:26		0x8398be		488b5210		MOVQ 0x10(DX), DX
  tracer.go:26		0x8398c2		488b7620		MOVQ 0x20(SI), SI
  tracer.go:26		0x8398c6		488d1db334d100		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.tracedTypeAdapter,github.com/microsoft/typescript-go/internal/tracing.TracedType(SB), BX
  tracer.go:26		0x8398cd		4889c1			MOVQ AX, CX
  tracer.go:26		0x8398d0		4889d0			MOVQ DX, AX
  tracer.go:26		0x8398d3		ffd6			CALL SI
  checker.go:25000	0x8398d5		488b7c2440		MOVQ 0x40(SP), DI
  checker.go:25000	0x8398da		4889f8			MOVQ DI, AX
  checker.go:25000	0x8398dd		4883c420		ADDQ $0x20, SP
  checker.go:25000	0x8398e1		5d			POPQ BP
  checker.go:25000	0x8398e2		c3			RET
  checker.go:24988	0x8398e3		4889442408		MOVQ AX, 0x8(SP)
  checker.go:24988	0x8398e8		895c2410		MOVL BX, 0x10(SP)
  checker.go:24988	0x8398ec		894c2414		MOVL CX, 0x14(SP)
  checker.go:24988	0x8398f0		48897c2418		MOVQ DI, 0x18(SP)
  checker.go:24988	0x8398f5		4088742420		MOVB SI, 0x20(SP)
  checker.go:24988	0x8398fa		e80161c5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:24988	0x8398ff		488b442408		MOVQ 0x8(SP), AX
  checker.go:24988	0x839904		8b5c2410		MOVL 0x10(SP), BX
  checker.go:24988	0x839908		8b4c2414		MOVL 0x14(SP), CX
  checker.go:24988	0x83990c		488b7c2418		MOVQ 0x18(SP), DI
  checker.go:24988	0x839911		0fb6742420		MOVZX 0x20(SP), SI
  checker.go:24988	0x839916		e9e5feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newObjectType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:25049	0x839cc0		493b6610		CMPQ SP, 0x10(R14)
  checker.go:25049	0x839cc4		0f8656010000		JBE 0x839e20
  checker.go:25049	0x839cca		55			PUSHQ BP
  checker.go:25049	0x839ccb		4889e5			MOVQ SP, BP
  checker.go:25049	0x839cce		4883ec20		SUBQ $0x20, SP
  checker.go:25053	0x839cd2		4889442430		MOVQ AX, 0x30(SP)
  checker.go:25053	0x839cd7		895c2438		MOVL BX, 0x38(SP)
  checker.go:25053	0x839cdb		48894c2440		MOVQ CX, 0x40(SP)
  checker.go:25053	0x839ce0		f7c303000000		TESTL $0x3, BX
  checker.go:25053	0x839ce6		0f85c6000000		JNE 0x839db2
  checker.go:25056	0x839cec		0fbae303		BTL $0x3, BX
  checker.go:25056	0x839cf0		0f82a9000000		JB 0x839d9f
  checker.go:25059	0x839cf6		0fbae302		BTL $0x2, BX
  checker.go:25059	0x839cfa		660f1f440000		NOPW 0(AX)(AX*1)
  checker.go:25059	0x839d00		0f8286000000		JB 0x839d8c
  checker.go:25062	0x839d06		0fbae305		BTL $0x5, BX
  checker.go:25062	0x839d0a		726b			JB 0x839d77
  checker.go:25065	0x839d0c		0fbae30a		BTL $0xa, BX
  checker.go:25065	0x839d10		7252			JB 0x839d64
  checker.go:25068	0x839d12		0fbae308		BTL $0x8, BX
  checker.go:25068	0x839d16		7239			JB 0x839d51
  checker.go:25071	0x839d18		0fbae318		BTL $0x18, BX
  checker.go:25071	0x839d1c		7220			JB 0x839d3e
  checker.go:25074	0x839d1e		0fbae304		BTL $0x4, BX
  checker.go:25074	0x839d22		0f83e4000000		JAE 0x839e0c
  checker.go:25075	0x839d28		488d0531346300		LEAQ 0x633431(IP), AX
  checker.go:25075	0x839d2f		e80ca2beff		CALL runtime.newobject(SB)
  checker.go:25075	0x839d34		b907000000		MOVL $0x7, CX
  checker.go:25076	0x839d39		e985000000		JMP 0x839dc3
  checker.go:25072	0x839d3e		488d051b735e00		LEAQ 0x5e731b(IP), AX
  checker.go:25072	0x839d45		e8f6a1beff		CALL runtime.newobject(SB)
  checker.go:25072	0x839d4a		b90b000000		MOVL $0xb, CX
  checker.go:25073	0x839d4f		eb72			JMP 0x839dc3
  checker.go:25069	0x839d51		488d0568086100		LEAQ 0x610868(IP), AX
  checker.go:25069	0x839d58		e8e3a1beff		CALL runtime.newobject(SB)
  checker.go:25069	0x839d5d		b90e000000		MOVL $0xe, CX
  checker.go:25070	0x839d62		eb5f			JMP 0x839dc3
  checker.go:25066	0x839d64		488d0535336300		LEAQ 0x633335(IP), AX
  checker.go:25066	0x839d6b		e8d0a1beff		CALL runtime.newobject(SB)
  checker.go:25066	0x839d70		b90d000000		MOVL $0xd, CX
  checker.go:25067	0x839d75		eb4c			JMP 0x839dc3
  checker.go:25063	0x839d77		488d0522c26700		LEAQ 0x67c222(IP), AX
  checker.go:25063	0x839d7e		6690			NOPW
  checker.go:25063	0x839d80		e8bba1beff		CALL runtime.newobject(SB)
  checker.go:25063	0x839d85		b90c000000		MOVL $0xc, CX
  checker.go:25064	0x839d8a		eb37			JMP 0x839dc3
  checker.go:25060	0x839d8c		488d05ed0b6100		LEAQ 0x610bed(IP), AX
  checker.go:25060	0x839d93		e8a8a1beff		CALL runtime.newobject(SB)
  checker.go:25060	0x839d98		b908000000		MOVL $0x8, CX
  checker.go:25061	0x839d9d		eb24			JMP 0x839dc3
  checker.go:25057	0x839d9f		488d05dadb6500		LEAQ 0x65dbda(IP), AX
  checker.go:25057	0x839da6		e895a1beff		CALL runtime.newobject(SB)
  checker.go:25057	0x839dab		b90a000000		MOVL $0xa, CX
  checker.go:25058	0x839db0		eb11			JMP 0x839dc3
  checker.go:25054	0x839db2		488d05076e6900		LEAQ 0x696e07(IP), AX
  checker.go:25054	0x839db9		e882a1beff		CALL runtime.newobject(SB)
  checker.go:25054	0x839dbe		b909000000		MOVL $0x9, CX
  checker.go:25080	0x839dc3		bb00001000		MOVL $0x100000, BX
  checker.go:25080	0x839dc8		4889c7			MOVQ AX, DI
  checker.go:25080	0x839dcb		89ce			MOVL CX, SI
  checker.go:25080	0x839dcd		488b442430		MOVQ 0x30(SP), AX
  checker.go:25080	0x839dd2		8b4c2438		MOVL 0x38(SP), CX
  checker.go:25080	0x839dd6		e825faffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB)
  checker.go:25081	0x839ddb		8400			TESTB AL, 0(AX)
  checker.go:25081	0x839ddd		833d2cf76b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25081	0x839de4		7507			JNE 0x839ded
  checker.go:25081	0x839de6		488b542440		MOVQ 0x40(SP), DX
  checker.go:25081	0x839deb		eb15			JMP 0x839e02
  checker.go:25081	0x839ded		488b4810		MOVQ 0x10(AX), CX
  checker.go:25081	0x839df1		e80a77c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25081	0x839df6		488b542440		MOVQ 0x40(SP), DX
  checker.go:25081	0x839dfb		498913			MOVQ DX, 0(R11)
  checker.go:25081	0x839dfe		49894b08		MOVQ CX, 0x8(R11)
  checker.go:25081	0x839e02		48895010		MOVQ DX, 0x10(AX)
  checker.go:25082	0x839e06		4883c420		ADDQ $0x20, SP
  checker.go:25082	0x839e0a		5d			POPQ BP
  checker.go:25082	0x839e0b		c3			RET
  checker.go:25078	0x839e0c		488d054d885200		LEAQ 0x52884d(IP), AX
  checker.go:25078	0x839e13		488d1de6c5ce00		LEAQ 0xcec5e6(IP), BX
  checker.go:25078	0x839e1a		e881fcc4ff		CALL runtime.gopanic(SB)
  checker.go:25078	0x839e1f		90			NOPL
  checker.go:25049	0x839e20		4889442408		MOVQ AX, 0x8(SP)
  checker.go:25049	0x839e25		895c2410		MOVL BX, 0x10(SP)
  checker.go:25049	0x839e29		48894c2418		MOVQ CX, 0x18(SP)
  checker.go:25049	0x839e2e		e8cd5bc5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:25049	0x839e33		488b442408		MOVQ 0x8(SP), AX
  checker.go:25049	0x839e38		8b5c2410		MOVL 0x10(SP), BX
  checker.go:25049	0x839e3c		488b4c2418		MOVQ 0x18(SP), CX
  checker.go:25049	0x839e41		e97afeffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newObjectType(SB)
