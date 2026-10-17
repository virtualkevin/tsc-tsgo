package checker_test

import (
	"github.com/microsoft/typescript-go/internal/bundled"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
	"testing"
)

func TestConditionalInferenceFalseBranchAndDeferredGuards(t *testing.T) {
	const source = `
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends
    (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type Tag<T> = T extends { kind: "wanted"; value: infer V } ? V : "miss";
type Miss = Assert<Equal<Tag<{ kind: "other"; value: number }>, "miss">>;
type Hit = Assert<Equal<Tag<{ kind: "wanted"; value: number }>, number>>;
type Distributed = Assert<Equal<Tag<{ kind: "other"; value: number } |
    { kind: "wanted"; value: boolean }>, "miss" | boolean>>;
type AnyInput = Assert<Equal<Tag<any>, unknown>>;
type NeverInput = Assert<Equal<Tag<never>, never>>;
interface Box<K, V> { kind: K; value: V }
type Ref<T> = T extends Box<"wanted", infer V> ? V : "miss";
type RefMiss = Assert<Equal<Ref<Box<"other", number>>, "miss">>;
type RefHit = Assert<Equal<Ref<Box<"wanted", string>>, string>>;
type Constrained<T> = T extends { kind: "wanted"; value: infer V extends number } ? V : "miss";
type ConstraintMiss = Assert<Equal<Constrained<Box<"wanted", string>>, "miss">>;
type ConstraintHit = Assert<Equal<Constrained<Box<"wanted", 42>>, 42>>;
type Tuple<T> = T extends [string, infer V] ? V : "miss";
type TupleHit = Assert<Equal<Tuple<[string, 42]>, 42>>;
type TupleMiss = Assert<Equal<Tuple<[number, 42]>, "miss">>;
type Mapped<T> = { [K in keyof T]: T[K] };
type Unmap<T> = T extends Mapped<infer U> ? U : never;
type MappedHit = Assert<Equal<Unmap<{ a: number; b: string }>, { a: number; b: string }>>;
function deferred<T>(value: T) {
    const wrap = { kind: "wanted" as const, value };
    type Result = Tag<typeof wrap>;
    return null as unknown as Result;
}
const inferred = deferred(42 as const);
type Deferred = Assert<Equal<typeof inferred, 42>>;
type Nested<T extends { kind: string; value: number }> = Tag<T>;
type NestedHit = Assert<Equal<Nested<{ kind: "wanted"; value: 1 }>, 1>>;
type NestedMiss = Assert<Equal<Nested<{ kind: "other"; value: 1 }>, "miss">>;
`
	c, file := pendingAPIChecker(t, source)
	for _, diagnostic := range c.GetDiagnostics(t.Context(), file) {
		t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
	}
}

func TestConditionalInferenceVariadicTupleInsideCallable(t *testing.T) {
	const source = `
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends
    (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type Fn = (arg: [number]) => void;
type Plain = Fn extends (arg: [...infer T]) => void ? T : never;
type Parenthesized = Fn extends (arg: [...(infer T)]) => void ? T : never;
type Deep = Fn extends (arg: [...((((infer T))))]) => void ? T : never;
type A = Assert<Equal<Plain, [number]>>;
type B = Assert<Equal<Parenthesized, [number]>>;
type C = Assert<Equal<Deep, [number]>>;
type Wrapped = { fn: Fn } extends { fn: (arg: [...(infer T)]) => void } ? T : never;
type D = Assert<Equal<Wrapped, [number]>>;
interface Wrapper<T extends unknown[]> { fn: (arg: [...T]) => void }
type Generic = Wrapper<[number]> extends Wrapper<infer T> ? T : never;
type E = Assert<Equal<Generic, [number]>>;
type Constructor = new (arg: [number]) => object;
type Constructed = Constructor extends new (arg: [...(infer T)]) => object ? T : never;
type F = Assert<Equal<Constructed, [number]>>;
type MatchingTag = { kind: "hit"; fn: Fn } extends
    { kind: "hit"; fn: (arg: [...infer T]) => void } ? T : never;
type G = Assert<Equal<MatchingTag, [number]>>;
type WrongTag = { kind: "miss"; fn: Fn } extends
    { kind: "hit"; fn: (arg: [...infer T]) => void } ? T : "miss";
type H = Assert<Equal<WrongTag, "miss">>;
type OptionalTag = { kind?: "miss"; fn: Fn } extends
    { kind?: "hit"; fn: (arg: [...infer T]) => void } ? T : "miss";
type I = Assert<Equal<OptionalTag, "miss">>;
`
	c, file := pendingAPIChecker(t, source)
	for _, diagnostic := range c.GetDiagnostics(t.Context(), file) {
		t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
	}
}

func TestConditionalInferenceLiteralTagWithoutStrictNullChecks(t *testing.T) {
	const source = `
type FromNull = { kind: null; value: number } extends
    { kind: "hit"; value: infer V } ? V : "miss";
type FromUndefined = { kind: undefined; value: number } extends
    { kind: "hit"; value: infer V } ? V : "miss";
const fromNull: FromNull = 1;
const fromUndefined: FromUndefined = 1;
`
	fs := bundled.WrapFS(vfstest.FromMap(map[string]string{
		"/conditional.ts": source,
		"/tsconfig.json":  `{"compilerOptions":{"strict":true,"strictNullChecks":false,"target":"es2022","noEmit":true},"files":["conditional.ts"]}`,
	}, false))
	host := compiler.NewCompilerHost("/", fs, bundled.LibPath(), nil, nil)
	parsed, diagnostics := tsoptions.GetParsedCommandLineOfConfigFile("/tsconfig.json", &core.CompilerOptions{}, nil, host, nil)
	if len(diagnostics) != 0 {
		t.Fatalf("configuration diagnostics: %v", diagnostics)
	}
	program := compiler.NewProgram(compiler.ProgramOptions{Config: parsed, Host: host})
	program.BindSourceFiles()
	c, done := program.GetTypeChecker(t.Context())
	defer done()
	for _, diagnostic := range c.GetDiagnostics(t.Context(), program.GetSourceFile("/conditional.ts")) {
		t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
	}
}
