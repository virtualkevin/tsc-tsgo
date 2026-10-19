package checker

import "github.com/microsoft/typescript-go/internal/ast"

// A typed-root sequence with the same visible order as Properties. It snapshots
// clone metadata eagerly but leaves symbol publication to identity consumers.
type pendingPropertySequence struct {
	owner     *StructuredType
	pending   *pendingInstantiatedMembers
	originals []*ast.Symbol
}

func (c *Checker) pendingPropertySequence(owner *StructuredType) (pendingPropertySequence, bool) {
	p := owner.pendingMembers
	if p == nil || p.memberNames != nil || p.resolving || p.hasBases || len(p.bases) != 0 || p.source == nil || len(p.source.entries) != len(p.source.positions) {
		return pendingPropertySequence{}, false
	}
	// Reject the whole layout before creating any cache entries. In particular,
	// instantiated sources require mapper flattening that this prototype excludes.
	for i, original := range p.source.entries {
		if p.state(i) == pendingMemberSkipped {
			continue
		}
		position, ok := p.source.positions[original.Name]
		if !ok || position != i || original.Flags&ast.SymbolFlagsProperty == 0 || original.CheckFlags&ast.CheckFlagsInstantiated != 0 {
			return pendingPropertySequence{}, false
		}
	}
	sequence := pendingPropertySequence{owner: owner, pending: p}
	for i, original := range p.source.entries {
		if p.state(i) == pendingMemberSkipped {
			continue
		}
		v := pendingPropertyView{owner, p, original, original.Name, p.state(i) == pendingMemberKept}
		// Include reserved entries: eager ownTable captures their metadata too.
		v.prepareTypeState(c)
	}
	container := owner.symbol
	partition := container != nil && container.Flags&(ast.SymbolFlagsClass|ast.SymbolFlagsInterface) != 0
	if partition {
		for i, original := range p.source.entries {
			if p.state(i) != pendingMemberSkipped && !isReservedMemberName(original.Name) && c.isDeclarationContainedBy(original, container) {
				sequence.originals = append(sequence.originals, original)
			}
		}
	}
	contained := len(sequence.originals)
	for i, original := range p.source.entries {
		if p.state(i) != pendingMemberSkipped && !isReservedMemberName(original.Name) && (!partition || !c.isDeclarationContainedBy(original, container)) {
			sequence.originals = append(sequence.originals, original)
		}
	}
	c.sortSymbols(sequence.originals[:contained])
	c.sortSymbols(sequence.originals[contained:])
	return sequence, true
}

func (s pendingPropertySequence) at(i int) pendingPropertyView {
	original := s.originals[i]
	kept := false
	if s.owner.pendingMembers == s.pending && s.pending.memberNames == nil {
		kept = s.pending.state(s.pending.source.positions[original.Name]) == pendingMemberKept
	}
	return pendingPropertyView{s.owner, s.pending, original, original.Name, kept}
}
