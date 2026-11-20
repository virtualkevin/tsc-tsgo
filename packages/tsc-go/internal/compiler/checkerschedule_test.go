package compiler

import (
	"slices"
	"strings"
	"testing"

	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/vfs/vfstest"
)

func TestBalancedCheckerAssignments(t *testing.T) {
	for _, test := range []struct {
		name    string
		weights []int
		count   int
		want    []int
	}{
		{"empty", nil, 4, []int{}},
		{"one checker", []int{100, 10, 0, 100}, 1, []int{0, 0, 0, 0}},
		{"balanced heavy files", []int{100, 10, 100, 10}, 2, []int{0, 0, 1, 1}},
		{"stable equal weights", []int{10, 10, 10, 10, 10}, 3, []int{0, 1, 2, 0, 1}},
		{"skipped files have no load", []int{0, 100, 0, 10, 100, 10}, 2, []int{0, 0, 0, 0, 1, 1}},
		{"all skipped retain affinity", []int{0, 0, 0, 0, 0}, 3, []int{0, 1, 2, 0, 1}},
		{"more checkers than checked files", []int{0, 1, 0, 9}, 8, []int{0, 1, 2, 0}},
	} {
		t.Run(test.name, func(t *testing.T) {
			got := balancedCheckerAssignments(test.weights, test.count)
			if !slices.Equal(got, test.want) {
				t.Fatalf("assignments = %v, want %v", got, test.want)
			}
			if !slices.Equal(got, balancedCheckerAssignments(test.weights, test.count)) {
				t.Fatal("assignment is not deterministic")
			}
			for i, owner := range got {
				if owner < 0 || owner >= test.count {
					t.Fatalf("file %d has invalid checker %d", i, owner)
				}
			}
		})
	}
}

func TestCheckerSchedulingSkipsUncheckedFiles(t *testing.T) {
	fs := vfstest.FromMap(map[string]string{
		"/checked.ts":   "export const value = 1;",
		"/library.d.ts": strings.Repeat("declare const value: number;\n", 100),
		"/unchecked.ts": "// @ts-nocheck\n" + strings.Repeat("export const value = 1;\n", 100),
	}, true)
	program := NewProgram(ProgramOptions{
		Config: &tsoptions.ParsedCommandLine{
			ParsedConfig: &core.ParsedOptions{
				FileNames: []string{"/checked.ts", "/library.d.ts", "/unchecked.ts"},
				CompilerOptions: &core.CompilerOptions{
					NoLib:          core.TSTrue,
					SkipLibCheck:   core.TSTrue,
					SingleThreaded: core.TSTrue,
				},
			},
		},
		Host: NewCompilerHost("/", fs, "", nil, nil),
	})
	weights := checkerSchedulingWeights(program)
	if len(weights) != 3 {
		t.Fatalf("scheduled %d files, want 3", len(weights))
	}
	for i, file := range program.files {
		if file.FileName() == "/checked.ts" {
			if weights[i] != len(file.Text()) {
				t.Errorf("checked source has weight %d, want %d", weights[i], len(file.Text()))
			}
		} else if weights[i] != 0 {
			t.Errorf("skipped file %s has weight %d, want zero", file.FileName(), weights[i])
		}
	}
}
