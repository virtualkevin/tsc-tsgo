package ast

import (
	"encoding/json"
	"math/bits"
	"os"
	"strings"
	"sync"
)

const (
	NameConstructionIdentifier = iota
	NameConstructionBinderSymbol
	NameConstructionCheckerSymbol
)

type nameConstructionCounts struct {
	Requests, NameBytes, Empty, Distinct, DistinctBytes, Untracked uint64
	LengthBuckets                                                  [65]uint64
}
type nameConstructionCensus struct {
	sync.Mutex
	Categories              [3]nameConstructionCounts
	Distinct, DistinctBytes uint64
	MembershipMasks         [8]uint64
	LimitKeys               int
	LimitBytes              uint64
	names                   map[string]int
	masks                   []uint8
}

func (c *nameConstructionCensus) record(kind int, name string) {
	c.Lock()
	defer c.Unlock()
	p := &c.Categories[kind]
	p.Requests++
	p.NameBytes += uint64(len(name))
	p.LengthBuckets[bits.Len(uint(len(name)))]++
	if name == "" {
		p.Empty++
	}
	bit := uint8(1 << kind)
	if index, ok := c.names[name]; ok {
		mask := c.masks[index]
		if mask&bit == 0 {
			p.Distinct++
			p.DistinctBytes += uint64(len(name))
			c.MembershipMasks[mask]--
			c.MembershipMasks[mask|bit]++
			c.masks[index] = mask | bit
		}
		return
	}
	if len(c.names) >= c.LimitKeys || uint64(len(name)) > c.LimitBytes-c.DistinctBytes {
		p.Untracked++
		return
	}
	if c.names == nil {
		c.names = make(map[string]int)
	}
	// Retain exact name bytes, not the backing source-file string. No name text
	// or semantic object is serialized. Existing map keys are never reassigned,
	// so a category update cannot replace the cloned key with a source substring.
	// Counts are construction events, not live objects.
	c.names[strings.Clone(name)] = len(c.masks)
	c.masks = append(c.masks, bit)
	c.Distinct++
	c.DistinctBytes += uint64(len(name))
	c.MembershipMasks[bit]++
	p.Distinct++
	p.DistinctBytes += uint64(len(name))
}

var nameConstructionPath = os.Getenv("TSC_GO_NAME_CONSTRUCTION_CENSUS")
var constructionNames = nameConstructionCensus{LimitKeys: 1 << 20, LimitBytes: 64 << 20}

func ObserveNameConstruction(kind int, name string) {
	if nameConstructionPath == "" {
		return
	}
	constructionNames.record(kind, name)
}
func WriteNameConstructionCensus() error {
	if nameConstructionPath == "" {
		return nil
	}
	constructionNames.Lock()
	defer constructionNames.Unlock()
	report := struct {
		Scope  string
		Labels [3]string
		Counts *nameConstructionCensus
	}{
		"Exact-byte names observed at NodeFactory.NewIdentifier, Binder.newSymbol and Checker.newSymbol. Counts construction events, including temporary/repeated construction, not live objects, total symbol writes/copies, query conversion frequency, semantic equivalence or timing. Bounded map; when limits are reached untracked events may repeat omitted names. Shared mutex and cloned-name retention perturb execution. Membership bit 0 identifier, bit 1 binder symbol, bit 2 checker symbol. Length bucket is bits.Len(byte length). No name text serialized.",
		[3]string{"identifier-constructor", "binder-symbol-constructor", "checker-symbol-constructor"}, &constructionNames}
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(nameConstructionPath, append(data, '\n'), 0600)
}
