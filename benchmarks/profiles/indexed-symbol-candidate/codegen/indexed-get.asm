TEXT github.com/microsoft/typescript-go/internal/core.(*IndexedPointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB) github.com/microsoft/typescript-go/internal/core/indexedpointerlinkstore.go
  indexedpointerlinkstore.go:53	0x9058e0		493b6610		CMPQ SP, 0x10(R14)																													
  indexedpointerlinkstore.go:53	0x9058e4		0f8632010000		JBE 0x905a1c																														
  indexedpointerlinkstore.go:53	0x9058ea		55			PUSHQ BP																														
  indexedpointerlinkstore.go:53	0x9058eb		4889e5			MOVQ SP, BP																														
  indexedpointerlinkstore.go:53	0x9058ee		4883ec20		SUBQ $0x20, SP																														
  indexedpointerlinkstore.go:54	0x9058f2		85ff			TESTL DI, DI																														
  indexedpointerlinkstore.go:54	0x9058f4		0f840c010000		JE 0x905a06																														
  indexedpointerlinkstore.go:19	0x9058fa		8400			TESTB AL, 0(AX)																														
  indexedpointerlinkstore.go:19	0x9058fc		89fa			MOVL DI, DX																														
  indexedpointerlinkstore.go:19	0x9058fe		c1ef18			SHRL $0x18, DI																														
  indexedpointerlinkstore.go:19	0x905901		488b34f8		MOVQ 0(AX)(DI*8), SI																													
  indexedpointerlinkstore.go:20	0x905905		4885f6			TESTQ SI, SI																														
  indexedpointerlinkstore.go:20	0x905908		743a			JE 0x905944																														
  indexedpointerlinkstore.go:23	0x90590a		89d7			MOVL DX, DI																														
  indexedpointerlinkstore.go:23	0x90590c		c1ea10			SHRL $0x10, DX																														
  indexedpointerlinkstore.go:23	0x90590f		0fb6d2			MOVZX DL, DX																														
  indexedpointerlinkstore.go:23	0x905912		488b14d6		MOVQ 0(SI)(DX*8), DX																													
  indexedpointerlinkstore.go:24	0x905916		4885d2			TESTQ DX, DX																														
  indexedpointerlinkstore.go:24	0x905919		7423			JE 0x90593e																														
  indexedpointerlinkstore.go:27	0x90591b		89fe			MOVL DI, SI																														
  indexedpointerlinkstore.go:27	0x90591d		c1ef08			SHRL $0x8, DI																														
  indexedpointerlinkstore.go:27	0x905920		400fb6ff		MOVZX DI, DI																														
  indexedpointerlinkstore.go:27	0x905924		488b14fa		MOVQ 0(DX)(DI*8), DX																													
  indexedpointerlinkstore.go:28	0x905928		4885d2			TESTQ DX, DX																														
  indexedpointerlinkstore.go:28	0x90592b		740d			JE 0x90593a																														
  indexedpointerlinkstore.go:31	0x90592d		400fb6fe		MOVZX SI, DI																														
  indexedpointerlinkstore.go:31	0x905931		48c1e704		SHLQ $0x4, DI																														
  indexedpointerlinkstore.go:31	0x905935		4801fa			ADDQ DI, DX																														
  indexedpointerlinkstore.go:57	0x905938		eb0e			JMP 0x905948																														
  indexedpointerlinkstore.go:57	0x90593a		31d2			XORL DX, DX																														
  indexedpointerlinkstore.go:57	0x90593c		eb0a			JMP 0x905948																														
  indexedpointerlinkstore.go:65	0x90593e		89fe			MOVL DI, SI																														
  indexedpointerlinkstore.go:65	0x905940		31d2			XORL DX, DX																														
  indexedpointerlinkstore.go:57	0x905942		eb04			JMP 0x905948																														
  indexedpointerlinkstore.go:65	0x905944		89d6			MOVL DX, SI																														
  indexedpointerlinkstore.go:65	0x905946		31d2			XORL DX, DX																														
  indexedpointerlinkstore.go:54	0x905948		48894c2440		MOVQ CX, 0x40(SP)																													
  indexedpointerlinkstore.go:58	0x90594d		4885d2			TESTQ DX, DX																														
  indexedpointerlinkstore.go:58	0x905950		7435			JE 0x905987																														
  indexedpointerlinkstore.go:58	0x905952		488b7a08		MOVQ 0x8(DX), DI																													
  indexedpointerlinkstore.go:58	0x905956		4885ff			TESTQ DI, DI																														
  indexedpointerlinkstore.go:58	0x905959		7427			JE 0x905982																														
  indexedpointerlinkstore.go:58	0x90595b		0f1f440000		NOPL 0(AX)(AX*1)																													
  indexedpointerlinkstore.go:59	0x905960		48390a			CMPQ 0(DX), CX																														
  indexedpointerlinkstore.go:59	0x905963		7509			JNE 0x90596e																														
  indexedpointerlinkstore.go:60	0x905965		4889f8			MOVQ DI, AX																														
  indexedpointerlinkstore.go:60	0x905968		4883c420		ADDQ $0x20, SP																														
  indexedpointerlinkstore.go:60	0x90596c		5d			POPQ BP																															
  indexedpointerlinkstore.go:60	0x90596d		c3			RET																															
  indexedpointerlinkstore.go:62	0x90596e		480518080000		ADDQ $0x818, AX																														
  indexedpointerlinkstore.go:62	0x905974		488b1b			MOVQ 0(BX), BX																														
  indexedpointerlinkstore.go:62	0x905977		e804030000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)			
  indexedpointerlinkstore.go:62	0x90597c		4883c420		ADDQ $0x20, SP																														
  indexedpointerlinkstore.go:62	0x905980		5d			POPQ BP																															
  indexedpointerlinkstore.go:62	0x905981		c3			RET																															
  indexedpointerlinkstore.go:58	0x905982		4885d2			TESTQ DX, DX																														
  indexedpointerlinkstore.go:64	0x905985		7522			JNE 0x9059a9																														
  indexedpointerlinkstore.go:54	0x905987		4889442430		MOVQ AX, 0x30(SP)																													
  indexedpointerlinkstore.go:54	0x90598c		48895c2438		MOVQ BX, 0x38(SP)																													
  indexedpointerlinkstore.go:65	0x905991		488b5b08		MOVQ 0x8(BX), BX																													
  indexedpointerlinkstore.go:65	0x905995		89f1			MOVL SI, CX																														
  indexedpointerlinkstore.go:65	0x905997		e8c4000000		CALL github.com/microsoft/typescript-go/internal/core.(*IndexedPointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).ensureEntry(SB)	
  indexedpointerlinkstore.go:67	0x90599c		488b5c2438		MOVQ 0x38(SP), BX																													
  indexedpointerlinkstore.go:67	0x9059a1		4889c2			MOVQ AX, DX																														
  indexedpointerlinkstore.go:67	0x9059a4		488b442430		MOVQ 0x30(SP), AX																													
  indexedpointerlinkstore.go:67	0x9059a9		4889542418		MOVQ DX, 0x18(SP)																													
  indexedpointerlinkstore.go:67	0x9059ae		480500080000		ADDQ $0x800, AX																														
  indexedpointerlinkstore.go:67	0x9059b4		488b5b10		MOVQ 0x10(BX), BX																													
  indexedpointerlinkstore.go:67	0x9059b8		e8c3070000		CALL github.com/microsoft/typescript-go/internal/core.(*Arena[go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).New(SB)													
  indexedpointerlinkstore.go:68	0x9059bd		488b4c2418		MOVQ 0x18(SP), CX																													
  indexedpointerlinkstore.go:68	0x9059c2		8401			TESTB AL, 0(CX)																														
  indexedpointerlinkstore.go:68	0x9059c4		833d453b5f0100		CMPL runtime.writeBarrier(SB), $0x0																											
  indexedpointerlinkstore.go:68	0x9059cb		7507			JNE 0x9059d4																														
  indexedpointerlinkstore.go:68	0x9059cd		488b742440		MOVQ 0x40(SP), SI																													
  indexedpointerlinkstore.go:68	0x9059d2		eb25			JMP 0x9059f9																														
  indexedpointerlinkstore.go:68	0x9059d4		488b11			MOVQ 0(CX), DX																														
  indexedpointerlinkstore.go:68	0x9059d7		488b5908		MOVQ 0x8(CX), BX																													
  indexedpointerlinkstore.go:68	0x9059db		0f1f440000		NOPL 0(AX)(AX*1)																													
  indexedpointerlinkstore.go:68	0x9059e0		e85bbbb8ff		CALL runtime.gcWriteBarrier4(SB)																											
  indexedpointerlinkstore.go:68	0x9059e5		488b742440		MOVQ 0x40(SP), SI																													
  indexedpointerlinkstore.go:68	0x9059ea		498933			MOVQ SI, 0(R11)																														
  indexedpointerlinkstore.go:68	0x9059ed		49895308		MOVQ DX, 0x8(R11)																													
  indexedpointerlinkstore.go:68	0x9059f1		49894310		MOVQ AX, 0x10(R11)																													
  indexedpointerlinkstore.go:68	0x9059f5		49895b18		MOVQ BX, 0x18(R11)																													
  indexedpointerlinkstore.go:68	0x9059f9		488931			MOVQ SI, 0(CX)																														
  indexedpointerlinkstore.go:68	0x9059fc		48894108		MOVQ AX, 0x8(CX)																													
  indexedpointerlinkstore.go:69	0x905a00		4883c420		ADDQ $0x20, SP																														
  indexedpointerlinkstore.go:69	0x905a04		5d			POPQ BP																															
  indexedpointerlinkstore.go:69	0x905a05		c3			RET																															
  indexedpointerlinkstore.go:55	0x905a06		8400			TESTB AL, 0(AX)																														
  indexedpointerlinkstore.go:55	0x905a08		480518080000		ADDQ $0x818, AX																														
  indexedpointerlinkstore.go:55	0x905a0e		488b1b			MOVQ 0(BX), BX																														
  indexedpointerlinkstore.go:55	0x905a11		e86a020000		CALL github.com/microsoft/typescript-go/internal/core.(*PointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)			
  indexedpointerlinkstore.go:55	0x905a16		4883c420		ADDQ $0x20, SP																														
  indexedpointerlinkstore.go:55	0x905a1a		5d			POPQ BP																															
  indexedpointerlinkstore.go:55	0x905a1b		c3			RET																															
  indexedpointerlinkstore.go:53	0x905a1c		4889442408		MOVQ AX, 0x8(SP)																													
  indexedpointerlinkstore.go:53	0x905a21		48895c2410		MOVQ BX, 0x10(SP)																													
  indexedpointerlinkstore.go:53	0x905a26		48894c2418		MOVQ CX, 0x18(SP)																													
  indexedpointerlinkstore.go:53	0x905a2b		897c2420		MOVL DI, 0x20(SP)																													
  indexedpointerlinkstore.go:53	0x905a2f		e8cc9fb8ff		CALL runtime.morestack_noctxt.abi0(SB)																											
  indexedpointerlinkstore.go:53	0x905a34		488b442408		MOVQ 0x8(SP), AX																													
  indexedpointerlinkstore.go:53	0x905a39		488b5c2410		MOVQ 0x10(SP), BX																													
  indexedpointerlinkstore.go:53	0x905a3e		488b4c2418		MOVQ 0x18(SP), CX																													
  indexedpointerlinkstore.go:53	0x905a43		8b7c2420		MOVL 0x20(SP), DI																													
  indexedpointerlinkstore.go:53	0x905a47		e994feffff		JMP github.com/microsoft/typescript-go/internal/core.(*IndexedPointerLinkStore[go.shape.c0c4b16d918faf8873b6fc03e3aff51f6fc22122f56fa6b90453d0a3782a74c5,go.shape.d6cbdb9886be08dc6c9eab4296483119612961cb9874c1cd84b71bcfe563e7bf]).Get(SB)		
