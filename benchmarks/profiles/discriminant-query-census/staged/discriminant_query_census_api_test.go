package checker_test

import (
	"github.com/microsoft/typescript-go/internal/bundled"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
	"reflect"
	"testing"
)

func TestDiscriminantQueryActualCheckerDifferential(t *testing.T) {
	var control [3]uint32
	var controlTypes []string
	for _, enabled := range []bool{false, true} {
		value := ""
		if enabled {
			value = "enabled"
		}
		t.Setenv("TSC_GO_DISCRIMINANT_QUERY_CENSUS", value)
		fs := bundled.WrapFS(vfstest.FromMap(map[string]string{
			"/main.tsx": `declare namespace JSX { interface Element {} interface IntrinsicElements { box: {kind: "a"; value: string} | {kind: "b"; value: number} } }
   type Props = {kind: "a"; value: string} | {kind: "b"; value: number};
   const a = <box kind="a" value="ok"/>;
   const b: Props = {kind: "b", value: 1};`,
			"/tsconfig.json": `{"compilerOptions":{"strict":true,"target":"es2022","jsx":"preserve","noEmit":true},"files":["main.tsx"]}`,
		}, false))
		host := compiler.NewCompilerHost("/", fs, bundled.LibPath(), nil, nil)
		config, ds := tsoptions.GetParsedCommandLineOfConfigFile("/tsconfig.json", &core.CompilerOptions{}, nil, host, nil)
		if len(ds) != 0 {
			t.Fatal(ds)
		}
		program := compiler.NewProgram(compiler.ProgramOptions{Config: config, Host: host})
		program.BindSourceFiles()
		c, done := program.GetTypeChecker(t.Context())
		file := program.GetSourceFile("/main.tsx")
		var rendered []string
		for _, i := range []int{2, 3} {
			name := file.Statements.Nodes[i].AsVariableStatement().DeclarationList.AsVariableDeclarationList().Declarations.Nodes[0].Name()
			before := c.GetTypeAtLocation(name)
			rendered = append(rendered, c.TypeToString(before))
			if ds := c.GetDiagnostics(t.Context(), file); len(ds) != 0 {
				t.Fatalf("diagnostics: %v", ds)
			}
			if c.GetTypeAtLocation(name) != before {
				t.Fatal("query history identity changed")
			}
		}
		counters := [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}
		if !enabled {
			control = counters
			controlTypes = rendered
		} else {
			if counters != control || !reflect.DeepEqual(rendered, controlTypes) {
				t.Fatal("observer changed behavior", control, counters, controlTypes, rendered)
			}
			snapshot, ok := c.DiscriminantQuerySnapshot()
			var calls uint64
			for _, r := range snapshot.Rows {
				calls += r.Calls
			}
			if !ok || snapshot.Active || calls == 0 {
				t.Fatal("observer not exercised", snapshot)
			}
		}
		done()
	}
}
