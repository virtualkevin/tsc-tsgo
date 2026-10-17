package compiler

import (
	"cmp"
	"slices"

	"github.com/microsoft/typescript-go/internal/ast"
)

// checkerSchedulingImports reads the program's completed resolutions. Module
// targets use the same redirect-aware lookup as the checker; aliases are deduped
// by SourceFile identity, and edges are sorted independently of map iteration.
func checkerSchedulingImports(program *Program) [][]int {
	index := make(map[*ast.SourceFile]int, len(program.files))
	for i, file := range program.files {
		index[file] = i
	}
	imports := make([][]int, len(program.files))
	for i, file := range program.files {
		add := func(target *ast.SourceFile) {
			if k, ok := index[target]; ok && k != i {
				imports[i] = append(imports[i], k)
			}
		}
		for _, resolved := range program.resolvedModules[file.Path()] {
			if resolved.IsResolved() {
				add(program.GetSourceFileForResolvedModule(resolved.ResolvedFileName))
			}
		}
		for _, resolved := range program.typeResolutionsInFile[file.Path()] {
			if resolved != nil && resolved.IsResolved() {
				add(program.GetSourceFile(resolved.ResolvedFileName))
			}
		}
		slices.Sort(imports[i])
		imports[i] = slices.Compact(imports[i])
	}
	return imports
}

// dependencyCheckerGroups ports the bounded checked-import groups from tsc-ts's
// parallel-check.ts. Large declarations and their few importers stay together;
// a group with substantial independent work is rejected to avoid a long tail.
// Zero-weight files are unchecked and never join groups or contribute load.
func dependencyCheckerGroups(weights []int, imports [][]int, checkerCount int) [][]int {
	const maxImporters = 16
	const leastLoad = 1_000_000
	n := len(weights)
	edges := make([][]int, n)
	importers := make([][]int, n)
	var total uint64
	for i, weight := range weights {
		if weight <= 0 {
			continue
		}
		total += uint64(weight)
		if i >= len(imports) {
			continue
		}
		for _, k := range imports[i] {
			if k >= 0 && k < n && k != i && weights[k] > 0 {
				edges[i] = append(edges[i], k)
			}
		}
		slices.Sort(edges[i])
		edges[i] = slices.Compact(edges[i])
		for _, k := range edges[i] {
			importers[k] = append(importers[k], i)
		}
	}
	starts := make([]bool, n)
	for i, weight := range weights {
		if weight <= 0 || len(importers[i]) < 1 || len(importers[i]) > maxImporters {
			continue
		}
		load := uint64(weight)
		for _, k := range edges[i] {
			load += uint64(weights[k])
		}
		starts[i] = load >= leastLoad && load*16 >= total
	}
	parent := make([]int, n)
	for i := range parent {
		parent[i] = -1
	}
	find := func(x int) int {
		if parent[x] < 0 {
			parent[x] = x
		}
		root := x
		for parent[root] != root {
			root = parent[root]
		}
		for parent[x] != root {
			next := parent[x]
			parent[x] = root
			x = next
		}
		return root
	}
	union := func(a, b int) {
		a, b = find(a), find(b)
		if a != b {
			parent[max(a, b)] = min(a, b)
		}
	}
	seen := make([]int, n)
	for i := range seen {
		seen[i] = -1
	}
	for start, isStart := range starts {
		if !isStart {
			continue
		}
		find(start)
		for _, k := range edges[start] {
			if starts[k] {
				union(start, k)
			}
		}
		for _, k := range importers[start] {
			if starts[k] {
				union(start, k)
			}
		}
		closure := []int{start}
		seen[start] = start
		complete := true
		for q := 0; q < len(closure) && complete; q++ {
			for _, k := range importers[closure[q]] {
				if seen[k] == start {
					continue
				}
				seen[k] = start
				closure = append(closure, k)
				if len(closure) > maxImporters+1 {
					complete = false
					break
				}
			}
		}
		if complete {
			for _, k := range closure {
				union(start, k)
			}
		}
	}
	members := make([][]int, n)
	for i := range weights {
		if parent[i] >= 0 {
			root := find(i)
			members[root] = append(members[root], i)
		}
	}
	var groups [][]int
	for _, group := range members {
		if len(group) < 2 {
			continue
		}
		var sum, largest uint64
		for _, i := range group {
			weight := uint64(weights[i])
			sum += weight
			largest = max(largest, weight)
		}
		if (sum-largest)*uint64(checkerCount)*4 > total {
			continue
		}
		groups = append(groups, group)
	}
	return groups
}

// dependencyCheckerAssignments balances indivisible groups and singleton files
// once, before checks run. The pool retains these associations for diagnostics,
// emit and API access; within each checker it still visits files in program order.
func dependencyCheckerAssignments(weights []int, imports [][]int, checkerCount int) []int {
	groups := dependencyCheckerGroups(weights, imports, checkerCount)
	if len(groups) == 0 {
		return balancedCheckerAssignments(weights, checkerCount)
	}
	assignments := make([]int, len(weights))
	grouped := make([]bool, len(weights))
	for i := range assignments {
		assignments[i] = i % checkerCount
	}
	type unit struct {
		files  []int
		weight uint64
	}
	units := make([]unit, 0, len(weights))
	for _, group := range groups {
		u := unit{files: group}
		for _, i := range group {
			grouped[i] = true
			u.weight += uint64(weights[i])
		}
		units = append(units, u)
	}
	for i, weight := range weights {
		if weight > 0 && !grouped[i] {
			units = append(units, unit{[]int{i}, uint64(weight)})
		}
	}
	slices.SortFunc(units, func(a, b unit) int {
		if c := cmp.Compare(b.weight, a.weight); c != 0 {
			return c
		}
		return cmp.Compare(a.files[0], b.files[0])
	})
	loads := make([]uint64, checkerCount)
	for _, u := range units {
		lightest := 0
		for i := 1; i < checkerCount; i++ {
			if loads[i] < loads[lightest] {
				lightest = i
			}
		}
		for _, file := range u.files {
			assignments[file] = lightest
		}
		loads[lightest] += u.weight
	}
	return assignments
}
