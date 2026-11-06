package checker_test

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/bundled"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
	"reflect"
	"testing"
)

func TestSpreadOverrideTableHistories(t *testing.T) {
	cases := []struct {
		name, source string
		codes        []int32
	}{
		{"ordinary", `const result = {value: 1, method(x: number) {return x+1}, get label() {return "x"}};`, nil},
		{"required", `const source = {value: 2}; const result = {value: 1, ...source};`, []int32{2783}},
		{"optional", `declare const source: {value?: number}; const result = {value: 1, ...source};`, nil},
		{"leading", `const source = {value: 2}; const result = {...source, value: 1};`, nil},
		{"multiple", `const source = {value: 2}; const result = {value: 1, ...source, other: 3, ...{other: 4}};`, []int32{2783, 2783}},
		{"computed", `const key = "value"; const result = {[key]: 1, ...{value: 2}};`, []int32{2783}},
		{"accessor", `const result = {get value() {return 1}, ...{value: 2}};`, nil},
	}
	for _, strict := range []bool{false, true} {
		for _, tc := range cases {
			options := `{"compilerOptions":{"target":"es2022","noEmit":true,"strictNullChecks":` + map[bool]string{false: "false", true: "true"}[strict] + `},"files":["main.ts"]}`
			fs := bundled.WrapFS(vfstest.FromMap(map[string]string{"/main.ts": tc.source, "/tsconfig.json": options}, false))
			host := compiler.NewCompilerHost("/", fs, bundled.LibPath(), nil, nil)
			config, ds := tsoptions.GetParsedCommandLineOfConfigFile("/tsconfig.json", &core.CompilerOptions{}, nil, host, nil)
			if len(ds) != 0 {
				t.Fatal(ds)
			}
			program := compiler.NewProgram(compiler.ProgramOptions{Config: config, Host: host})
			program.BindSourceFiles()
			c, done := program.GetTypeChecker(t.Context())
			file := program.GetSourceFile("/main.ts")
			stmt := file.Statements.Nodes[len(file.Statements.Nodes)-1]
			name := stmt.AsVariableStatement().DeclarationList.AsVariableDeclarationList().Declarations.Nodes[0].Name()
			first := c.GetTypeAtLocation(name)
			var observed []int32
			var positions []int
			var messages []string
			for _, d := range c.GetDiagnostics(t.Context(), file) {
				observed = append(observed, d.Code())
				positions = append(positions, d.Pos())
				messages = append(messages, d.String())
			}
			want := tc.codes
			if !strict {
				want = nil
			}
			if !reflect.DeepEqual(observed, want) {
				t.Fatalf("%s strict=%v diagnostic codes got %v want %v", tc.name, strict, observed, want)
			}
			again := c.GetDiagnostics(t.Context(), file)
			if len(again) != len(observed) || c.GetTypeAtLocation(name) != first {
				t.Fatalf("%s unstable query history", tc.name)
			}
			text := c.TypeToString(first)
			encoded, err := json.Marshal(struct {
				Name      string
				Strict    bool
				Type      string
				Codes     []int32
				Positions []int
				Messages  []string
				Counters  [3]uint32
			}{tc.name, strict, text, observed, positions, messages, [3]uint32{c.TotalInstantiationCount, c.TypeCount, c.SymbolCount}})
			if err != nil {
				t.Fatal(err)
			}
			t.Log("OBSERVED " + string(encoded))
			done()
		}
	}
}
