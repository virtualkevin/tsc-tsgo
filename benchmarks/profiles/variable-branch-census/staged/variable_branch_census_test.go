package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func variableCensusChecker() *Checker {
	c := pendingTestChecker()
	c.variableBranchCensus = &variableBranchCensus{rows: make(map[variableBranchKey]*variableBranchRow)}
	return c
}
func TestVariableBranchNestedPartition(t *testing.T) {
	c := variableCensusChecker()
	outer := c.beginVariableBranch(ast.KindParameter, false, CheckModeNormal)
	c.TotalInstantiationCount += 2
	inner := c.beginVariableBranch(ast.KindPropertySignature, true, CheckModeNormal)
	inner.selectBranch(5)
	c.TotalInstantiationCount += 3
	typ := &Type{flags: TypeFlagsString}
	c.endVariableBranch(inner, typ)
	c.TotalInstantiationCount += 4
	outer.selectBranch(12)
	c.endVariableBranch(outer, nil)
	if c.variableBranchCensus.active != nil {
		t.Fatal("active frame")
	}
	a, b := c.variableBranchCensus.rows[outer.key], c.variableBranchCensus.rows[inner.key]
	if a.InclusiveInstantiations != 9 || a.ExclusiveInstantiations != 6 || b.ExclusiveInstantiations != 3 || a.NonNil != 0 || b.NonNil != 1 {
		t.Fatal("partition")
	}
	if a.ExclusiveNs > a.InclusiveNs || a.Calls != 1 || b.Calls != 1 {
		t.Fatal("elapsed/counts")
	}
}
func TestVariableBranchAnnotationDifferential(t *testing.T) {
	f := ast.NewNodeFactory(ast.NodeFactoryHooks{})
	for _, annotated := range []bool{false, true} {
		var annotation *ast.Node
		if annotated {
			annotation = f.NewKeywordTypeNode(ast.KindStringKeyword)
		}
		declaration := f.NewPropertySignatureDeclaration(nil, f.NewIdentifier("p"), nil, annotation, nil)
		declaration.Parent = &ast.Node{Kind: ast.KindInterfaceDeclaration}
		if annotation != nil {
			annotation.Parent = declaration
		}
		for _, enabled := range []bool{false, true} {
			c := pendingTestChecker()
			c.stringType = &Type{flags: TypeFlagsString}
			if enabled {
				c.variableBranchCensus = &variableBranchCensus{rows: make(map[variableBranchKey]*variableBranchRow)}
			}
			before := c.SymbolCount
			result := c.getTypeForVariableLikeDeclaration(declaration, false, CheckModeNormal)
			if (annotated && result != c.stringType) || (!annotated && result != nil) || c.SymbolCount != before || c.TotalInstantiationCount != 0 {
				t.Fatal("behavior changed", annotated, enabled)
			}
			if enabled {
				if len(c.variableBranchCensus.rows) != 1 {
					t.Fatal("row count")
				}
				for key, row := range c.variableBranchCensus.rows {
					expected := 18
					if annotated {
						expected = 5
					}
					if key.Branch != expected || row.Calls != 1 || (row.NonNil == 1) != annotated {
						t.Fatal("branch accounting", key, row)
					}
				}
			}
		}
	}
}
func TestVariableBranchSnapshotFields(t *testing.T) {
	c := variableCensusChecker()
	c.instantiationDepth = 1
	frame := c.beginVariableBranch(ast.KindParameter, true, CheckModeNormal)
	frame.selectBranch(8)
	c.endVariableBranch(frame, nil)
	snapshot, ok := c.VariableBranchSnapshot()
	if !ok || snapshot.Active || len(snapshot.Rows) != 1 {
		t.Fatal("snapshot")
	}
	encoded, err := json.Marshal(snapshot)
	if err != nil {
		t.Fatal(err)
	}
	var decoded struct {
		Rows []struct {
			Branch                            int
			DeclarationKind                   int
			IncludeOptionality, ActiveContext bool
			Calls                             uint64
		}
	}
	if err = json.Unmarshal(encoded, &decoded); err != nil {
		t.Fatal(err)
	}
	row := decoded.Rows[0]
	if row.Branch != 8 || row.DeclarationKind != int(ast.KindParameter) || !row.IncludeOptionality || !row.ActiveContext || row.Calls != 1 {
		t.Fatal("lost fields", string(encoded))
	}
	var absent *variableBranchFrame
	absent.selectBranch(5)
}
