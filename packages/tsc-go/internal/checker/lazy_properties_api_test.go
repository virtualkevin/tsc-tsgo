package checker_test

import (
	"fmt"
	"strings"
	"testing"
)

func TestLazyIntersectionAPIPreservesSparseGenericMembers(t *testing.T) {
	var source strings.Builder
	source.WriteString("interface Wide<T> { tag: T;\n")
	for i := range 96 {
		fmt.Fprintf(&source, "p%d: T;\n", i)
	}
	source.WriteString("}\ndeclare const value: Wide<string> & { tag: 'ok' };\n")
	c, file := pendingAPIChecker(t, source.String())
	before := c.SymbolCount
	typ := pendingVariableType(c, file, 1)
	tag := c.GetPropertyOfType(typ, "tag")
	if tag == nil {
		t.Fatal("missing intersection tag")
	}
	if allocated := c.SymbolCount - before; allocated >= 48 {
		t.Fatalf("sparse lookup eagerly allocated most wide generic members: %d", allocated)
	}
	if properties := c.GetPropertiesOfType(typ); len(properties) != 97 {
		t.Fatalf("got %d properties, want 97", len(properties))
	}
	if c.GetPropertyOfType(typ, "tag") != tag {
		t.Fatal("enumeration changed property identity")
	}
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		t.Fatalf("unexpected diagnostics: %v", diagnostics)
	}
}

func TestLazyIntersectionAPIPrivateOptionalPatternAndRecursiveProperties(t *testing.T) {
	const source = `
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type Conflict = { tag: "a" } & { tag: "b" };
type TagConflict = Assert<Equal<Conflict, never>>;
type Optional = { tag?: "a" } & { tag?: "b" };
const optional: Optional = {};
type ExistingNever = { value: never } & { value: string };
type NotEntirelyNever = Assert<Equal<ExistingNever extends never ? true : false, false>>;
class First { private value!: string; }
class Second { private value!: string; }
type PrivateConflict = Assert<Equal<First & Second, never>>;
class Shared { private value!: string; }
type RepeatedPrivate = Assert<Equal<Shared & Shared, Shared>>;
type Pattern = { tag: ` + "`a${string}`" + ` } & { tag: "b" };
type PatternConflict = Assert<Equal<Pattern, never>>;
interface Recursive<T> { value: T; next?: Recursive<T>; }
declare const recursive: Recursive<string> & { value: "ok" };
const next: Recursive<string> | undefined = recursive.next;
const value: "ok" = recursive.value;
interface Indexed { [name: string]: string | number }
declare function infer<T>(value: T | ({ required: string } & Indexed)): T;
const inferred = infer({ required: "", extra: 1 });
`
	c, file := pendingAPIChecker(t, source)
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		for _, diagnostic := range diagnostics {
			t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
		}
	}
}
