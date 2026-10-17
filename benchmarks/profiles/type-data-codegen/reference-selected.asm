TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).typeResolutionHasProperty(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:18704	0x80d4e0		493b6610		CMPQ SP, 0x10(R14)
  checker.go:18704	0x80d4e4		0f86f1020000		JBE 0x80d7db
  checker.go:18704	0x80d4ea		55			PUSHQ BP
  checker.go:18704	0x80d4eb		4889e5			MOVQ SP, BP
  checker.go:18704	0x80d4ee		4883ec18		SUBQ $0x18, SP
  checker.go:18705	0x80d4f2		48635310		MOVSXD 0x10(BX), DX
  checker.go:18705	0x80d4f6		660f1f840000000000	NOPW 0(AX)(AX*1)
  checker.go:18705	0x80d4ff		90			NOPL
  checker.go:18705	0x80d500		4883fa09		CMPQ DX, $0x9
  checker.go:18705	0x80d504		0f87bd020000		JA 0x80d7c7
  checker.go:18705	0x80d50a		488d0daf6cd200		LEAQ 0xd26caf(IP), CX
  checker.go:18705	0x80d511		ff24d1			JMP 0(CX)(DX*8)
  checker.go:18707	0x80d514		8400			TESTB AL, 0(AX)
  checker.go:18707	0x80d516		488b13			MOVQ 0(BX), DX
  checker.go:18707	0x80d519		488d35c05d5c00		LEAQ 0x5c5dc0(IP), SI
  checker.go:18707	0x80d520		4839f2			CMPQ DX, SI
  checker.go:18707	0x80d523		0f858c020000		JNE 0x80d7b5
  checker.go:18707	0x80d529		4805f8080000		ADDQ $0x8f8, AX
  checker.go:18707	0x80d52f		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18707	0x80d533		488d1d6607d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX
  checker.go:18707	0x80d53a		e8c1670f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)
  checker.go:18707	0x80d53f		48833800		CMPQ 0(AX), $0x0
  checker.go:18707	0x80d543		0f95c0			SETNE AL
  checker.go:18707	0x80d546		4883c418		ADDQ $0x18, SP
  checker.go:18707	0x80d54a		5d			POPQ BP
  checker.go:18707	0x80d54b		c3			RET
  checker.go:18715	0x80d54c		488b03			MOVQ 0(BX), AX
  checker.go:18715	0x80d54f		488d150aa06d00		LEAQ 0x6da00a(IP), DX
  checker.go:18715	0x80d556		4839d0			CMPQ AX, DX
  checker.go:18715	0x80d559		0f8547020000		JNE 0x80d7a6
  checker.go:18715	0x80d55f		488b4b08		MOVQ 0x8(BX), CX
  types.go:716		0x80d563		488b5128		MOVQ 0x28(CX), DX
  types.go:716		0x80d567		488b4130		MOVQ 0x30(CX), AX
  types.go:716		0x80d56b		488b4a20		MOVQ 0x20(DX), CX
  types.go:716		0x80d56f		ffd1			CALL CX
  checker.go:18715	0x80d571		4883b81001000000	CMPQ 0x110(AX), $0x0
  checker.go:18715	0x80d579		0f95c0			SETNE AL
  checker.go:18715	0x80d57c		4883c418		ADDQ $0x18, SP
  checker.go:18715	0x80d580		5d			POPQ BP
  checker.go:18715	0x80d581		c3			RET
  checker.go:18709	0x80d582		8400			TESTB AL, 0(AX)
  checker.go:18709	0x80d584		488b13			MOVQ 0(BX), DX
  checker.go:18709	0x80d587		488d35525d5c00		LEAQ 0x5c5d52(IP), SI
  checker.go:18709	0x80d58e		4839f2			CMPQ DX, SI
  checker.go:18709	0x80d591		0f85fd010000		JNE 0x80d794
  checker.go:18709	0x80d597		4805f8090000		ADDQ $0x9f8, AX
  checker.go:18709	0x80d59d		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18709	0x80d5a1		488d1df800d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.TypeAliasLinks](SB), BX
  checker.go:18709	0x80d5a8		e853780f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.07b4bb953fce386053033c51a7b2f9f24c1586764f3e1f7952f8941b6d2d7f9e]).Get(SB)
  checker.go:18709	0x80d5ad		48833800		CMPQ 0(AX), $0x0
  checker.go:18709	0x80d5b1		0f95c0			SETNE AL
  checker.go:18709	0x80d5b4		4883c418		ADDQ $0x18, SP
  checker.go:18709	0x80d5b8		5d			POPQ BP
  checker.go:18709	0x80d5b9		c3			RET
  checker.go:18717	0x80d5ba		488b03			MOVQ 0(BX), AX
  checker.go:18717	0x80d5bd		488d157c296700		LEAQ 0x67297c(IP), DX
  checker.go:18717	0x80d5c4		4839d0			CMPQ AX, DX
  checker.go:18717	0x80d5c7		0f85b8010000		JNE 0x80d785
  checker.go:18717	0x80d5cd		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18717	0x80d5d1		4883795000		CMPQ 0x50(CX), $0x0
  checker.go:18717	0x80d5d6		0f95c0			SETNE AL
  checker.go:18717	0x80d5d9		4883c418		ADDQ $0x18, SP
  checker.go:18717	0x80d5dd		5d			POPQ BP
  checker.go:18717	0x80d5de		c3			RET
  checker.go:18719	0x80d5df		488b03			MOVQ 0(BX), AX
  checker.go:18719	0x80d5e2		488d15779f6d00		LEAQ 0x6d9f77(IP), DX
  checker.go:18719	0x80d5e9		4839d0			CMPQ AX, DX
  checker.go:18719	0x80d5ec		0f8584010000		JNE 0x80d776
  checker.go:18719	0x80d5f2		488b4b08		MOVQ 0x8(BX), CX
  types.go:712		0x80d5f6		488b5128		MOVQ 0x28(CX), DX
  types.go:712		0x80d5fa		488b4130		MOVQ 0x30(CX), AX
  types.go:712		0x80d5fe		488b4a18		MOVQ 0x18(DX), CX
  types.go:712		0x80d602		ffd1			CALL CX
  checker.go:18719	0x80d604		4883783800		CMPQ 0x38(AX), $0x0
  checker.go:18719	0x80d609		0f95c0			SETNE AL
  checker.go:18719	0x80d60c		4883c418		ADDQ $0x18, SP
  checker.go:18719	0x80d610		5d			POPQ BP
  checker.go:18719	0x80d611		c3			RET
  checker.go:18711	0x80d612		488b03			MOVQ 0(BX), AX
  checker.go:18711	0x80d615		488d15449f6d00		LEAQ 0x6d9f44(IP), DX
  checker.go:18711	0x80d61c		0f1f4000		NOPL 0(AX)
  checker.go:18711	0x80d620		4839d0			CMPQ AX, DX
  checker.go:18711	0x80d623		0f853e010000		JNE 0x80d767
  checker.go:18711	0x80d629		488b4b08		MOVQ 0x8(BX), CX
  types.go:715		0x80d62d		488b5128		MOVQ 0x28(CX), DX
  types.go:715		0x80d631		488b4130		MOVQ 0x30(CX), AX
  types.go:715		0x80d635		488b4a40		MOVQ 0x40(DX), CX
  types.go:715		0x80d639		ffd1			CALL CX
  checker.go:18711	0x80d63b		4883b8c800000000	CMPQ 0xc8(AX), $0x0
  checker.go:18711	0x80d643		0f95c0			SETNE AL
  checker.go:18711	0x80d646		4883c418		ADDQ $0x18, SP
  checker.go:18711	0x80d64a		5d			POPQ BP
  checker.go:18711	0x80d64b		c3			RET
  checker.go:18713	0x80d64c		488b03			MOVQ 0(BX), AX
  checker.go:18713	0x80d64f		488d150a9f6d00		LEAQ 0x6d9f0a(IP), DX
  checker.go:18713	0x80d656		4839d0			CMPQ AX, DX
  checker.go:18713	0x80d659		0f85f9000000		JNE 0x80d758
  checker.go:18713	0x80d65f		488b4b08		MOVQ 0x8(BX), CX
  types.go:716		0x80d663		488b5128		MOVQ 0x28(CX), DX
  types.go:716		0x80d667		488b4130		MOVQ 0x30(CX), AX
  types.go:716		0x80d66b		488b4a20		MOVQ 0x20(DX), CX
  types.go:716		0x80d66f		ffd1			CALL CX
  checker.go:18713	0x80d671		0fb68008010000		MOVZX 0x108(AX), AX
  checker.go:18713	0x80d678		4883c418		ADDQ $0x18, SP
  checker.go:18713	0x80d67c		5d			POPQ BP
  checker.go:18713	0x80d67d		c3			RET
  checker.go:18723	0x80d67e		8400			TESTB AL, 0(AX)
  checker.go:18723	0x80d680		488b13			MOVQ 0(BX), DX
  checker.go:18723	0x80d683		488d35565c5c00		LEAQ 0x5c5c56(IP), SI
  checker.go:18723	0x80d68a		4839f2			CMPQ DX, SI
  checker.go:18723	0x80d68d		0f85b3000000		JNE 0x80d746
  checker.go:18723	0x80d693		4805f8080000		ADDQ $0x8f8, AX
  checker.go:18723	0x80d699		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18723	0x80d69d		488d1dfc05d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX
  checker.go:18723	0x80d6a4		e857660f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)
  checker.go:18723	0x80d6a9		4883780800		CMPQ 0x8(AX), $0x0
  checker.go:18723	0x80d6ae		0f95c0			SETNE AL
  checker.go:18723	0x80d6b1		4883c418		ADDQ $0x18, SP
  checker.go:18723	0x80d6b5		5d			POPQ BP
  checker.go:18723	0x80d6b6		c3			RET
  checker.go:18721	0x80d6b7		8400			TESTB AL, 0(AX)
  checker.go:18721	0x80d6b9		488b13			MOVQ 0(BX), DX
  checker.go:18721	0x80d6bc		488d355d327200		LEAQ 0x72325d(IP), SI
  checker.go:18721	0x80d6c3		4839f2			CMPQ DX, SI
  checker.go:18721	0x80d6c6		756c			JNE 0x80d734
  checker.go:18721	0x80d6c8		4805b8070000		ADDQ $0x7b8, AX
  checker.go:18721	0x80d6ce		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18721	0x80d6d2		488d1d470dd300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Node,github.com/microsoft/typescript-go/internal/checker.NodeLinks](SB), BX
  checker.go:18721	0x80d6d9		e8224f0f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Node,go.shape.struct { github.com/microsoft/typescript-go/internal/checker.flags github.com/microsoft/typescript-go/internal/checker.NodeCheckFlags; github.com/microsoft/typescript-go/internal/checker.declarationRequiresScopeChange github.com/microsoft/typescript-go/internal/core.Tristate; github.com/microsoft/typescript-go/internal/checker.hasReportedStatementInAmbientContext bool }]).Get(SB)
  checker.go:18721	0x80d6de		8b10			MOVL 0(AX), DX
  checker.go:18721	0x80d6e0		0fbae219		BTL $0x19, DX
  checker.go:18721	0x80d6e4		0f92c0			SETB AL
  checker.go:18721	0x80d6e7		4883c418		ADDQ $0x18, SP
  checker.go:18721	0x80d6eb		5d			POPQ BP
  checker.go:18721	0x80d6ec		c3			RET
  checker.go:18725	0x80d6ed		8400			TESTB AL, 0(AX)
  checker.go:18725	0x80d6ef		488b13			MOVQ 0(BX), DX
  checker.go:18725	0x80d6f2		488d35e75b5c00		LEAQ 0x5c5be7(IP), SI
  checker.go:18725	0x80d6f9		4839f2			CMPQ DX, SI
  checker.go:18725	0x80d6fc		7524			JNE 0x80d722
  checker.go:18725	0x80d6fe		480558090000		ADDQ $0x958, AX
  checker.go:18725	0x80d704		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18725	0x80d708		488d1d5103d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.AliasSymbolLinks](SB), BX
  checker.go:18725	0x80d70f		e84c6c0f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.struct { github.com/microsoft/typescript-go/internal/checker.immediateTarget *github.com/microsoft/typescript-go/internal/ast.Symbol; github.com/microsoft/typescript-go/internal/checker.aliasTarget *github.com/microsoft/typescript-go/internal/ast.Symbol; github.com/microsoft/typescript-go/internal/checker.referenced bool; github.com/microsoft/typescript-go/internal/checker.typeOnlyDeclaration *github.com/microsoft/typescript-go/internal/ast.Node }]).Get(SB)
  checker.go:18725	0x80d714		4883780800		CMPQ 0x8(AX), $0x0
  checker.go:18725	0x80d719		0f95c0			SETNE AL
  checker.go:18725	0x80d71c		4883c418		ADDQ $0x18, SP
  checker.go:18725	0x80d720		5d			POPQ BP
  checker.go:18725	0x80d721		c3			RET
  checker.go:18725	0x80d722		4889d0			MOVQ DX, AX
  checker.go:18725	0x80d725		4889f3			MOVQ SI, BX
  checker.go:18725	0x80d728		488d0d11a55900		LEAQ 0x59a511(IP), CX
  checker.go:18725	0x80d72f		e86c27c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18721	0x80d734		4889d0			MOVQ DX, AX
  checker.go:18721	0x80d737		4889f3			MOVQ SI, BX
  checker.go:18721	0x80d73a		488d0dffa45900		LEAQ 0x59a4ff(IP), CX
  checker.go:18721	0x80d741		e85a27c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18723	0x80d746		4889d0			MOVQ DX, AX
  checker.go:18723	0x80d749		4889f3			MOVQ SI, BX
  checker.go:18723	0x80d74c		488d0deda45900		LEAQ 0x59a4ed(IP), CX
  checker.go:18723	0x80d753		e84827c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18713	0x80d758		4889d3			MOVQ DX, BX
  checker.go:18713	0x80d75b		488d0ddea45900		LEAQ 0x59a4de(IP), CX
  checker.go:18713	0x80d762		e83927c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18711	0x80d767		4889d3			MOVQ DX, BX
  checker.go:18711	0x80d76a		488d0dcfa45900		LEAQ 0x59a4cf(IP), CX
  checker.go:18711	0x80d771		e82a27c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18719	0x80d776		4889d3			MOVQ DX, BX
  checker.go:18719	0x80d779		488d0dc0a45900		LEAQ 0x59a4c0(IP), CX
  checker.go:18719	0x80d780		e81b27c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18717	0x80d785		4889d3			MOVQ DX, BX
  checker.go:18717	0x80d788		488d0db1a45900		LEAQ 0x59a4b1(IP), CX
  checker.go:18717	0x80d78f		e80c27c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18709	0x80d794		4889d0			MOVQ DX, AX
  checker.go:18709	0x80d797		4889f3			MOVQ SI, BX
  checker.go:18709	0x80d79a		488d0d9fa45900		LEAQ 0x59a49f(IP), CX
  checker.go:18709	0x80d7a1		e8fa26c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18715	0x80d7a6		4889d3			MOVQ DX, BX
  checker.go:18715	0x80d7a9		488d0d90a45900		LEAQ 0x59a490(IP), CX
  checker.go:18715	0x80d7b0		e8eb26c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18707	0x80d7b5		4889d0			MOVQ DX, AX
  checker.go:18707	0x80d7b8		4889f3			MOVQ SI, BX
  checker.go:18707	0x80d7bb		488d0d7ea45900		LEAQ 0x59a47e(IP), CX
  checker.go:18707	0x80d7c2		e8d926c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18727	0x80d7c7		488d05320f5500		LEAQ 0x550f32(IP), AX
  checker.go:18727	0x80d7ce		488d1deb4cd100		LEAQ 0xd14ceb(IP), BX
  checker.go:18727	0x80d7d5		e8c6c2c7ff		CALL runtime.gopanic(SB)
  checker.go:18727	0x80d7da		90			NOPL
  checker.go:18704	0x80d7db		4889442408		MOVQ AX, 0x8(SP)
  checker.go:18704	0x80d7e0		48895c2410		MOVQ BX, 0x10(SP)
  checker.go:18704	0x80d7e5		e81622c8ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:18704	0x80d7ea		488b442408		MOVQ 0x8(SP), AX
  checker.go:18704	0x80d7ef		488b5c2410		MOVQ 0x10(SP), BX
  checker.go:18704	0x80d7f4		e9e7fcffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).typeResolutionHasProperty(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isReducibleIntersection(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:24918	0x8373c0		493b6610		CMPQ SP, 0x10(R14)
  checker.go:24918	0x8373c4		0f86b0000000		JBE 0x83747a
  checker.go:24918	0x8373ca		55			PUSHQ BP
  checker.go:24918	0x8373cb		4889e5			MOVQ SP, BP
  checker.go:24918	0x8373ce		4883ec28		SUBQ $0x28, SP
  types.go:702		0x8373d2		488b5328		MOVQ 0x28(BX), DX
  checker.go:24919	0x8373d6		90			NOPL
  types.go:702		0x8373d7		488d35a2d5cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.IntersectionType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), SI
  types.go:702		0x8373de		6690			NOPW
  types.go:702		0x8373e0		4839f2			CMPQ DX, SI
  types.go:702		0x8373e3		757e			JNE 0x837463
  types.go:702		0x8373e5		488b5330		MOVQ 0x30(BX), DX
  types.go:702		0x8373e9		4889542420		MOVQ DX, 0x20(SP)
  checker.go:24920	0x8373ee		4883baf000000000	CMPQ 0xf0(DX), $0x0
  checker.go:24920	0x8373f6		754a			JNE 0x837442
  types.go:702		0x8373f8		4889442438		MOVQ AX, 0x38(SP)
  checker.go:24921	0x8373fd		488b88380c0000		MOVQ 0xc38(AX), CX
  checker.go:22038	0x837404		31ff			XORL DI, DI
  checker.go:22038	0x837406		e815ccfeff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB)
  checker.go:24921	0x83740b		833dfeb06b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:24921	0x837412		7507			JNE 0x83741b
  checker.go:24921	0x837414		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24921	0x837419		eb18			JMP 0x837433
  checker.go:24921	0x83741b		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24921	0x837420		488b91f0000000		MOVQ 0xf0(CX), DX
  checker.go:24921	0x837427		e8d4a0c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:24921	0x83742c		498903			MOVQ AX, 0(R11)
  checker.go:24921	0x83742f		49895308		MOVQ DX, 0x8(R11)
  checker.go:24921	0x837433		488981f0000000		MOVQ AX, 0xf0(CX)
  checker.go:24923	0x83743a		488b442438		MOVQ 0x38(SP), AX
  checker.go:24923	0x83743f		4889ca			MOVQ CX, DX
  checker.go:24923	0x837442		488b9af0000000		MOVQ 0xf0(DX), BX
  checker.go:24923	0x837449		e8f2abfeff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getReducedType(SB)
  checker.go:24923	0x83744e		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24923	0x837453		483981f0000000		CMPQ 0xf0(CX), AX
  checker.go:24923	0x83745a		0f95c0			SETNE AL
  checker.go:24923	0x83745d		4883c428		ADDQ $0x28, SP
  checker.go:24923	0x837461		5d			POPQ BP
  checker.go:24923	0x837462		c3			RET
  types.go:702		0x837463		4889d0			MOVQ DX, AX
  types.go:702		0x837466		488d1d136f6b00		LEAQ 0x6b6f13(IP), BX
  types.go:702		0x83746d		488d0d0cb15f00		LEAQ 0x5fb10c(IP), CX
  types.go:702		0x837474		e8e78abeff		CALL runtime.panicdottypeI(SB)
  types.go:702		0x837479		90			NOPL
  checker.go:24918	0x83747a		4889442408		MOVQ AX, 0x8(SP)
  checker.go:24918	0x83747f		48895c2410		MOVQ BX, 0x10(SP)
  checker.go:24918	0x837484		e87785c5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:24918	0x837489		488b442408		MOVQ 0x8(SP), AX
  checker.go:24918	0x83748e		488b5c2410		MOVQ 0x10(SP), BX
  checker.go:24918	0x837493		e928ffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).isReducibleIntersection(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:24984	0x837c20		493b6610		CMPQ SP, 0x10(R14)
  checker.go:24984	0x837c24		0f8617010000		JBE 0x837d41
  checker.go:24984	0x837c2a		55			PUSHQ BP
  checker.go:24984	0x837c2b		4889e5			MOVQ SP, BP
  checker.go:24984	0x837c2e		4883ec28		SUBQ $0x28, SP
  checker.go:24992	0x837c32		4889442438		MOVQ AX, 0x38(SP)
  checker.go:24992	0x837c37		895c2440		MOVL BX, 0x40(SP)
  checker.go:24992	0x837c3b		894c2444		MOVL CX, 0x44(SP)
  checker.go:24992	0x837c3f		4889742450		MOVQ SI, 0x50(SP)
  checker.go:24992	0x837c44		48897c2448		MOVQ DI, 0x48(SP)
  checker.go:24985	0x837c49		ff4058			INCL 0x58(AX)
  checker.go:24986	0x837c4c		488b4f38		MOVQ 0x38(DI), CX
  checker.go:24986	0x837c50		4889f0			MOVQ SI, AX
  checker.go:24986	0x837c53		ffd1			CALL CX
  checker.go:24987	0x837c55		8b4c2440		MOVL 0x40(SP), CX
  checker.go:24987	0x837c59		8908			MOVL CX, 0(AX)
  checker.go:24988	0x837c5b		8b4c2444		MOVL 0x44(SP), CX
  checker.go:24988	0x837c5f		81e1ffffc7ff		ANDL $-0x380001, CX
  checker.go:24988	0x837c65		894804			MOVL CX, 0x4(AX)
  checker.go:24989	0x837c68		488b4c2438		MOVQ 0x38(SP), CX
  checker.go:24989	0x837c6d		8b5158			MOVL 0x58(CX), DX
  checker.go:24989	0x837c70		895008			MOVL DX, 0x8(AX)
  checker.go:24990	0x837c73		833d96a86b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:24990	0x837c7a		7507			JNE 0x837c83
  checker.go:24991	0x837c7c		488b542450		MOVQ 0x50(SP), DX
  checker.go:24990	0x837c81		eb21			JMP 0x837ca4
  checker.go:24990	0x837c83		488b5020		MOVQ 0x20(AX), DX
  checker.go:24991	0x837c87		488b5830		MOVQ 0x30(AX), BX
  checker.go:24990	0x837c8b		e8b098c5ff		CALL runtime.gcWriteBarrier4(SB)
  checker.go:24990	0x837c90		49890b			MOVQ CX, 0(R11)
  checker.go:24990	0x837c93		49895308		MOVQ DX, 0x8(R11)
  checker.go:24991	0x837c97		488b542450		MOVQ 0x50(SP), DX
  checker.go:24991	0x837c9c		49895310		MOVQ DX, 0x10(R11)
  checker.go:24991	0x837ca0		49895b18		MOVQ BX, 0x18(R11)
  checker.go:24990	0x837ca4		48894820		MOVQ CX, 0x20(AX)
  checker.go:24991	0x837ca8		488b5c2448		MOVQ 0x48(SP), BX
  checker.go:24991	0x837cad		48895828		MOVQ BX, 0x28(AX)
  checker.go:24991	0x837cb1		48895030		MOVQ DX, 0x30(AX)
  checker.go:24992	0x837cb5		488b8970120000		MOVQ 0x1270(CX), CX
  checker.go:24992	0x837cbc		0f1f4000		NOPL 0(AX)
  checker.go:24992	0x837cc0		4885c9			TESTQ CX, CX
  checker.go:24992	0x837cc3		7475			JE 0x837d3a
  checker.go:24986	0x837cc5		4889442418		MOVQ AX, 0x18(SP)
  checker.go:24992	0x837cca		48894c2420		MOVQ CX, 0x20(SP)
  checker.go:24993	0x837ccf		90			NOPL
  tracer.go:354		0x837cd0		488d05095b5e00		LEAQ 0x5e5b09(IP), AX
  tracer.go:354		0x837cd7		e864c2beff		CALL runtime.newobject(SB)
  tracer.go:354		0x837cdc		833d2da86b0100		CMPL runtime.writeBarrier(SB), $0x0
  tracer.go:354		0x837ce3		7507			JNE 0x837cec
  tracer.go:354		0x837ce5		488b542418		MOVQ 0x18(SP), DX
  tracer.go:354		0x837cea		eb0d			JMP 0x837cf9
  tracer.go:354		0x837cec		e8ef97c5ff		CALL runtime.gcWriteBarrier1(SB)
  tracer.go:354		0x837cf1		488b542418		MOVQ 0x18(SP), DX
  tracer.go:354		0x837cf6		498913			MOVQ DX, 0(R11)
  tracer.go:354		0x837cf9		488910			MOVQ DX, 0(AX)
  tracer.go:354		0x837cfc		488b7220		MOVQ 0x20(DX), SI
  tracer.go:354		0x837d00		833d09a86b0100		CMPL runtime.writeBarrier(SB), $0x0
  tracer.go:354		0x837d07		7408			JE 0x837d11
  tracer.go:354		0x837d09		e8d297c5ff		CALL runtime.gcWriteBarrier1(SB)
  tracer.go:354		0x837d0e		498933			MOVQ SI, 0(R11)
  tracer.go:354		0x837d11		48897008		MOVQ SI, 0x8(AX)
  tracer.go:26		0x837d15		488b542420		MOVQ 0x20(SP), DX
  tracer.go:26		0x837d1a		488b7208		MOVQ 0x8(DX), SI
  tracer.go:26		0x837d1e		488b5210		MOVQ 0x10(DX), DX
  tracer.go:26		0x837d22		488b7620		MOVQ 0x20(SI), SI
  tracer.go:26		0x837d26		488d1d1318d100		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.tracedTypeAdapter,github.com/microsoft/typescript-go/internal/tracing.TracedType(SB), BX
  tracer.go:26		0x837d2d		4889c1			MOVQ AX, CX
  tracer.go:26		0x837d30		4889d0			MOVQ DX, AX
  tracer.go:26		0x837d33		ffd6			CALL SI
  checker.go:24995	0x837d35		488b442418		MOVQ 0x18(SP), AX
  checker.go:24995	0x837d3a		4883c428		ADDQ $0x28, SP
  checker.go:24995	0x837d3e		5d			POPQ BP
  checker.go:24995	0x837d3f		90			NOPL
  checker.go:24995	0x837d40		c3			RET
  checker.go:24984	0x837d41		4889442408		MOVQ AX, 0x8(SP)
  checker.go:24984	0x837d46		895c2410		MOVL BX, 0x10(SP)
  checker.go:24984	0x837d4a		894c2414		MOVL CX, 0x14(SP)
  checker.go:24984	0x837d4e		48897c2418		MOVQ DI, 0x18(SP)
  checker.go:24984	0x837d53		4889742420		MOVQ SI, 0x20(SP)
  checker.go:24984	0x837d58		e8a37cc5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:24984	0x837d5d		488b442408		MOVQ 0x8(SP), AX
  checker.go:24984	0x837d62		8b5c2410		MOVL 0x10(SP), BX
  checker.go:24984	0x837d66		8b4c2414		MOVL 0x14(SP), CX
  checker.go:24984	0x837d6a		488b7c2418		MOVQ 0x18(SP), DI
  checker.go:24984	0x837d6f		488b742420		MOVQ 0x20(SP), SI
  checker.go:24984	0x837d74		e9a7feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).newObjectType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:25044	0x838140		493b6610		CMPQ SP, 0x10(R14)
  checker.go:25044	0x838144		0f866b010000		JBE 0x8382b5
  checker.go:25044	0x83814a		55			PUSHQ BP
  checker.go:25044	0x83814b		4889e5			MOVQ SP, BP
  checker.go:25044	0x83814e		4883ec20		SUBQ $0x20, SP
  checker.go:25047	0x838152		4889442430		MOVQ AX, 0x30(SP)
  checker.go:25047	0x838157		895c2438		MOVL BX, 0x38(SP)
  checker.go:25047	0x83815b		48894c2440		MOVQ CX, 0x40(SP)
  checker.go:25047	0x838160		f7c303000000		TESTL $0x3, BX
  checker.go:25047	0x838166		0f85d7000000		JNE 0x838243
  checker.go:25049	0x83816c		0fbae303		BTL $0x3, BX
  checker.go:25049	0x838170		0f82b8000000		JB 0x83822e
  checker.go:25051	0x838176		0fbae302		BTL $0x2, BX
  checker.go:25051	0x83817a		660f1f440000		NOPW 0(AX)(AX*1)
  checker.go:25051	0x838180		0f8293000000		JB 0x838219
  checker.go:25053	0x838186		0fbae305		BTL $0x5, BX
  checker.go:25053	0x83818a		7278			JB 0x838204
  checker.go:25055	0x83818c		0fbae30a		BTL $0xa, BX
  checker.go:25055	0x838190		725d			JB 0x8381ef
  checker.go:25057	0x838192		0fbae308		BTL $0x8, BX
  checker.go:25057	0x838196		7242			JB 0x8381da
  checker.go:25059	0x838198		0fbae318		BTL $0x18, BX
  checker.go:25059	0x83819c		7227			JB 0x8381c5
  checker.go:25061	0x83819e		0fbae304		BTL $0x4, BX
  checker.go:25061	0x8381a2		0f83f9000000		JAE 0x8382a1
  checker.go:25062	0x8381a8		488d0531126300		LEAQ 0x631231(IP), AX
  checker.go:25062	0x8381af		e88cbdbeff		CALL runtime.newobject(SB)
  checker.go:25062	0x8381b4		488d0d45cacf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.ObjectType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25062	0x8381bb		0f1f440000		NOPL 0(AX)(AX*1)
  checker.go:25062	0x8381c0		e991000000		JMP 0x838256
  checker.go:25060	0x8381c5		488d0574505e00		LEAQ 0x5e5074(IP), AX
  checker.go:25060	0x8381cc		e86fbdbeff		CALL runtime.newobject(SB)
  checker.go:25060	0x8381d1		488d0dd8c9cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.InstantiationExpressionType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25060	0x8381d8		eb7c			JMP 0x838256
  checker.go:25058	0x8381da		488d055fe66000		LEAQ 0x60e65f(IP), AX
  checker.go:25058	0x8381e1		e85abdbeff		CALL runtime.newobject(SB)
  checker.go:25058	0x8381e6		488d0d73c9cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.EvolvingArrayType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25058	0x8381ed		eb67			JMP 0x838256
  checker.go:25056	0x8381ef		488d052a116300		LEAQ 0x63112a(IP), AX
  checker.go:25056	0x8381f6		e845bdbeff		CALL runtime.newobject(SB)
  checker.go:25056	0x8381fb		488d0d0ec9cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.ReverseMappedType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25056	0x838202		eb52			JMP 0x838256
  checker.go:25054	0x838204		488d0515a06700		LEAQ 0x67a015(IP), AX
  checker.go:25054	0x83820b		e830bdbeff		CALL runtime.newobject(SB)
  checker.go:25054	0x838210		488d0da9c8cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.MappedType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25054	0x838217		eb3d			JMP 0x838256
  checker.go:25052	0x838219		488d05e0e96000		LEAQ 0x60e9e0(IP), AX
  checker.go:25052	0x838220		e81bbdbeff		CALL runtime.newobject(SB)
  checker.go:25052	0x838225		488d0d44c8cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.TypeReference,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25052	0x83822c		eb28			JMP 0x838256
  checker.go:25050	0x83822e		488d05cbb96500		LEAQ 0x65b9cb(IP), AX
  checker.go:25050	0x838235		e806bdbeff		CALL runtime.newobject(SB)
  checker.go:25050	0x83823a		488d0d6fc4cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.TupleType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25050	0x838241		eb13			JMP 0x838256
  checker.go:25048	0x838243		488d05f64b6900		LEAQ 0x694bf6(IP), AX
  checker.go:25048	0x83824a		e8f1bcbeff		CALL runtime.newobject(SB)
  checker.go:25048	0x83824f		488d0dcac7cf00		LEAQ go:itab.*github.com/microsoft/typescript-go/internal/checker.InterfaceType,github.com/microsoft/typescript-go/internal/checker.TypeData(SB), CX
  checker.go:25066	0x838256		bb00001000		MOVL $0x100000, BX
  checker.go:25066	0x83825b		4889cf			MOVQ CX, DI
  checker.go:25066	0x83825e		4889c6			MOVQ AX, SI
  checker.go:25066	0x838261		488b442430		MOVQ 0x30(SP), AX
  checker.go:25066	0x838266		8b4c2438		MOVL 0x38(SP), CX
  checker.go:25066	0x83826a		e8b1f9ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).newType(SB)
  checker.go:25067	0x83826f		8400			TESTB AL, 0(AX)
  checker.go:25067	0x838271		833d98a26b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25067	0x838278		7508			JNE 0x838282
  checker.go:25067	0x83827a		488b542440		MOVQ 0x40(SP), DX
  checker.go:25067	0x83827f		90			NOPL
  checker.go:25067	0x838280		eb15			JMP 0x838297
  checker.go:25067	0x838282		488b4810		MOVQ 0x10(AX), CX
  checker.go:25067	0x838286		e87592c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25067	0x83828b		488b542440		MOVQ 0x40(SP), DX
  checker.go:25067	0x838290		498913			MOVQ DX, 0(R11)
  checker.go:25067	0x838293		49894b08		MOVQ CX, 0x8(R11)
  checker.go:25067	0x838297		48895010		MOVQ DX, 0x10(AX)
  checker.go:25068	0x83829b		4883c420		ADDQ $0x20, SP
  checker.go:25068	0x83829f		5d			POPQ BP
  checker.go:25068	0x8382a0		c3			RET
  checker.go:25064	0x8382a1		488d0558645200		LEAQ 0x526458(IP), AX
  checker.go:25064	0x8382a8		488d1db1a2ce00		LEAQ 0xcea2b1(IP), BX
  checker.go:25064	0x8382af		e8ec17c5ff		CALL runtime.gopanic(SB)
  checker.go:25064	0x8382b4		90			NOPL
  checker.go:25044	0x8382b5		4889442408		MOVQ AX, 0x8(SP)
  checker.go:25044	0x8382ba		895c2410		MOVL BX, 0x10(SP)
  checker.go:25044	0x8382be		48894c2418		MOVQ CX, 0x18(SP)
  checker.go:25044	0x8382c3		e83877c5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:25044	0x8382c8		488b442408		MOVQ 0x8(SP), AX
  checker.go:25044	0x8382cd		8b5c2410		MOVL 0x10(SP), BX
  checker.go:25044	0x8382d1		488b4c2418		MOVQ 0x18(SP), CX
  checker.go:25044	0x8382d6		e965feffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).newObjectType(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).setStructuredTypeMembers(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:25126	0x838a00		493b6610		CMPQ SP, 0x10(R14)
  checker.go:25126	0x838a04		0f865a020000		JBE 0x838c64
  checker.go:25126	0x838a0a		55			PUSHQ BP
  checker.go:25126	0x838a0b		4889e5			MOVQ SP, BP
  checker.go:25126	0x838a0e		4883ec40		SUBQ $0x40, SP
  checker.go:25132	0x838a12		4889442468		MOVQ AX, 0x68(SP)
  checker.go:25132	0x838a17		48895c2470		MOVQ BX, 0x70(SP)
  checker.go:25132	0x838a1c		48894c2478		MOVQ CX, 0x78(SP)
  checker.go:25132	0x838a21		4c899c24a8000000	MOVQ R11, 0xa8(SP)
  checker.go:25132	0x838a29		4c898c2498000000	MOVQ R9, 0x98(SP)
  checker.go:25132	0x838a31		4c89842490000000	MOVQ R8, 0x90(SP)
  checker.go:25132	0x838a39		4889b42488000000	MOVQ SI, 0x88(SP)
  checker.go:25132	0x838a41		4c899424a0000000	MOVQ R10, 0xa0(SP)
  checker.go:25132	0x838a49		4889bc2480000000	MOVQ DI, 0x80(SP)
  checker.go:25127	0x838a51		814b0400002000		ORL $0x200000, 0x4(BX)
  types.go:713		0x838a58		488b4b28		MOVQ 0x28(BX), CX
  types.go:713		0x838a5c		488b4330		MOVQ 0x30(BX), AX
  types.go:713		0x838a60		488b4930		MOVQ 0x30(CX), CX
  checker.go:25128	0x838a64		90			NOPL
  types.go:713		0x838a65		ffd1			CALL CX
  checker.go:25129	0x838a67		8400			TESTB AL, 0(AX)
  checker.go:25129	0x838a69		833da09a6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25129	0x838a70		7507			JNE 0x838a79
  checker.go:25130	0x838a72		488b5c2478		MOVQ 0x78(SP), BX
  checker.go:25129	0x838a77		eb1d			JMP 0x838a96
  checker.go:25129	0x838a79		488b5040		MOVQ 0x40(AX), DX
  checker.go:25130	0x838a7d		488b7048		MOVQ 0x48(AX), SI
  checker.go:25129	0x838a81		e89a8ac5ff		CALL runtime.gcWriteBarrier3(SB)
  checker.go:25129	0x838a86		498913			MOVQ DX, 0(R11)
  checker.go:25130	0x838a89		488b5c2478		MOVQ 0x78(SP), BX
  checker.go:25130	0x838a8e		49895b08		MOVQ BX, 0x8(R11)
  checker.go:25130	0x838a92		49897310		MOVQ SI, 0x10(R11)
  types.go:713		0x838a96		4889442438		MOVQ AX, 0x38(SP)
  checker.go:25129	0x838a9b		48c7404000000000	MOVQ $0x0, 0x40(AX)
  checker.go:25130	0x838aa3		48895848		MOVQ BX, 0x48(AX)
  checker.go:25131	0x838aa7		488b542470		MOVQ 0x70(SP), DX
  checker.go:25131	0x838aac		488b4a10		MOVQ 0x10(DX), CX
  checker.go:25131	0x838ab0		488b442468		MOVQ 0x68(SP), AX
  checker.go:25131	0x838ab5		e806affeff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getNamedMembers(SB)
  checker.go:25131	0x838aba		488b542438		MOVQ 0x38(SP), DX
  checker.go:25131	0x838abf		48895a58		MOVQ BX, 0x58(DX)
  checker.go:25131	0x838ac3		48894a60		MOVQ CX, 0x60(DX)
  checker.go:25131	0x838ac7		833d429a6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25131	0x838ace		7410			JE 0x838ae0
  checker.go:25131	0x838ad0		4c8b5250		MOVQ 0x50(DX), R10
  checker.go:25131	0x838ad4		e8278ac5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25131	0x838ad9		498903			MOVQ AX, 0(R11)
  checker.go:25131	0x838adc		4d895308		MOVQ R10, 0x8(R11)
  checker.go:25131	0x838ae0		48894250		MOVQ AX, 0x50(DX)
  checker.go:25132	0x838ae4		488b8c2488000000	MOVQ 0x88(SP), CX
  checker.go:25132	0x838aec		4885c9			TESTQ CX, CX
  checker.go:25132	0x838aef		0f84b4000000		JE 0x838ba9
  checker.go:25133	0x838af5		4c8b8424a0000000	MOVQ 0xa0(SP), R8
  checker.go:25133	0x838afd		0f1f00			NOPL 0(AX)
  checker.go:25133	0x838b00		4d85c0			TESTQ R8, R8
  checker.go:25133	0x838b03		753d			JNE 0x838b42
  checker.go:25136	0x838b05		48894a70		MOVQ CX, 0x70(DX)
  checker.go:25136	0x838b09		48894a78		MOVQ CX, 0x78(DX)
  checker.go:25136	0x838b0d		833dfc996b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25136	0x838b14		750c			JNE 0x838b22
  checker.go:25136	0x838b16		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25136	0x838b1e		6690			NOPW
  checker.go:25136	0x838b20		eb18			JMP 0x838b3a
  checker.go:25136	0x838b22		488b4268		MOVQ 0x68(DX), AX
  checker.go:25136	0x838b26		e8d589c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25136	0x838b2b		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25136	0x838b33		49891b			MOVQ BX, 0(R11)
  checker.go:25136	0x838b36		49894308		MOVQ AX, 0x8(R11)
  checker.go:25136	0x838b3a		48895a68		MOVQ BX, 0x68(DX)
  checker.go:25136	0x838b3e		6690			NOPW
  checker.go:25136	0x838b40		eb5e			JMP 0x838ba0
  checker.go:25134	0x838b42		488d05d70ccf00		LEAQ github.com/microsoft/typescript-go/internal/core..dict.Concatenate[*github.com/microsoft/typescript-go/internal/checker.Signature](SB), AX
  checker.go:25134	0x838b49		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25134	0x838b51		488bbc2490000000	MOVQ 0x90(SP), DI
  checker.go:25134	0x838b59		488bb42498000000	MOVQ 0x98(SP), SI
  checker.go:25134	0x838b61		4c8b8c24a8000000	MOVQ 0xa8(SP), R9
  checker.go:25134	0x838b69		e892b5f4ff		CALL github.com/microsoft/typescript-go/internal/core.Concatenate[go.shape.*uint8](SB)
  checker.go:25134	0x838b6e		488b542438		MOVQ 0x38(SP), DX
  checker.go:25134	0x838b73		48895a70		MOVQ BX, 0x70(DX)
  checker.go:25134	0x838b77		48894a78		MOVQ CX, 0x78(DX)
  checker.go:25134	0x838b7b		833d8e996b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25134	0x838b82		7410			JE 0x838b94
  checker.go:25134	0x838b84		488b4a68		MOVQ 0x68(DX), CX
  checker.go:25134	0x838b88		e87389c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25134	0x838b8d		498903			MOVQ AX, 0(R11)
  checker.go:25134	0x838b90		49894b08		MOVQ CX, 0x8(R11)
  checker.go:25134	0x838b94		48894268		MOVQ AX, 0x68(DX)
  checker.go:25138	0x838b98		488b8c2488000000	MOVQ 0x88(SP), CX
  checker.go:25138	0x838ba0		48898a80000000		MOVQ CX, 0x80(DX)
  checker.go:25138	0x838ba7		eb73			JMP 0x838c1c
  checker.go:25140	0x838ba9		488b8424a0000000	MOVQ 0xa0(SP), AX
  checker.go:25140	0x838bb1		4885c0			TESTQ AX, AX
  checker.go:25140	0x838bb4		7439			JE 0x838bef
  checker.go:25141	0x838bb6		48894270		MOVQ AX, 0x70(DX)
  checker.go:25141	0x838bba		48894278		MOVQ AX, 0x78(DX)
  checker.go:25141	0x838bbe		833d4b996b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25141	0x838bc5		750a			JNE 0x838bd1
  checker.go:25141	0x838bc7		488b8c2498000000	MOVQ 0x98(SP), CX
  checker.go:25141	0x838bcf		eb18			JMP 0x838be9
  checker.go:25141	0x838bd1		488b4268		MOVQ 0x68(DX), AX
  checker.go:25141	0x838bd5		e82689c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25141	0x838bda		488b8c2498000000	MOVQ 0x98(SP), CX
  checker.go:25141	0x838be2		49890b			MOVQ CX, 0(R11)
  checker.go:25141	0x838be5		49894308		MOVQ AX, 0x8(R11)
  checker.go:25141	0x838be9		48894a68		MOVQ CX, 0x68(DX)
  checker.go:25141	0x838bed		eb22			JMP 0x838c11
  checker.go:25143	0x838bef		440f117a70		MOVUPS X15, 0x70(DX)
  checker.go:25143	0x838bf4		833d15996b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25143	0x838bfb		740c			JE 0x838c09
  checker.go:25143	0x838bfd		488b4268		MOVQ 0x68(DX), AX
  checker.go:25143	0x838c01		e8da88c5ff		CALL runtime.gcWriteBarrier1(SB)
  checker.go:25143	0x838c06		498903			MOVQ AX, 0(R11)
  checker.go:25143	0x838c09		48c7426800000000	MOVQ $0x0, 0x68(DX)
  checker.go:25145	0x838c11		48c7828000000000000000	MOVQ $0x0, 0x80(DX)
  checker.go:25147	0x838c1c		488b442458		MOVQ 0x58(SP), AX
  checker.go:25147	0x838c21		48898290000000		MOVQ AX, 0x90(DX)
  checker.go:25147	0x838c28		48898298000000		MOVQ AX, 0x98(DX)
  checker.go:25147	0x838c2f		833dda986b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25147	0x838c36		7507			JNE 0x838c3f
  checker.go:25147	0x838c38		488b4c2450		MOVQ 0x50(SP), CX
  checker.go:25147	0x838c3d		eb18			JMP 0x838c57
  checker.go:25147	0x838c3f		488b8288000000		MOVQ 0x88(DX), AX
  checker.go:25147	0x838c46		e8b588c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25147	0x838c4b		488b4c2450		MOVQ 0x50(SP), CX
  checker.go:25147	0x838c50		49890b			MOVQ CX, 0(R11)
  checker.go:25147	0x838c53		49894308		MOVQ AX, 0x8(R11)
  checker.go:25147	0x838c57		48898a88000000		MOVQ CX, 0x88(DX)
  checker.go:25148	0x838c5e		4883c440		ADDQ $0x40, SP
  checker.go:25148	0x838c62		5d			POPQ BP
  checker.go:25148	0x838c63		c3			RET
  checker.go:25126	0x838c64		4889442420		MOVQ AX, 0x20(SP)
  checker.go:25126	0x838c69		48895c2428		MOVQ BX, 0x28(SP)
  checker.go:25126	0x838c6e		48894c2430		MOVQ CX, 0x30(SP)
  checker.go:25126	0x838c73		48897c2438		MOVQ DI, 0x38(SP)
  checker.go:25126	0x838c78		4889742440		MOVQ SI, 0x40(SP)
  checker.go:25126	0x838c7d		4c89442448		MOVQ R8, 0x48(SP)
  checker.go:25126	0x838c82		4c894c2450		MOVQ R9, 0x50(SP)
  checker.go:25126	0x838c87		4c89542458		MOVQ R10, 0x58(SP)
  checker.go:25126	0x838c8c		4c895c2460		MOVQ R11, 0x60(SP)
  checker.go:25126	0x838c91		e86a6dc5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:25126	0x838c96		488b442420		MOVQ 0x20(SP), AX
  checker.go:25126	0x838c9b		488b5c2428		MOVQ 0x28(SP), BX
  checker.go:25126	0x838ca0		488b4c2430		MOVQ 0x30(SP), CX
  checker.go:25126	0x838ca5		488b7c2438		MOVQ 0x38(SP), DI
  checker.go:25126	0x838caa		488b742440		MOVQ 0x40(SP), SI
  checker.go:25126	0x838caf		4c8b442448		MOVQ 0x48(SP), R8
  checker.go:25126	0x838cb4		4c8b4c2450		MOVQ 0x50(SP), R9
  checker.go:25126	0x838cb9		4c8b542458		MOVQ 0x58(SP), R10
  checker.go:25126	0x838cbe		4c8b5c2460		MOVQ 0x60(SP), R11
  checker.go:25126	0x838cc3		e938fdffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).setStructuredTypeMembers(SB)
