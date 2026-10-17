package checker_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/microsoft/typescript-go/internal/bundled"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
)

func TestCrossProductComplexityErrorsStillReportEachUse(t *testing.T) {
	var source strings.Builder
	for _, prefix := range []string{"A", "B"} {
		fmt.Fprintf(&source, "type %s = { %s: 1 }", prefix, prefix)
		for i := 0; i < 320; i++ {
			fmt.Fprintf(&source, " | %q", fmt.Sprintf("%s%d", prefix, i))
		}
		source.WriteString(";\n")
	}
	// Most combinations would be pruned, but the existing 100,000-combination
	// gate must still reject this input, independently at both source locations.
	source.WriteString("type First = A & B;\ntype Second = A & B;\n")
	fs := bundled.WrapFS(vfstest.FromMap(map[string]string{
		"/cross.ts":      source.String(),
		"/tsconfig.json": `{"compilerOptions":{"strict":true,"noEmit":true},"files":["cross.ts"]}`,
	}, false))
	host := compiler.NewCompilerHost("/", fs, bundled.LibPath(), nil, nil)
	config, diagnostics := tsoptions.GetParsedCommandLineOfConfigFile("/tsconfig.json", &core.CompilerOptions{}, nil, host, nil)
	if len(diagnostics) != 0 {
		t.Fatalf("unexpected config diagnostics: %v", diagnostics)
	}
	program := compiler.NewProgram(compiler.ProgramOptions{Config: config, Host: host})
	program.BindSourceFiles()
	c, done := program.GetTypeChecker(t.Context())
	defer done()
	diagnostics = c.GetDiagnostics(t.Context(), program.GetSourceFile("/cross.ts"))
	if len(diagnostics) != 2 {
		t.Fatalf("got %d diagnostics; want complexity errors at both uses", len(diagnostics))
	}
	for _, diagnostic := range diagnostics {
		if diagnostic.Code() != 2590 {
			t.Fatalf("got diagnostic %d; want complexity error 2590", diagnostic.Code())
		}
	}
}
