TEXT github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfPropertyOfType(SB) github.com/microsoft/typescript-go/internal/checker/checker.go
  checker.go:18819	0x80e9c0		493b6610		CMPQ SP, 0x10(R14)										
  checker.go:18819	0x80e9c4		763f			JBE 0x80ea05											
  checker.go:18819	0x80e9c6		55			PUSHQ BP											
  checker.go:18819	0x80e9c7		4889e5			MOVQ SP, BP											
  checker.go:18819	0x80e9ca		4883ec28		SUBQ $0x28, SP											
  checker.go:18819	0x80e9ce		48894c2448		MOVQ CX, 0x48(SP)										
  checker.go:18821	0x80e9d3		4889442438		MOVQ AX, 0x38(SP)										
  checker.go:18820	0x80e9d8		90			NOPL												
  checker.go:18756	0x80e9d9		31f6			XORL SI, SI											
  checker.go:18756	0x80e9db		4189f0			MOVL SI, R8											
  checker.go:18756	0x80e9de		6690			NOPW												
  checker.go:18756	0x80e9e0		e8fbfcffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getPropertyOfTypeEx(SB)	
  checker.go:18821	0x80e9e5		4885c0			TESTQ AX, AX											
  checker.go:18821	0x80e9e8		7413			JE 0x80e9fd											
  checker.go:18822	0x80e9ea		4889c3			MOVQ AX, BX											
  checker.go:18822	0x80e9ed		488b442438		MOVQ 0x38(SP), AX										
  checker.go:18822	0x80e9f2		e86918ffff		CALL github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfSymbol(SB)		
  checker.go:18822	0x80e9f7		4883c428		ADDQ $0x28, SP											
  checker.go:18822	0x80e9fb		5d			POPQ BP												
  checker.go:18822	0x80e9fc		c3			RET												
  checker.go:18824	0x80e9fd		31c0			XORL AX, AX											
  checker.go:18824	0x80e9ff		4883c428		ADDQ $0x28, SP											
  checker.go:18824	0x80ea03		5d			POPQ BP												
  checker.go:18824	0x80ea04		c3			RET												
  checker.go:18819	0x80ea05		4889442408		MOVQ AX, 0x8(SP)										
  checker.go:18819	0x80ea0a		48895c2410		MOVQ BX, 0x10(SP)										
  checker.go:18819	0x80ea0f		48894c2418		MOVQ CX, 0x18(SP)										
  checker.go:18819	0x80ea14		48897c2420		MOVQ DI, 0x20(SP)										
  checker.go:18819	0x80ea19		e8e20fc8ff		CALL runtime.morestack_noctxt.abi0(SB)								
  checker.go:18819	0x80ea1e		488b442408		MOVQ 0x8(SP), AX										
  checker.go:18819	0x80ea23		488b5c2410		MOVQ 0x10(SP), BX										
  checker.go:18819	0x80ea28		488b4c2418		MOVQ 0x18(SP), CX										
  checker.go:18819	0x80ea2d		488b7c2420		MOVQ 0x20(SP), DI										
  checker.go:18819	0x80ea32		eb8c			JMP github.com/microsoft/typescript-go/internal/checker.(*Checker).getTypeOfPropertyOfType(SB)	
