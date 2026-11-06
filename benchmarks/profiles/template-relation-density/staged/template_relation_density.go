package checker

import (
	"encoding/json"
	"math/bits"
	"os"
)

type densityTileKey struct {
	Packed   uint64
	Relation uint8
}
type densityRow struct {
	Relation                                                          uint8
	Writes, NonPlain, Unpackable, Recorded, Repeated, Dropped, Unique uint64
	Tiles                                                             int
	Occupancy                                                         [257]uint64
}
type templateRelationDensity struct {
	tiles map[densityTileKey]*[4]uint64
	rows  [5]densityRow
	limit int
}

func newTemplateRelationDensity() *templateRelationDensity {
	if os.Getenv("TSC_GO_TEMPLATE_RELATION_DENSITY") == "" {
		return nil
	}
	return &templateRelationDensity{tiles: make(map[densityTileKey]*[4]uint64), limit: 131072}
}

// Observes only ordinary recursive failure writes, after the original cache write.
// This measures ever-written plain failures, not current relation-cache contents.
func (c *Checker) observeTemplateFailure(source, target *Type, state IntersectionState, relation *Relation, result RelationComparisonResult) {
	o := c.templateRelationDensity
	if target.flags != TypeFlagsTemplateLiteral || (source.flags != TypeFlagsTemplateLiteral && source.flags != TypeFlagsStringLiteral) {
		return
	}
	var kind uint8
	switch relation {
	case c.assignableRelation:
		kind = 0
	case c.comparableRelation:
		kind = 1
	case c.identityRelation:
		kind = 2
	case c.subtypeRelation:
		kind = 3
	case c.strictSubtypeRelation:
		kind = 4
	default:
		panic("density unknown relation")
	}
	row := &o.rows[kind]
	row.Relation = kind
	row.Writes++
	if result != RelationComparisonResultFailed {
		row.NonPlain++
		return
	}
	a, b := source.id, target.id
	if kind == 2 && a > b {
		a, b = b, a
	}
	if a == 0 || b == 0 || a >= 1<<30 || b >= 1<<30 || state > (IntersectionStateSource|IntersectionStateTarget) || source.objectFlags&ObjectFlagsReference != 0 || target.objectFlags&ObjectFlagsReference != 0 {
		row.Unpackable++
		return
	}
	packed := uint64(a)<<32 | uint64(b)<<2 | uint64(state)
	key := densityTileKey{packed &^ uint64(15<<32|15<<2), kind}
	block := o.tiles[key]
	if block == nil {
		if len(o.tiles) >= o.limit {
			row.Dropped++
			return
		}
		block = new([4]uint64)
		o.tiles[key] = block
	}
	index := uint((a&15)<<4 | (b & 15))
	word, mask := index>>6, uint64(1)<<(index&63)
	row.Recorded++
	if block[word]&mask != 0 {
		row.Repeated++
	} else {
		block[word] |= mask
		row.Unique++
	}
}

type TemplateRelationDensitySnapshot struct {
	CheckerID uint32
	TileLimit int
	Tiles     int
	Rows      [5]densityRow
}

func (c *Checker) TemplateRelationDensitySnapshot() (TemplateRelationDensitySnapshot, bool) {
	o := c.templateRelationDensity
	if o == nil {
		return TemplateRelationDensitySnapshot{}, false
	}
	rows := o.rows
	for kind := range rows {
		rows[kind].Relation = uint8(kind)
	}
	for key, block := range o.tiles {
		n := bits.OnesCount64(block[0]) + bits.OnesCount64(block[1]) + bits.OnesCount64(block[2]) + bits.OnesCount64(block[3])
		if n == 0 {
			panic("empty density tile")
		}
		rows[key.Relation].Tiles++
		rows[key.Relation].Occupancy[n]++
	}
	return TemplateRelationDensitySnapshot{c.id, o.limit, len(o.tiles), rows}, true
}
func WriteTemplateRelationDensitySnapshots(path string, owners []TemplateRelationDensitySnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []TemplateRelationDensitySnapshot
	}{1, "Ever-written ordinary recursive plain failures for exact string-literal/template sources and template targets; fixed 16x16 ID tiles with intersection state/relation identity preserved. Cap 131072 tiles per checker, known tiles continue after saturation. Not current cache size, all relation writes, type equivalence, allocation/RSS, or speedup.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
