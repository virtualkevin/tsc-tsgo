package checker

import "github.com/microsoft/typescript-go/internal/ast"

// Reuse the immutable name-to-position layout. If actual members don't fit,
// transfer already constructed symbols to a normal table without replaying work.
type pendingMemberBuilder struct {
	names      *memberNames
	properties []*ast.Symbol
	table      ast.SymbolTable
	filled     int
}

func newPendingMemberBuilder(names *memberNames) pendingMemberBuilder {
	var properties []*ast.Symbol
	if len(names.names) != 0 {
		properties = make([]*ast.Symbol, len(names.names))
	}
	return pendingMemberBuilder{names: names, properties: properties}
}
func (b *pendingMemberBuilder) asTable() ast.SymbolTable {
	if b.table == nil {
		b.table = make(ast.SymbolTable, b.filled)
		for i, symbol := range b.properties {
			if symbol != nil {
				b.table[b.names.names[i]] = symbol
			}
		}
		b.properties = nil
	}
	return b.table
}
func (b *pendingMemberBuilder) put(name string, symbol *ast.Symbol, inherited bool) {
	if b.table == nil {
		if i, ok := b.names.positions[name]; ok {
			old := b.properties[i]
			if !inherited || old == nil || old.Flags&ast.SymbolFlagsValue == 0 {
				if old == nil {
					b.filled++
				}
				b.properties[i] = symbol
			}
			return
		}
		b.asTable()
	}
	if old, ok := b.table[name]; !inherited || !ok || old.Flags&ast.SymbolFlagsValue == 0 {
		b.table[name] = symbol
	}
}

// Only accept the exact complete named-value set in the existing sorted order.
// Distinct names avoid compareSymbols' ID-assignment tie breaker. Aliases and
// any changed declared/inherited partition use the original classification path.
func (b *pendingMemberBuilder) orderedProperties(c *Checker, container *ast.Symbol) bool {
	if b.table != nil || b.filled != len(b.properties) {
		return false
	}
	for i, symbol := range b.properties {
		if symbol.Name != b.names.names[i] || isReservedMemberName(symbol.Name) || symbol.Flags&ast.SymbolFlagsValue == 0 {
			return false
		}
	}
	partition := container != nil && container.Flags&(ast.SymbolFlagsClass|ast.SymbolFlagsInterface) != 0
	var previous *ast.Symbol
	var previousContained bool
	for _, symbol := range b.properties {
		contained := partition && c.isDeclarationContainedBy(symbol, container)
		if previous != nil {
			if contained && !previousContained {
				return false
			}
			if contained == previousContained && c.compareSymbols(previous, symbol) > 0 {
				return false
			}
		}
		previous, previousContained = symbol, contained
	}
	return true
}
func (p *pendingInstantiatedMembers) materializeWithLayout(t *StructuredType, names *memberNames) {
	t.pendingMembers = nil
	b := newPendingMemberBuilder(names)
	for i, source := range p.source.entries {
		state := p.state(i)
		if state == pendingMemberSkipped {
			continue
		}
		var symbol *ast.Symbol
		if p.source.positions[source.Name] == i {
			symbol = p.memberAt(i)
		} else if state == pendingMemberKept {
			symbol = source
		} else {
			// Earlier duplicates still allocate in the original source order.
			symbol = p.checker.newInstantiatedSymbol(source, p.mapper)
		}
		b.put(source.Name, symbol, false)
	}
	p.instantiated = nil
	for _, base := range p.bases {
		properties := base.properties
		if base.typ != nil {
			properties = base.typ.Properties()
		}
		for _, symbol := range properties {
			if !isStaticPrivateIdentifierProperty(symbol) {
				b.put(symbol.Name, symbol, true)
			}
		}
	}
	if b.orderedProperties(p.checker, t.symbol) {
		t.properties = b.properties
		p.source.lastMemberNames = names
		p.keepPropertiesOnDemand(t, names, b.properties)
		return
	}
	members := b.asTable()
	t.members = members
	t.properties = p.checker.getNamedMembers(members, t.symbol)
	p.keepTableOnDemand(t, members)
}
