TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).typeResolutionHasProperty(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:18705	0x80e1e0		493b6610		CMPQ SP, 0x10(R14)
  checker.go:18705	0x80e1e4		0f8688030000		JBE 0x80e572
  checker.go:18705	0x80e1ea		55			PUSHQ BP
  checker.go:18705	0x80e1eb		4889e5			MOVQ SP, BP
  checker.go:18705	0x80e1ee		4883ec18		SUBQ $0x18, SP
  checker.go:18706	0x80e1f2		48635310		MOVSXD 0x10(BX), DX
  checker.go:18706	0x80e1f6		660f1f840000000000	NOPW 0(AX)(AX*1)
  checker.go:18706	0x80e1ff		90			NOPL
  checker.go:18706	0x80e200		4883fa09		CMPQ DX, $0x9
  checker.go:18706	0x80e204		0f8754030000		JA 0x80e55e
  checker.go:18706	0x80e20a		488d0d2f9ed200		LEAQ 0xd29e2f(IP), CX
  checker.go:18706	0x80e211		ff24d1			JMP 0(CX)(DX*8)
  checker.go:18708	0x80e214		8400			TESTB AL, 0(AX)
  checker.go:18708	0x80e216		488b13			MOVQ 0(BX), DX
  checker.go:18708	0x80e219		488d35e08e5c00		LEAQ 0x5c8ee0(IP), SI
  checker.go:18708	0x80e220		4839f2			CMPQ DX, SI
  checker.go:18708	0x80e223		0f8523030000		JNE 0x80e54c
  checker.go:18708	0x80e229		4805f8080000		ADDQ $0x8f8, AX
  checker.go:18708	0x80e22f		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18708	0x80e233		488d1da632d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX
  checker.go:18708	0x80e23a		e8e1aa0f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)
  checker.go:18708	0x80e23f		48833800		CMPQ 0(AX), $0x0
  checker.go:18708	0x80e243		0f95c0			SETNE AL
  checker.go:18708	0x80e246		4883c418		ADDQ $0x18, SP
  checker.go:18708	0x80e24a		5d			POPQ BP
  checker.go:18708	0x80e24b		c3			RET
  checker.go:18716	0x80e24c		488b03			MOVQ 0(BX), AX
  checker.go:18716	0x80e24f		488d150ad76d00		LEAQ 0x6dd70a(IP), DX
  checker.go:18716	0x80e256		4839d0			CMPQ AX, DX
  checker.go:18716	0x80e259		0f85de020000		JNE 0x80e53d
  checker.go:18716	0x80e25f		488b4b08		MOVQ 0x8(BX), CX
  type_data.go:157	0x80e263		0fb6510c		MOVZX 0xc(CX), DX
  type_data.go:158	0x80e267		84d2			TESTL DL, DL
  type_data.go:158	0x80e269		0f84bb020000		JE 0x80e52a
  type_data.go:161	0x80e26f		83c2f7			ADDL $-0x9, DX
  type_data.go:161	0x80e272		80fa01			CMPL DL, $0x1
  type_data.go:161	0x80e275		7706			JA 0x80e27d
  type_data.go:162	0x80e277		488b4928		MOVQ 0x28(CX), CX
  checker.go:18716	0x80e27b		eb02			JMP 0x80e27f
  checker.go:18716	0x80e27d		31c9			XORL CX, CX
  checker.go:18716	0x80e27f		4883b90801000000	CMPQ 0x108(CX), $0x0
  checker.go:18716	0x80e287		0f95c0			SETNE AL
  checker.go:18716	0x80e28a		4883c418		ADDQ $0x18, SP
  checker.go:18716	0x80e28e		5d			POPQ BP
  checker.go:18716	0x80e28f		c3			RET
  checker.go:18710	0x80e290		8400			TESTB AL, 0(AX)
  checker.go:18710	0x80e292		488b13			MOVQ 0(BX), DX
  checker.go:18710	0x80e295		488d35648e5c00		LEAQ 0x5c8e64(IP), SI
  checker.go:18710	0x80e29c		0f1f4000		NOPL 0(AX)
  checker.go:18710	0x80e2a0		4839f2			CMPQ DX, SI
  checker.go:18710	0x80e2a3		0f856f020000		JNE 0x80e518
  checker.go:18710	0x80e2a9		4805f8090000		ADDQ $0x9f8, AX
  checker.go:18710	0x80e2af		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18710	0x80e2b3		488d1d262cd300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.TypeAliasLinks](SB), BX
  checker.go:18710	0x80e2ba		e861bb0f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.07b4bb953fce386053033c51a7b2f9f24c1586764f3e1f7952f8941b6d2d7f9e]).Get(SB)
  checker.go:18710	0x80e2bf		48833800		CMPQ 0(AX), $0x0
  checker.go:18710	0x80e2c3		0f95c0			SETNE AL
  checker.go:18710	0x80e2c6		4883c418		ADDQ $0x18, SP
  checker.go:18710	0x80e2ca		5d			POPQ BP
  checker.go:18710	0x80e2cb		c3			RET
  checker.go:18718	0x80e2cc		488b03			MOVQ 0(BX), AX
  checker.go:18718	0x80e2cf		488d15ea596700		LEAQ 0x6759ea(IP), DX
  checker.go:18718	0x80e2d6		4839d0			CMPQ AX, DX
  checker.go:18718	0x80e2d9		0f852a020000		JNE 0x80e509
  checker.go:18718	0x80e2df		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18718	0x80e2e3		4883795000		CMPQ 0x50(CX), $0x0
  checker.go:18718	0x80e2e8		0f95c0			SETNE AL
  checker.go:18718	0x80e2eb		4883c418		ADDQ $0x18, SP
  checker.go:18718	0x80e2ef		5d			POPQ BP
  checker.go:18718	0x80e2f0		c3			RET
  checker.go:18720	0x80e2f1		488b03			MOVQ 0(BX), AX
  checker.go:18720	0x80e2f4		488d1565d66d00		LEAQ 0x6dd665(IP), DX
  checker.go:18720	0x80e2fb		0f1f440000		NOPL 0(AX)(AX*1)
  checker.go:18720	0x80e300		4839d0			CMPQ AX, DX
  checker.go:18720	0x80e303		0f85f1010000		JNE 0x80e4fa
  checker.go:18720	0x80e309		488b4b08		MOVQ 0x8(BX), CX
  type_data.go:117	0x80e30d		0fb6510c		MOVZX 0xc(CX), DX
  type_data.go:118	0x80e311		84d2			TESTL DL, DL
  type_data.go:118	0x80e313		0f84ce010000		JE 0x80e4e7
  type_data.go:121	0x80e319		83c2fb			ADDL $-0x5, DX
  type_data.go:121	0x80e31c		0f1f4000		NOPL 0(AX)
  type_data.go:121	0x80e320		80fa13			CMPL DL, $0x13
  type_data.go:121	0x80e323		7706			JA 0x80e32b
  type_data.go:122	0x80e325		488b4928		MOVQ 0x28(CX), CX
  checker.go:18720	0x80e329		eb02			JMP 0x80e32d
  checker.go:18720	0x80e32b		31c9			XORL CX, CX
  checker.go:18720	0x80e32d		4883793000		CMPQ 0x30(CX), $0x0
  checker.go:18720	0x80e332		0f95c0			SETNE AL
  checker.go:18720	0x80e335		4883c418		ADDQ $0x18, SP
  checker.go:18720	0x80e339		5d			POPQ BP
  checker.go:18720	0x80e33a		c3			RET
  checker.go:18712	0x80e33b		488b03			MOVQ 0(BX), AX
  checker.go:18712	0x80e33e		488d151bd66d00		LEAQ 0x6dd61b(IP), DX
  checker.go:18712	0x80e345		4839d0			CMPQ AX, DX
  checker.go:18712	0x80e348		0f858a010000		JNE 0x80e4d8
  checker.go:18712	0x80e34e		488b4b08		MOVQ 0x8(BX), CX
  type_data.go:147	0x80e352		0fb6510c		MOVZX 0xc(CX), DX
  type_data.go:148	0x80e356		84d2			TESTL DL, DL
  type_data.go:148	0x80e358		0f8467010000		JE 0x80e4c5
  type_data.go:151	0x80e35e		83c2f8			ADDL $-0x8, DX
  type_data.go:151	0x80e361		80fa02			CMPL DL, $0x2
  type_data.go:151	0x80e364		7706			JA 0x80e36c
  type_data.go:152	0x80e366		488b4928		MOVQ 0x28(CX), CX
  checker.go:18712	0x80e36a		eb02			JMP 0x80e36e
  checker.go:18712	0x80e36c		31c9			XORL CX, CX
  checker.go:18712	0x80e36e		4883b9c000000000	CMPQ 0xc0(CX), $0x0
  checker.go:18712	0x80e376		0f95c0			SETNE AL
  checker.go:18712	0x80e379		4883c418		ADDQ $0x18, SP
  checker.go:18712	0x80e37d		5d			POPQ BP
  checker.go:18712	0x80e37e		c3			RET
  checker.go:18714	0x80e37f		488b03			MOVQ 0(BX), AX
  checker.go:18714	0x80e382		488d15d7d56d00		LEAQ 0x6dd5d7(IP), DX
  checker.go:18714	0x80e389		4839d0			CMPQ AX, DX
  checker.go:18714	0x80e38c		0f8520010000		JNE 0x80e4b2
  checker.go:18714	0x80e392		488b4b08		MOVQ 0x8(BX), CX
  type_data.go:157	0x80e396		0fb6510c		MOVZX 0xc(CX), DX
  type_data.go:157	0x80e39a		660f1f440000		NOPW 0(AX)(AX*1)
  type_data.go:158	0x80e3a0		84d2			TESTL DL, DL
  type_data.go:158	0x80e3a2		0f84f7000000		JE 0x80e49f
  type_data.go:161	0x80e3a8		83c2f7			ADDL $-0x9, DX
  type_data.go:161	0x80e3ab		80fa01			CMPL DL, $0x1
  type_data.go:161	0x80e3ae		7706			JA 0x80e3b6
  type_data.go:162	0x80e3b0		488b4928		MOVQ 0x28(CX), CX
  checker.go:18714	0x80e3b4		eb02			JMP 0x80e3b8
  checker.go:18714	0x80e3b6		31c9			XORL CX, CX
  checker.go:18714	0x80e3b8		0fb68100010000		MOVZX 0x100(CX), AX
  checker.go:18714	0x80e3bf		4883c418		ADDQ $0x18, SP
  checker.go:18714	0x80e3c3		5d			POPQ BP
  checker.go:18714	0x80e3c4		c3			RET
  checker.go:18724	0x80e3c5		8400			TESTB AL, 0(AX)
  checker.go:18724	0x80e3c7		488b13			MOVQ 0(BX), DX
  checker.go:18724	0x80e3ca		488d352f8d5c00		LEAQ 0x5c8d2f(IP), SI
  checker.go:18724	0x80e3d1		4839f2			CMPQ DX, SI
  checker.go:18724	0x80e3d4		0f85b3000000		JNE 0x80e48d
  checker.go:18724	0x80e3da		4805f8080000		ADDQ $0x8f8, AX
  checker.go:18724	0x80e3e0		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18724	0x80e3e4		488d1df530d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.ValueSymbolLinks](SB), BX
  checker.go:18724	0x80e3eb		e830a90f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)
  checker.go:18724	0x80e3f0		4883780800		CMPQ 0x8(AX), $0x0
  checker.go:18724	0x80e3f5		0f95c0			SETNE AL
  checker.go:18724	0x80e3f8		4883c418		ADDQ $0x18, SP
  checker.go:18724	0x80e3fc		5d			POPQ BP
  checker.go:18724	0x80e3fd		c3			RET
  checker.go:18722	0x80e3fe		8400			TESTB AL, 0(AX)
  checker.go:18722	0x80e400		488b13			MOVQ 0(BX), DX
  checker.go:18722	0x80e403		488d3556637200		LEAQ 0x726356(IP), SI
  checker.go:18722	0x80e40a		4839f2			CMPQ DX, SI
  checker.go:18722	0x80e40d		756c			JNE 0x80e47b
  checker.go:18722	0x80e40f		4805b8070000		ADDQ $0x7b8, AX
  checker.go:18722	0x80e415		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18722	0x80e419		488d1d4038d300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Node,github.com/microsoft/typescript-go/internal/checker.NodeLinks](SB), BX
  checker.go:18722	0x80e420		e8fb910f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Node,go.shape.struct { github.com/microsoft/typescript-go/internal/checker.flags github.com/microsoft/typescript-go/internal/checker.NodeCheckFlags; github.com/microsoft/typescript-go/internal/checker.declarationRequiresScopeChange github.com/microsoft/typescript-go/internal/core.Tristate; github.com/microsoft/typescript-go/internal/checker.hasReportedStatementInAmbientContext bool }]).Get(SB)
  checker.go:18722	0x80e425		8b10			MOVL 0(AX), DX
  checker.go:18722	0x80e427		0fbae219		BTL $0x19, DX
  checker.go:18722	0x80e42b		0f92c0			SETB AL
  checker.go:18722	0x80e42e		4883c418		ADDQ $0x18, SP
  checker.go:18722	0x80e432		5d			POPQ BP
  checker.go:18722	0x80e433		c3			RET
  checker.go:18726	0x80e434		8400			TESTB AL, 0(AX)
  checker.go:18726	0x80e436		488b13			MOVQ 0(BX), DX
  checker.go:18726	0x80e439		488d35c08c5c00		LEAQ 0x5c8cc0(IP), SI
  checker.go:18726	0x80e440		4839f2			CMPQ DX, SI
  checker.go:18726	0x80e443		7524			JNE 0x80e469
  checker.go:18726	0x80e445		480558090000		ADDQ $0x958, AX
  checker.go:18726	0x80e44b		488b4b08		MOVQ 0x8(BX), CX
  checker.go:18726	0x80e44f		488d1d4a2ed300		LEAQ github.com/microsoft/typescript-go/internal/core..dict.LinkStore[*github.com/microsoft/typescript-go/internal/ast.Symbol,github.com/microsoft/typescript-go/internal/checker.AliasSymbolLinks](SB), BX
  checker.go:18726	0x80e456		e825af0f00		CALL github.com/microsoft/typescript-go/internal/core.(*LinkStore[go.shape.*github.com/microsoft/typescript-go/internal/ast.Symbol,go.shape.struct { github.com/microsoft/typescript-go/internal/checker.immediateTarget *github.com/microsoft/typescript-go/internal/ast.Symbol; github.com/microsoft/typescript-go/internal/checker.aliasTarget *github.com/microsoft/typescript-go/internal/ast.Symbol; github.com/microsoft/typescript-go/internal/checker.referenced bool; github.com/microsoft/typescript-go/internal/checker.typeOnlyDeclaration *github.com/microsoft/typescript-go/internal/ast.Node }]).Get(SB)
  checker.go:18726	0x80e45b		4883780800		CMPQ 0x8(AX), $0x0
  checker.go:18726	0x80e460		0f95c0			SETNE AL
  checker.go:18726	0x80e463		4883c418		ADDQ $0x18, SP
  checker.go:18726	0x80e467		5d			POPQ BP
  checker.go:18726	0x80e468		c3			RET
  checker.go:18726	0x80e469		4889d0			MOVQ DX, AX
  checker.go:18726	0x80e46c		4889f3			MOVQ SI, BX
  checker.go:18726	0x80e46f		488d0dead55900		LEAQ 0x59d5ea(IP), CX
  checker.go:18726	0x80e476		e8251ac1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18722	0x80e47b		4889d0			MOVQ DX, AX
  checker.go:18722	0x80e47e		4889f3			MOVQ SI, BX
  checker.go:18722	0x80e481		488d0dd8d55900		LEAQ 0x59d5d8(IP), CX
  checker.go:18722	0x80e488		e8131ac1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18724	0x80e48d		4889d0			MOVQ DX, AX
  checker.go:18724	0x80e490		4889f3			MOVQ SI, BX
  checker.go:18724	0x80e493		488d0dc6d55900		LEAQ 0x59d5c6(IP), CX
  checker.go:18724	0x80e49a		e8011ac1ff		CALL runtime.panicdottypeE(SB)
  type_data.go:159	0x80e49f		488d05ba415500		LEAQ 0x5541ba(IP), AX
  type_data.go:159	0x80e4a6		488d1d036dd100		LEAQ 0xd16d03(IP), BX
  type_data.go:159	0x80e4ad		e8eeb5c7ff		CALL runtime.gopanic(SB)
  checker.go:18714	0x80e4b2		4889d3			MOVQ DX, BX
  checker.go:18714	0x80e4b5		488d0da4d55900		LEAQ 0x59d5a4(IP), CX
  checker.go:18714	0x80e4bc		0f1f4000		NOPL 0(AX)
  checker.go:18714	0x80e4c0		e8db19c1ff		CALL runtime.panicdottypeE(SB)
  type_data.go:149	0x80e4c5		488d0594415500		LEAQ 0x554194(IP), AX
  type_data.go:149	0x80e4cc		488d1ddd6cd100		LEAQ 0xd16cdd(IP), BX
  type_data.go:149	0x80e4d3		e8c8b5c7ff		CALL runtime.gopanic(SB)
  checker.go:18712	0x80e4d8		4889d3			MOVQ DX, BX
  checker.go:18712	0x80e4db		488d0d7ed55900		LEAQ 0x59d57e(IP), CX
  checker.go:18712	0x80e4e2		e8b919c1ff		CALL runtime.panicdottypeE(SB)
  type_data.go:119	0x80e4e7		488d0572415500		LEAQ 0x554172(IP), AX
  type_data.go:119	0x80e4ee		488d1dbb6cd100		LEAQ 0xd16cbb(IP), BX
  type_data.go:119	0x80e4f5		e8a6b5c7ff		CALL runtime.gopanic(SB)
  checker.go:18720	0x80e4fa		4889d3			MOVQ DX, BX
  checker.go:18720	0x80e4fd		488d0d5cd55900		LEAQ 0x59d55c(IP), CX
  checker.go:18720	0x80e504		e89719c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18718	0x80e509		4889d3			MOVQ DX, BX
  checker.go:18718	0x80e50c		488d0d4dd55900		LEAQ 0x59d54d(IP), CX
  checker.go:18718	0x80e513		e88819c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18710	0x80e518		4889d0			MOVQ DX, AX
  checker.go:18710	0x80e51b		4889f3			MOVQ SI, BX
  checker.go:18710	0x80e51e		488d0d3bd55900		LEAQ 0x59d53b(IP), CX
  checker.go:18710	0x80e525		e87619c1ff		CALL runtime.panicdottypeE(SB)
  type_data.go:159	0x80e52a		488d052f415500		LEAQ 0x55412f(IP), AX
  type_data.go:159	0x80e531		488d1d786cd100		LEAQ 0xd16c78(IP), BX
  type_data.go:159	0x80e538		e863b5c7ff		CALL runtime.gopanic(SB)
  checker.go:18716	0x80e53d		4889d3			MOVQ DX, BX
  checker.go:18716	0x80e540		488d0d19d55900		LEAQ 0x59d519(IP), CX
  checker.go:18716	0x80e547		e85419c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18708	0x80e54c		4889d0			MOVQ DX, AX
  checker.go:18708	0x80e54f		4889f3			MOVQ SI, BX
  checker.go:18708	0x80e552		488d0d07d55900		LEAQ 0x59d507(IP), CX
  checker.go:18708	0x80e559		e84219c1ff		CALL runtime.panicdottypeE(SB)
  checker.go:18728	0x80e55e		488d05fb405500		LEAQ 0x5540fb(IP), AX
  checker.go:18728	0x80e565		488d1df47dd100		LEAQ 0xd17df4(IP), BX
  checker.go:18728	0x80e56c		e82fb5c7ff		CALL runtime.gopanic(SB)
  checker.go:18728	0x80e571		90			NOPL
  checker.go:18705	0x80e572		4889442408		MOVQ AX, 0x8(SP)
  checker.go:18705	0x80e577		48895c2410		MOVQ BX, 0x10(SP)
  checker.go:18705	0x80e57c		0f1f4000		NOPL 0(AX)
  checker.go:18705	0x80e580		e87b14c8ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:18705	0x80e585		488b442408		MOVQ 0x8(SP), AX
  checker.go:18705	0x80e58a		488b5c2410		MOVQ 0x10(SP), BX
  checker.go:18705	0x80e58f		e94cfcffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).typeResolutionHasProperty(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).isReducibleIntersection(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:24919	0x838fa0		493b6610		CMPQ SP, 0x10(R14)
  checker.go:24919	0x838fa4		0f86a7000000		JBE 0x839051
  checker.go:24919	0x838faa		55			PUSHQ BP
  checker.go:24919	0x838fab		4889e5			MOVQ SP, BP
  checker.go:24919	0x838fae		4883ec28		SUBQ $0x28, SP
  checker.go:24920	0x838fb2		90			NOPL
  type_data.go:85	0x838fb3		90			NOPL
  type_data.go:38	0x838fb4		807b0c11		CMPB 0xc(BX), $0x11
  type_data.go:38	0x838fb8		0f857f000000		JNE 0x83903d
  type_data.go:86	0x838fbe		488b5328		MOVQ 0x28(BX), DX
  type_data.go:86	0x838fc2		4889542420		MOVQ DX, 0x20(SP)
  checker.go:24921	0x838fc7		4883bae800000000	CMPQ 0xe8(DX), $0x0
  checker.go:24921	0x838fcf		754b			JNE 0x83901c
  type_data.go:38	0x838fd1		4889442438		MOVQ AX, 0x38(SP)
  checker.go:24922	0x838fd6		488b88380c0000		MOVQ 0xc38(AX), CX
  checker.go:22039	0x838fdd		31ff			XORL DI, DI
  checker.go:22039	0x838fdf		90			NOPL
  checker.go:22039	0x838fe0		e85bc9feff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).instantiateTypeWithAlias(SB)
  checker.go:24922	0x838fe5		833d24056c0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:24922	0x838fec		7507			JNE 0x838ff5
  checker.go:24922	0x838fee		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24922	0x838ff3		eb18			JMP 0x83900d
  checker.go:24922	0x838ff5		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24922	0x838ffa		488b91e8000000		MOVQ 0xe8(CX), DX
  checker.go:24922	0x839001		e8fa84c5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:24922	0x839006		498903			MOVQ AX, 0(R11)
  checker.go:24922	0x839009		49895308		MOVQ DX, 0x8(R11)
  checker.go:24922	0x83900d		488981e8000000		MOVQ AX, 0xe8(CX)
  checker.go:24924	0x839014		488b442438		MOVQ 0x38(SP), AX
  checker.go:24924	0x839019		4889ca			MOVQ CX, DX
  checker.go:24924	0x83901c		488b9ae8000000		MOVQ 0xe8(DX), BX
  checker.go:24924	0x839023		e8f8a7feff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getReducedType(SB)
  checker.go:24924	0x839028		488b4c2420		MOVQ 0x20(SP), CX
  checker.go:24924	0x83902d		483981e8000000		CMPQ 0xe8(CX), AX
  checker.go:24924	0x839034		0f95c0			SETNE AL
  checker.go:24924	0x839037		4883c428		ADDQ $0x28, SP
  checker.go:24924	0x83903b		5d			POPQ BP
  checker.go:24924	0x83903c		c3			RET
  type_data.go:39	0x83903d		488d051c965200		LEAQ 0x52961c(IP), AX
  type_data.go:39	0x839044		488d1d55c1ce00		LEAQ 0xcec155(IP), BX
  type_data.go:39	0x83904b		e8500ac5ff		CALL runtime.gopanic(SB)
  type_data.go:39	0x839050		90			NOPL
  checker.go:24919	0x839051		4889442408		MOVQ AX, 0x8(SP)
  checker.go:24919	0x839056		48895c2410		MOVQ BX, 0x10(SP)
  checker.go:24919	0x83905b		0f1f440000		NOPL 0(AX)(AX*1)
  checker.go:24919	0x839060		e89b69c5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:24919	0x839065		488b442408		MOVQ 0x8(SP), AX
  checker.go:24919	0x83906a		488b5c2410		MOVQ 0x10(SP), BX
  checker.go:24919	0x83906f		e92cffffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).isReducibleIntersection(SB)

TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).setStructuredTypeMembers(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:25140	0x83a640		493b6610		CMPQ SP, 0x10(R14)
  checker.go:25140	0x83a644		0f866b020000		JBE 0x83a8b5
  checker.go:25140	0x83a64a		55			PUSHQ BP
  checker.go:25140	0x83a64b		4889e5			MOVQ SP, BP
  checker.go:25140	0x83a64e		4883ec40		SUBQ $0x40, SP
  checker.go:25140	0x83a652		4889bc2480000000	MOVQ DI, 0x80(SP)
  checker.go:25140	0x83a65a		4c898c2498000000	MOVQ R9, 0x98(SP)
  checker.go:25141	0x83a662		814b0400002000		ORL $0x200000, 0x4(BX)
  type_data.go:127	0x83a669		0fb6530c		MOVZX 0xc(BX), DX
  type_data.go:128	0x83a66d		84d2			TESTL DL, DL
  type_data.go:128	0x83a66f		0f842c020000		JE 0x83a8a1
  type_data.go:131	0x83a675		83c2fa			ADDL $-0x6, DX
  type_data.go:131	0x83a678		80fa0b			CMPL DL, $0xb
  type_data.go:131	0x83a67b		7706			JA 0x83a683
  type_data.go:132	0x83a67d		488b5328		MOVQ 0x28(BX), DX
  checker.go:25142	0x83a681		eb02			JMP 0x83a685
  checker.go:25142	0x83a683		31d2			XORL DX, DX
  type_data.go:128	0x83a685		4c899c24a8000000	MOVQ R11, 0xa8(SP)
  type_data.go:128	0x83a68d		4c898c2498000000	MOVQ R9, 0x98(SP)
  type_data.go:128	0x83a695		4c89842490000000	MOVQ R8, 0x90(SP)
  type_data.go:128	0x83a69d		4889b42488000000	MOVQ SI, 0x88(SP)
  type_data.go:128	0x83a6a5		4c899424a0000000	MOVQ R10, 0xa0(SP)
  type_data.go:128	0x83a6ad		4889bc2480000000	MOVQ DI, 0x80(SP)
  checker.go:25143	0x83a6b5		8402			TESTB AL, 0(DX)
  checker.go:25143	0x83a6b7		833d52ee6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25143	0x83a6be		6690			NOPW
  checker.go:25143	0x83a6c0		7418			JE 0x83a6da
  checker.go:25143	0x83a6c2		4c8b6238		MOVQ 0x38(DX), R12
  checker.go:25144	0x83a6c6		4c8b6a40		MOVQ 0x40(DX), R13
  checker.go:25143	0x83a6ca		e8516ec5ff		CALL runtime.gcWriteBarrier3(SB)
  checker.go:25143	0x83a6cf		4d8923			MOVQ R12, 0(R11)
  checker.go:25144	0x83a6d2		49894b08		MOVQ CX, 0x8(R11)
  checker.go:25144	0x83a6d6		4d896b10		MOVQ R13, 0x10(R11)
  checker.go:25142	0x83a6da		4889542438		MOVQ DX, 0x38(SP)
  checker.go:25143	0x83a6df		48c7423800000000	MOVQ $0x0, 0x38(DX)
  checker.go:25144	0x83a6e7		48894a40		MOVQ CX, 0x40(DX)
  checker.go:25145	0x83a6eb		488b5310		MOVQ 0x10(BX), DX
  checker.go:25145	0x83a6ef		4889cb			MOVQ CX, BX
  checker.go:25145	0x83a6f2		4889d1			MOVQ DX, CX
  checker.go:25145	0x83a6f5		e8e6abfeff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getNamedMembers(SB)
  checker.go:25145	0x83a6fa		488b542438		MOVQ 0x38(SP), DX
  checker.go:25145	0x83a6ff		48895a50		MOVQ BX, 0x50(DX)
  checker.go:25145	0x83a703		48894a58		MOVQ CX, 0x58(DX)
  checker.go:25145	0x83a707		833d02ee6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25145	0x83a70e		7410			JE 0x83a720
  checker.go:25145	0x83a710		4c8b5248		MOVQ 0x48(DX), R10
  checker.go:25145	0x83a714		e8e76dc5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25145	0x83a719		498903			MOVQ AX, 0(R11)
  checker.go:25145	0x83a71c		4d895308		MOVQ R10, 0x8(R11)
  checker.go:25145	0x83a720		48894248		MOVQ AX, 0x48(DX)
  checker.go:25146	0x83a724		488b8c2488000000	MOVQ 0x88(SP), CX
  checker.go:25146	0x83a72c		4885c9			TESTQ CX, CX
  checker.go:25146	0x83a72f		0f84b1000000		JE 0x83a7e6
  checker.go:25147	0x83a735		4c8b8424a0000000	MOVQ 0xa0(SP), R8
  checker.go:25147	0x83a73d		0f1f00			NOPL 0(AX)
  checker.go:25147	0x83a740		4d85c0			TESTQ R8, R8
  checker.go:25147	0x83a743		753d			JNE 0x83a782
  checker.go:25150	0x83a745		48894a68		MOVQ CX, 0x68(DX)
  checker.go:25150	0x83a749		48894a70		MOVQ CX, 0x70(DX)
  checker.go:25150	0x83a74d		833dbced6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25150	0x83a754		750c			JNE 0x83a762
  checker.go:25150	0x83a756		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25150	0x83a75e		6690			NOPW
  checker.go:25150	0x83a760		eb18			JMP 0x83a77a
  checker.go:25150	0x83a762		488b4260		MOVQ 0x60(DX), AX
  checker.go:25150	0x83a766		e8956dc5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25150	0x83a76b		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25150	0x83a773		49891b			MOVQ BX, 0(R11)
  checker.go:25150	0x83a776		49894308		MOVQ AX, 0x8(R11)
  checker.go:25150	0x83a77a		48895a60		MOVQ BX, 0x60(DX)
  checker.go:25150	0x83a77e		6690			NOPW
  checker.go:25150	0x83a780		eb5e			JMP 0x83a7e0
  checker.go:25148	0x83a782		488d05172fcf00		LEAQ github.com/microsoft/typescript-go/internal/core..dict.Concatenate[*github.com/microsoft/typescript-go/internal/checker.Signature](SB), AX
  checker.go:25148	0x83a789		488b9c2480000000	MOVQ 0x80(SP), BX
  checker.go:25148	0x83a791		488bbc2490000000	MOVQ 0x90(SP), DI
  checker.go:25148	0x83a799		488bb42498000000	MOVQ 0x98(SP), SI
  checker.go:25148	0x83a7a1		4c8b8c24a8000000	MOVQ 0xa8(SP), R9
  checker.go:25148	0x83a7a9		e85299f4ff		CALL github.com/microsoft/typescript-go/internal/core.Concatenate[go.shape.*uint8](SB)
  checker.go:25148	0x83a7ae		488b542438		MOVQ 0x38(SP), DX
  checker.go:25148	0x83a7b3		48895a68		MOVQ BX, 0x68(DX)
  checker.go:25148	0x83a7b7		48894a70		MOVQ CX, 0x70(DX)
  checker.go:25148	0x83a7bb		833d4eed6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25148	0x83a7c2		7410			JE 0x83a7d4
  checker.go:25148	0x83a7c4		488b4a60		MOVQ 0x60(DX), CX
  checker.go:25148	0x83a7c8		e8336dc5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25148	0x83a7cd		498903			MOVQ AX, 0(R11)
  checker.go:25148	0x83a7d0		49894b08		MOVQ CX, 0x8(R11)
  checker.go:25148	0x83a7d4		48894260		MOVQ AX, 0x60(DX)
  checker.go:25152	0x83a7d8		488b8c2488000000	MOVQ 0x88(SP), CX
  checker.go:25152	0x83a7e0		48894a78		MOVQ CX, 0x78(DX)
  checker.go:25152	0x83a7e4		eb72			JMP 0x83a858
  checker.go:25154	0x83a7e6		488b8424a0000000	MOVQ 0xa0(SP), AX
  checker.go:25154	0x83a7ee		4885c0			TESTQ AX, AX
  checker.go:25154	0x83a7f1		7439			JE 0x83a82c
  checker.go:25155	0x83a7f3		48894268		MOVQ AX, 0x68(DX)
  checker.go:25155	0x83a7f7		48894270		MOVQ AX, 0x70(DX)
  checker.go:25155	0x83a7fb		833d0eed6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25155	0x83a802		750a			JNE 0x83a80e
  checker.go:25155	0x83a804		488b8c2498000000	MOVQ 0x98(SP), CX
  checker.go:25155	0x83a80c		eb18			JMP 0x83a826
  checker.go:25155	0x83a80e		488b4260		MOVQ 0x60(DX), AX
  checker.go:25155	0x83a812		e8e96cc5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25155	0x83a817		488b8c2498000000	MOVQ 0x98(SP), CX
  checker.go:25155	0x83a81f		49890b			MOVQ CX, 0(R11)
  checker.go:25155	0x83a822		49894308		MOVQ AX, 0x8(R11)
  checker.go:25155	0x83a826		48894a60		MOVQ CX, 0x60(DX)
  checker.go:25155	0x83a82a		eb24			JMP 0x83a850
  checker.go:25157	0x83a82c		440f117a68		MOVUPS X15, 0x68(DX)
  checker.go:25157	0x83a831		833dd8ec6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25157	0x83a838		740e			JE 0x83a848
  checker.go:25157	0x83a83a		488b4260		MOVQ 0x60(DX), AX
  checker.go:25157	0x83a83e		6690			NOPW
  checker.go:25157	0x83a840		e89b6cc5ff		CALL runtime.gcWriteBarrier1(SB)
  checker.go:25157	0x83a845		498903			MOVQ AX, 0(R11)
  checker.go:25157	0x83a848		48c7426000000000	MOVQ $0x0, 0x60(DX)
  checker.go:25159	0x83a850		48c7427800000000	MOVQ $0x0, 0x78(DX)
  checker.go:25161	0x83a858		488b442458		MOVQ 0x58(SP), AX
  checker.go:25161	0x83a85d		48898288000000		MOVQ AX, 0x88(DX)
  checker.go:25161	0x83a864		48898290000000		MOVQ AX, 0x90(DX)
  checker.go:25161	0x83a86b		833d9eec6b0100		CMPL runtime.writeBarrier(SB), $0x0
  checker.go:25161	0x83a872		7507			JNE 0x83a87b
  checker.go:25161	0x83a874		488b4c2450		MOVQ 0x50(SP), CX
  checker.go:25161	0x83a879		eb18			JMP 0x83a893
  checker.go:25161	0x83a87b		488b8280000000		MOVQ 0x80(DX), AX
  checker.go:25161	0x83a882		e8796cc5ff		CALL runtime.gcWriteBarrier2(SB)
  checker.go:25161	0x83a887		488b4c2450		MOVQ 0x50(SP), CX
  checker.go:25161	0x83a88c		49890b			MOVQ CX, 0(R11)
  checker.go:25161	0x83a88f		49894308		MOVQ AX, 0x8(R11)
  checker.go:25161	0x83a893		48898a80000000		MOVQ CX, 0x80(DX)
  checker.go:25162	0x83a89a		4883c440		ADDQ $0x40, SP
  checker.go:25162	0x83a89e		5d			POPQ BP
  checker.go:25162	0x83a89f		90			NOPL
  checker.go:25162	0x83a8a0		c3			RET
  type_data.go:129	0x83a8a1		488d05b87d5200		LEAQ 0x527db8(IP), AX
  type_data.go:129	0x83a8a8		488d1d01a9ce00		LEAQ 0xcea901(IP), BX
  type_data.go:129	0x83a8af		e8ecf1c4ff		CALL runtime.gopanic(SB)
  type_data.go:129	0x83a8b4		90			NOPL
  checker.go:25140	0x83a8b5		4889442420		MOVQ AX, 0x20(SP)
  checker.go:25140	0x83a8ba		48895c2428		MOVQ BX, 0x28(SP)
  checker.go:25140	0x83a8bf		48894c2430		MOVQ CX, 0x30(SP)
  checker.go:25140	0x83a8c4		48897c2438		MOVQ DI, 0x38(SP)
  checker.go:25140	0x83a8c9		4889742440		MOVQ SI, 0x40(SP)
  checker.go:25140	0x83a8ce		4c89442448		MOVQ R8, 0x48(SP)
  checker.go:25140	0x83a8d3		4c894c2450		MOVQ R9, 0x50(SP)
  checker.go:25140	0x83a8d8		4c89542458		MOVQ R10, 0x58(SP)
  checker.go:25140	0x83a8dd		4c895c2460		MOVQ R11, 0x60(SP)
  checker.go:25140	0x83a8e2		e81951c5ff		CALL runtime.morestack_noctxt.abi0(SB)
  checker.go:25140	0x83a8e7		488b442420		MOVQ 0x20(SP), AX
  checker.go:25140	0x83a8ec		488b5c2428		MOVQ 0x28(SP), BX
  checker.go:25140	0x83a8f1		488b4c2430		MOVQ 0x30(SP), CX
  checker.go:25140	0x83a8f6		488b7c2438		MOVQ 0x38(SP), DI
  checker.go:25140	0x83a8fb		488b742440		MOVQ 0x40(SP), SI
  checker.go:25140	0x83a900		4c8b442448		MOVQ 0x48(SP), R8
  checker.go:25140	0x83a905		4c8b4c2450		MOVQ 0x50(SP), R9
  checker.go:25140	0x83a90a		4c8b542458		MOVQ 0x58(SP), R10
  checker.go:25140	0x83a90f		4c8b5c2460		MOVQ 0x60(SP), R11
  checker.go:25140	0x83a914		e927fdffff		JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).setStructuredTypeMembers(SB)
