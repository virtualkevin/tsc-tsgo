package checker_test

import "testing"

func TestInferenceVariancesPreserveGenericAliasAndContravariantInference(t *testing.T) {
	// These type-level assertions independently specify inferred results. The
	// contravariant cases need the narrower candidate, unlike covariant inference.
	const source = `
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends
    (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
interface Animal { animal: true }
interface Dog extends Animal { dog: true }
interface Source<out T> { get: () => T }
interface Sink<in T> { put: (value: T) => void }
interface MeasuredSink<T> { put: (value: T) => void }
type SinkAlias<T> = (value: T) => void;
declare function covariant<T>(a: Source<T>, b: Source<T>): T;
declare function contravariant<T>(a: Sink<T>, b: Sink<T>): T;
declare function measuredContravariant<T>(a: MeasuredSink<T>, b: MeasuredSink<T>): T;
declare function alias<T>(a: SinkAlias<T>, b: SinkAlias<T>): T;
declare const animalSource: Source<Animal>;
declare const dogSource: Source<Dog>;
declare const animalSink: Sink<Animal>;
declare const dogSink: Sink<Dog>;
declare const animalMeasuredSink: MeasuredSink<Animal>;
declare const dogMeasuredSink: MeasuredSink<Dog>;
declare const animalAlias: SinkAlias<Animal>;
declare const dogAlias: SinkAlias<Dog>;
const wide = covariant(dogSource, animalSource);
const narrow = contravariant(animalSink, dogSink);
const measuredNarrow = measuredContravariant(animalMeasuredSink, dogMeasuredSink);
const narrowAlias = alias(animalAlias, dogAlias);
type Wide = Assert<Equal<typeof wide, Animal>>;
type Narrow = Assert<Equal<typeof narrow, Dog>>;
type MeasuredNarrow = Assert<Equal<typeof measuredNarrow, Dog>>;
type NarrowAlias = Assert<Equal<typeof narrowAlias, Dog>>;
interface Box<T> { value: T }
declare function nested<T>(box: Box<Box<T>>): T;
declare const nestedDog: Box<Box<Dog>>;
const dog = nested(nestedDog);
type Nested = Assert<Equal<typeof dog, Dog>>;
function enclosing<T>(value: T) {
  class Local { value = value; }
  declareLocal(new Local());
  return nested({ value: { value: new Local().value } });
}
declare function declareLocal<T>(value: { value: T }): T;
const captured = enclosing("captured" as const);
type Captured = Assert<Equal<typeof captured, "captured">>;
class Concrete { value = ""; }
declare function construct<T>(factory: new () => { value: T }): T;
const concrete = construct(Concrete);
type ConcreteValue = Assert<Equal<typeof concrete, string>>;
`
	c, file := pendingAPIChecker(t, source)
	if diagnostics := c.GetDiagnostics(t.Context(), file); len(diagnostics) != 0 {
		for _, diagnostic := range diagnostics {
			t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
		}
	}
}

func TestInferenceVariancesInvalidAnnotationsStillReport(t *testing.T) {
	// Concrete contextual callback arguments do not need variance measurement
	// during inference. Declaration checking must nevertheless reject each
	// incorrect variance annotation, including the function type alias.
	const source = `
interface BadSource<in T> { get: () => T }
interface BadSink<out T> { put: (value: T) => void }
type BadAlias<out T> = (value: T) => void;
declare function contextual<R>(callback: (
  source: BadSource<string>, sink: BadSink<string>, alias: BadAlias<string>
) => R): R;
const value = contextual((source, sink, alias) => {
  const text = source.get();
  sink.put(text);
  alias(text);
  return text;
});
const checked: string = value;
`
	c, file := pendingAPIChecker(t, source)
	diagnostics := c.GetDiagnostics(t.Context(), file)
	if len(diagnostics) != 3 {
		t.Fatalf("got %d diagnostics, want one per invalid variance annotation: %v", len(diagnostics), diagnostics)
	}
	for _, diagnostic := range diagnostics {
		if diagnostic.Code() != 2636 {
			t.Errorf("unexpected diagnostic %d, want variance error 2636: %v", diagnostic.Code(), diagnostic)
		}
	}
}
