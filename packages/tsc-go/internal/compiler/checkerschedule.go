package compiler

import (
	"cmp"
	"slices"
)

// balancedCheckerAssignments assigns the longest checked files to the least-loaded
// checker first. Zero weights represent skipped files; their round-robin affinity
// is retained without charging them against a checker's estimated semantic work.
// The assignment is fixed for the program's lifetime. Callers still process files
// in program order, so no checker state is shared or moved between workers.
func balancedCheckerAssignments(weights []int, checkerCount int) []int {
	assignments := make([]int, len(weights))
	order := make([]int, 0, len(weights))
	for i, weight := range weights {
		assignments[i] = i % checkerCount
		if weight > 0 {
			order = append(order, i)
		}
	}
	slices.SortStableFunc(order, func(a, b int) int {
		return cmp.Compare(weights[b], weights[a])
	})
	loads := make([]uint64, checkerCount)
	for _, file := range order {
		lightest := 0
		for checker := 1; checker < checkerCount; checker++ {
			if loads[checker] < loads[lightest] {
				lightest = checker
			}
		}
		assignments[file] = lightest
		loads[lightest] += uint64(weights[file])
	}
	return assignments
}

func checkerSchedulingWeights(program *Program) []int {
	weights := make([]int, len(program.files))
	for i, file := range program.files {
		if !program.SkipTypeChecking(file, false) {
			weights[i] = max(1, len(file.Text()))
		}
	}
	return weights
}
