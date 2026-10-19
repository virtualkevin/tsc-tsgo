package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"time"
)

var variableBranchNames = []string{"unclassified", "for-in", "for-of", "binding-element", "catch", "annotation", "auto", "auto-array", "parameter-no-symbol", "accessor-this", "accessor-return", "full-signature", "contextual-parameter", "initializer", "instance-flow-or-base", "static-flow-or-base", "jsx-boolean", "binding-pattern", "no-inferred-type"}

type variableBranchKey struct {
	Branch             int
	DeclarationKind    ast.Kind
	CheckMode          CheckMode
	IncludeOptionality bool
	ActiveContext      bool
}
type variableBranchRow struct {
	variableBranchKey
	Calls, NonNil, ErrorResults                      uint64
	InclusiveNs, ExclusiveNs                         int64
	InclusiveInstantiations, ExclusiveInstantiations uint64
}
type variableBranchCensus struct {
	rows   map[variableBranchKey]*variableBranchRow
	active *variableBranchFrame
}
type variableBranchFrame struct {
	key                 variableBranchKey
	parent              *variableBranchFrame
	start               time.Time
	startInstantiations uint32
	childNs             int64
	childInstantiations uint64
}

func newVariableBranchCensus() *variableBranchCensus {
	if os.Getenv("TSC_GO_VARIABLE_BRANCH_CENSUS") == "" {
		return nil
	}
	return &variableBranchCensus{rows: make(map[variableBranchKey]*variableBranchRow)}
}
func (c *Checker) beginVariableBranch(kind ast.Kind, optional bool, mode CheckMode) *variableBranchFrame {
	frame := &variableBranchFrame{key: variableBranchKey{DeclarationKind: kind, IncludeOptionality: optional, CheckMode: mode, ActiveContext: c.instantiationDepth != 0 || len(c.activeMappers) != 0}, parent: c.variableBranchCensus.active, start: time.Now(), startInstantiations: c.TotalInstantiationCount}
	c.variableBranchCensus.active = frame
	return frame
}
func (frame *variableBranchFrame) selectBranch(branch int) {
	if frame != nil {
		frame.key.Branch = branch
	}
}
func (c *Checker) endVariableBranch(frame *variableBranchFrame, result *Type) {
	elapsed := time.Since(frame.start).Nanoseconds()
	operations := uint64(c.TotalInstantiationCount - frame.startInstantiations)
	o := c.variableBranchCensus
	if o.active != frame || elapsed < frame.childNs || operations < frame.childInstantiations || frame.key.Branch < 0 || frame.key.Branch >= len(variableBranchNames) {
		panic("variable branch census invariant")
	}
	o.active = frame.parent
	if frame.parent != nil {
		frame.parent.childNs += elapsed
		frame.parent.childInstantiations += operations
	}
	row := o.rows[frame.key]
	if row == nil {
		row = &variableBranchRow{variableBranchKey: frame.key}
		o.rows[frame.key] = row
	}
	row.Calls++
	if result != nil {
		row.NonNil++
		if result == c.errorType {
			row.ErrorResults++
		}
	}
	row.InclusiveNs += elapsed
	row.ExclusiveNs += elapsed - frame.childNs
	row.InclusiveInstantiations += operations
	row.ExclusiveInstantiations += operations - frame.childInstantiations
}

type VariableBranchSnapshot struct {
	CheckerID uint32
	Active    bool
	Rows      []variableBranchRow
}

func (c *Checker) VariableBranchSnapshot() (VariableBranchSnapshot, bool) {
	o := c.variableBranchCensus
	if o == nil {
		return VariableBranchSnapshot{}, false
	}
	rows := make([]variableBranchRow, 0, len(o.rows))
	for _, r := range o.rows {
		rows = append(rows, *r)
	}
	return VariableBranchSnapshot{c.id, o.active != nil, rows}, true
}
func WriteVariableBranchSnapshots(path string, owners []VariableBranchSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Branches      []string
		Scope         string
		Owners        []VariableBranchSnapshot
	}{1, variableBranchNames, "Uncapped actual-return-branch aggregates for all getTypeForVariableLikeDeclaration calls, not only symbol cache misses. Includes preceding unsuccessful alternatives. Exclusive values subtract nested observed calls; elapsed time is instrumented wall time, not CPU/savings. No origins, semantic equivalence or effect-free sharing established.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
