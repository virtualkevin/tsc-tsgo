package checker_test

import (
	"fmt"
	"strings"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/bundled"
	"github.com/microsoft/typescript-go/internal/checker"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
)

func pendingAPIChecker(t *testing.T, content string) (*checker.Checker, *ast.SourceFile) {
	t.Helper()
	fs := bundled.WrapFS(vfstest.FromMap(map[string]string{
		"/pending.ts":    content,
		"/tsconfig.json": `{"compilerOptions":{"strict":true,"target":"es2022","noEmit":true},"files":["pending.ts"]}`,
	}, false))
	host := compiler.NewCompilerHost("/", fs, bundled.LibPath(), nil, nil)
	parsed, diagnostics := tsoptions.GetParsedCommandLineOfConfigFile("/tsconfig.json", &core.CompilerOptions{}, nil, host, nil)
	if len(diagnostics) != 0 {
		t.Fatalf("configuration diagnostics: %v", diagnostics)
	}
	program := compiler.NewProgram(compiler.ProgramOptions{Config: parsed, Host: host})
	program.BindSourceFiles()
	c, done := program.GetTypeChecker(t.Context())
	t.Cleanup(done)
	return c, program.GetSourceFile("/pending.ts")
}

func pendingVariableType(c *checker.Checker, file *ast.SourceFile, index int) *checker.Type {
	name := file.Statements.Nodes[index].AsVariableStatement().DeclarationList.AsVariableDeclarationList().Declarations.Nodes[0].Name()
	return c.GetTypeAtLocation(name)
}

func TestPendingMembersAPISparseLookupThenEnumeration(t *testing.T) {
	var text strings.Builder
	text.WriteString("interface Wide<T> {\n")
	for i := 0; i < 96; i++ {
		fmt.Fprintf(&text, "p%d: T;\n", i)
	}
	text.WriteString("}\ndeclare const value: Wide<string>;")
	c, file := pendingAPIChecker(t, text.String())
	typ := pendingVariableType(c, file, 1)
	before := c.SymbolCount
	first := c.GetPropertyOfType(typ, "p42")
	if first == nil {
		t.Fatal("missing property")
	}
	if allocated := c.SymbolCount - before; allocated >= 48 {
		t.Fatalf("single lookup instantiated most of the 96 properties: %d", allocated)
	}
	if c.GetPropertyOfType(typ, "p42") != first {
		t.Fatal("repeated lookup changed symbol identity")
	}
	properties := c.GetPropertiesOfType(typ)
	if len(properties) != 96 {
		t.Fatalf("got %d properties", len(properties))
	}
	if c.GetPropertyOfType(typ, "p42") != first {
		t.Fatal("enumeration replaced looked-up symbol")
	}
	if c.GetTypeOfSymbol(first) != c.GetStringType() {
		t.Fatal("type argument substitution was lost")
	}
	if len(typ.AsStructuredType().Properties()) != 96 {
		t.Fatal("public structured type accessor missed pending properties")
	}
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		t.Fatalf("unexpected diagnostics: %v", diagnostics)
	}
}

func TestPendingMembersAPIInheritanceAnonymousAndSetter(t *testing.T) {
	source := `
interface Base<T> { base: T; same: T }
interface Other<T> { other: T }
interface Derived<T> extends Base<T>, Other<T> { own: T; same: T }
type Box<T> = { value: T; next?: Box<T> };
class Access<T> { get entry(): string { return ""; } set entry(value: T) {} }
declare const derived: Derived<string>;
declare const box: Box<number>;
declare const accessor: Access<number>;
accessor.entry = 123;
`
	c, file := pendingAPIChecker(t, source)
	cases := []struct {
		index int
		name  string
		count int
		want  *checker.Type
	}{
		{5, "same", 4, c.GetStringType()},
		{6, "value", 2, c.GetNumberType()},
		{7, "entry", 1, c.GetStringType()},
	}
	for _, tt := range cases {
		typ := pendingVariableType(c, file, tt.index)
		symbol := c.GetPropertyOfType(typ, tt.name)
		if symbol == nil {
			t.Fatalf("missing %s", tt.name)
		}
		properties := c.GetPropertiesOfType(typ)
		if len(properties) != tt.count {
			t.Fatalf("%s: got %d properties, want %d", tt.name, len(properties), tt.count)
		}
		if c.GetPropertyOfType(typ, tt.name) != symbol {
			t.Fatalf("%s changed identity", tt.name)
		}
		if c.GetTypeOfSymbol(symbol) != tt.want {
			t.Fatalf("%s has wrong instantiated type", tt.name)
		}
	}
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		t.Fatalf("unexpected diagnostics: %v", diagnostics)
	}
}

func TestPendingMembersAPIRecursiveBaseAndPrivateStatic(t *testing.T) {
	source := `
interface Holder<T> { value: T }
interface Recursive<T> extends Holder<Recursive<T>> { tag: T }
class Parent<T> { static #hidden = 1; value!: T; }
class Child<T> extends Parent<T> { own!: T; }
declare const recursive: Recursive<string>;
declare const child: Child<number>;
`
	c, file := pendingAPIChecker(t, source)
	recursive := pendingVariableType(c, file, 4)
	value := c.GetPropertyOfType(recursive, "value")
	if value == nil || c.GetTypeOfSymbol(value) != recursive {
		t.Fatal("recursive base substitution changed type identity")
	}
	if len(c.GetPropertiesOfType(recursive)) != 2 || c.GetPropertyOfType(recursive, "value") != value {
		t.Fatal("recursive base enumeration changed symbol identity")
	}
	child := pendingVariableType(c, file, 5)
	inherited := c.GetPropertyOfType(child, "value")
	if inherited == nil || c.GetTypeOfSymbol(inherited) != c.GetNumberType() {
		t.Fatal("class base type argument substitution was lost")
	}
	if len(c.GetPropertiesOfType(child)) != 2 {
		t.Fatal("private static member leaked into instance properties")
	}
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		t.Fatalf("unexpected diagnostics: %v", diagnostics)
	}
}
