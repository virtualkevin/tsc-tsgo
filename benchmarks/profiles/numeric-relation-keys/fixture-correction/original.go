package checker_test

import (
	"strings"
	"testing"
)

func TestRelationKeysRecursiveGenericAssignmentsAndDiagnostics(t *testing.T) {
	const source = `
interface Left<T> { value: T; next?: Left<T>; map<U>(f: (value: T) => U): Left<U> }
interface Right<T> { value: T; next?: Right<T>; map<U>(f: (value: T) => U): Right<U> }
declare let left: Left<string>;
declare let right: Right<string>;
left = right;
right = left;
declare let wrong: Right<number>;
// @ts-expect-error distinct recursive value types remain incompatible
left = wrong;
// @ts-expect-error cached failure must still elaborate the second diagnostic
left = wrong;
function normalized<T, U>(l: Left<T>, r: Right<T>, other: Right<U>) {
  l = r;
  // @ts-expect-error unconstrained distinct parameters cannot be conflated
  l = other;
}
interface Constrained<T extends { tag: string }> { value: T; next?: Constrained<T> }
function constrained<T extends { tag: string }, U extends { tag: string }>(l: Constrained<T>, r: Constrained<U>) {
  // @ts-expect-error sharing constraints does not make different parameters assignable
  l = r;
}
type Intersected<T> = Left<T> & { kind: "ok" };
declare let intersection: Intersected<string>;
left = intersection;
// @ts-expect-error comparison in reverse still requires the intersection property
intersection = left;
type Equal<A, B> = (<T>() => T extends A ? 1 : 2) extends (<T>() => T extends B ? 1 : 2) ? true : false;
type Assert<T extends true> = T;
type GenericSignatureIdentity = Assert<Equal<<T>(x: Left<T>) => T, <U>(x: Left<U>) => U>>;
`
	c, file := pendingAPIChecker(t, source)
	for _, diagnostic := range c.GetDiagnostics(t.Context(), file) {
		t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
	}
}

func TestRelationKeysColdRecursiveConstraints(t *testing.T) {
	// Adapted from pinned signatureInstantiationWithRecursiveConstraints.ts
	// (#17148). Type parameter constraints recurse through the containing
	// interfaces; generic result references also exercise normalized relation
	// keys. Query relations before GetDiagnostics can warm those constraints.
	const source = `
declare let left: RecursiveLeft;
declare let right: RecursiveRight;
declare let different: Different;
interface Box<T> { value: T; next?: Box<T> }
interface RecursiveLeft { method<T extends RecursiveLeft>(arg: T): Box<T> }
interface RecursiveRight { method<T extends RecursiveRight>(arg: T): Box<T> }
interface Different { required: number; method<T extends Different>(arg: T): Box<T> }
left = right;
right = left;
// @ts-expect-error the failed cold relation must still produce its diagnostic
 different = left;
// @ts-expect-error failure caching must preserve a second diagnostic
 different = left;
`
	for _, reverseFirst := range []bool{false, true} {
		name := "left-first"
		if reverseFirst {
			name = "right-first"
		}
		t.Run(name, func(t *testing.T) {
			c, file := pendingAPIChecker(t, source)
			left := pendingVariableType(c, file, 0)
			right := pendingVariableType(c, file, 1)
			different := pendingVariableType(c, file, 2)
			if reverseFirst {
				left, right = right, left
			}
			for range 2 {
				if !c.IsTypeAssignableTo(left, right) || !c.IsTypeAssignableTo(right, left) {
					t.Fatal("recursive generic constraints differ between cold and cached relation checks")
				}
				if c.IsTypeAssignableTo(left, different) || c.IsTypeAssignableTo(right, different) {
					t.Fatal("recursive key normalization lost a required property")
				}
			}
			for _, diagnostic := range c.GetDiagnostics(t.Context(), file) {
				t.Errorf("unexpected diagnostic %d: %v", diagnostic.Code(), diagnostic)
			}
		})
	}
}

// Warm failure results from the API must still elaborate each source use. This
// checks diagnostic codes and locations directly, without @ts-expect-error.
func TestRelationKeysRepeatedFailureDiagnosticsKeepUsePositions(t *testing.T) {
	const source = `declare let left: Left<string>;
declare let wrong: Right<number>;
interface Left<T> { value: T; next?: Left<T> }
interface Right<T> { value: T; next?: Right<T> }
left = wrong;
left = wrong;
`
	c, file := pendingAPIChecker(t, source)
	left := pendingVariableType(c, file, 0)
	wrong := pendingVariableType(c, file, 1)
	for range 2 {
		if c.IsTypeAssignableTo(wrong, left) {
			t.Fatal("incompatible recursive value types became assignable")
		}
	}
	first, second := strings.Index(source, "left = wrong"), strings.LastIndex(source, "left = wrong")
	for attempt := 0; attempt < 2; attempt++ {
		ds := c.GetDiagnostics(t.Context(), file)
		if len(ds) != 2 {
			t.Fatalf("query %d: want two assignment diagnostics, got %v", attempt, ds)
		}
		positions := map[int]bool{}
		for _, d := range ds {
			if d.Code() != 2322 || d.File() != file {
				t.Fatalf("query %d: unexpected diagnostic %v", attempt, d)
			}
			positions[d.Pos()] = true
		}
		if !positions[first] || !positions[second] {
			t.Fatalf("query %d: positions %v, want %d and %d", attempt, positions, first, second)
		}
	}
}
