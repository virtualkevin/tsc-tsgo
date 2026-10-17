package compiler

import (
	"reflect"
	"slices"
	"testing"

	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/module"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
)

func TestDependencyCheckerGroups(t *testing.T) {
	for _, test := range []struct {
		name    string
		weights []int
		imports [][]int
		count   int
		want    [][]int
	}{
		{"shared large declaration", []int{1_000_000, 10_000, 10_000, 1_000_000}, [][]int{nil, {0}, {0}, nil}, 2, [][]int{{0, 1, 2}}},
		{"cycles and duplicate edges", []int{1_000_000, 10_000, 10_000, 1_000_000}, [][]int{{1, 1}, {0, 0}, {1, 1}, nil}, 2, [][]int{{0, 1, 2}}},
		{"over budget", []int{1_000_000, 1_000_000}, [][]int{{1}, {0}}, 2, nil},
		{"skipped files excluded", []int{1_000_000, 10_000, 0, 2_000_000}, [][]int{nil, {0, 2}, {0}, nil}, 2, [][]int{{0, 1}}},
		{"below minimum seed load", []int{100, 10, 10}, [][]int{nil, {0}, {0}}, 2, nil},
		{"zero weights", []int{0, 0}, [][]int{{1}, {0}}, 2, nil},
		{"empty", nil, nil, 4, nil},
	} {
		t.Run(test.name, func(t *testing.T) {
			got := dependencyCheckerGroups(test.weights, test.imports, test.count)
			if !reflect.DeepEqual(got, test.want) {
				t.Fatalf("groups = %v, want %v", got, test.want)
			}
			if !reflect.DeepEqual(got, dependencyCheckerGroups(test.weights, test.imports, test.count)) {
				t.Fatal("groups changed on repeated planning")
			}
		})
	}
	// A high-fanout shared declaration must not serialize every importing file.
	weights := make([]int, 18)
	imports := make([][]int, 18)
	weights[0] = 1_000_000
	for i := 1; i < len(weights); i++ {
		weights[i] = 10_000
		imports[i] = []int{0}
	}
	if got := dependencyCheckerGroups(weights, imports, 2); len(got) != 0 {
		t.Fatalf("high-fanout declaration formed groups: %v", got)
	}
}

func TestDependencyCheckerAssignments(t *testing.T) {
	weights := []int{1_000_000, 10_000, 0, 2_000_000}
	imports := [][]int{nil, {0, 0, 2}, {0}, nil}
	got := dependencyCheckerAssignments(weights, imports, 2)
	want := []int{1, 1, 0, 0}
	if !slices.Equal(got, want) {
		t.Fatalf("assignments = %v, want %v", got, want)
	}
	// Input edge/map traversal order and repeated edges do not alter affiliation.
	if other := dependencyCheckerAssignments(weights, [][]int{nil, {2, 0}, {0}, nil}, 2); !slices.Equal(got, other) {
		t.Fatalf("edge order changed assignment: %v vs %v", got, other)
	}
	for i, owner := range got {
		if owner < 0 || owner >= 2 {
			t.Fatalf("file %d has invalid owner %d", i, owner)
		}
	}
	for _, count := range []int{1, 2, 8} {
		weights := []int{20, 0, 10, 20}
		got := dependencyCheckerAssignments(weights, nil, count)
		if !slices.Equal(got, balancedCheckerAssignments(weights, count)) {
			t.Fatalf("no-group fallback changed balanced scheduling: %v", got)
		}
	}
}

func TestCheckerSchedulingImportsUseResolvedFileIdentity(t *testing.T) {
	fs := vfstest.FromMap(map[string]string{
		"/source.ts": "export const source = 1;",
		"/target.ts": "export const target = 2;",
	}, true)
	program := NewProgram(ProgramOptions{
		Config: &tsoptions.ParsedCommandLine{ParsedConfig: &core.ParsedOptions{
			FileNames:       []string{"/source.ts", "/target.ts"},
			CompilerOptions: &core.CompilerOptions{NoLib: core.TSTrue, SingleThreaded: core.TSTrue},
		}},
		Host: NewCompilerHost("/", fs, "", nil, nil),
	})
	source := program.GetSourceFile("/source.ts")
	target := program.GetSourceFile("/target.ts")
	// Program redirects and package aliases may have several paths for one file.
	// Scheduling must deduplicate the resolved object, not its requested filename.
	program.filesByPath[program.toPath("/alias.ts")] = target
	program.resolvedModules[source.Path()] = module.ModeAwareCache[*module.ResolvedModule]{
		{Name: "target"}:     {ResolvedFileName: "/target.ts"},
		{Name: "alias"}:      {ResolvedFileName: "/alias.ts"},
		{Name: "self"}:       {ResolvedFileName: "/source.ts"},
		{Name: "missing"}:    {ResolvedFileName: "/missing.ts"},
		{Name: "unresolved"}: {},
	}
	program.typeResolutionsInFile[source.Path()] = module.ModeAwareCache[*module.ResolvedTypeReferenceDirective]{
		{Name: "target"}:  {ResolvedFileName: "/target.ts"},
		{Name: "missing"}: {},
	}
	got := checkerSchedulingImports(program)
	sourceIndex := slices.Index(program.files, source)
	targetIndex := slices.Index(program.files, target)
	if !slices.Equal(got[sourceIndex], []int{targetIndex}) {
		t.Fatalf("source imports = %v, want [%d]", got[sourceIndex], targetIndex)
	}
	if len(got[targetIndex]) != 0 {
		t.Fatalf("unexpected target imports: %v", got[targetIndex])
	}
	if !reflect.DeepEqual(got, checkerSchedulingImports(program)) {
		t.Fatal("map traversal changed graph order")
	}
}
