package checker

import (
	"encoding/json"
	"github.com/microsoft/typescript-go/internal/ast"
	"os"
	"unsafe"
	"weak"
)

type windowKey struct {
	input  weak.Pointer[Type]
	mapper weak.Pointer[TypeMapper]
}
type windowState struct {
	epoch       uint64
	node        weak.Pointer[ast.Node]
	flags       TypeFlags
	objectFlags ObjectFlags
}
type windowEntry struct {
	key     windowKey
	state   windowState
	result  weak.Pointer[Type]
	serial  uint64
	pending bool
}
type WindowCounts struct {
	Requests, Aliased, Unsampled, Selected                                                              uint64
	FirstInWindow, RepeatedCompleted, NestedPending, Evictions                                          uint64
	SameObservedState, ChangedObservedState                                                             uint64
	FinishedFirst, FinishedRepeated, SameResult, ChangedResult, SameStateAndResult, EvictedBeforeFinish uint64
	FirstDescendantInstantiations, RepeatedDescendantInstantiations, CounterWraps                       uint64
}
type instantiationWindow struct {
	slots         []windowEntry
	mask          uint64
	serial, epoch uint64
	counts        WindowCounts
}
type windowToken struct {
	index             int
	serial            uint64
	before            uint32
	repeat, sameState bool
	old               weak.Pointer[Type]
}

func newInstantiationWindow() *instantiationWindow {
	if os.Getenv("TSC_GO_INSTANTIATION_WINDOW") == "" {
		return nil
	}
	return &instantiationWindow{slots: make([]windowEntry, 4096), mask: 127}
}
func windowHash(t *Type, m *TypeMapper) uint64 {
	// Scalar sampling only; never reconstruct pointers or use addresses as roots.
	// The pinned runtime is non-moving, as with the production pointer table.
	x := uint64(uintptr(unsafe.Pointer(m))) ^ uint64(t.id)*0x9e3779b97f4a7c15
	x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9
	x = (x ^ (x >> 27)) * 0x94d049bb133111eb
	return x ^ (x >> 31)
}
func (s *instantiationWindow) begin(c *Checker, t *Type, m *TypeMapper, alias *TypeAlias) windowToken {
	s.counts.Requests++
	if alias != nil {
		s.counts.Aliased++
		return windowToken{}
	}
	hash := windowHash(t, m)
	if hash&s.mask != 0 {
		s.counts.Unsampled++
		return windowToken{}
	}
	s.counts.Selected++
	// Selection bits and directory-index bits are disjoint for mask127.
	index := int((hash >> 7) % uint64(len(s.slots)))
	e := &s.slots[index]
	key := windowKey{weak.Make(t), weak.Make(m)}
	state := windowState{s.epoch, weak.Make(c.currentNode), t.flags, t.objectFlags}
	token := windowToken{index: index, before: c.TotalInstantiationCount}
	if e.serial != 0 && e.key == key {
		if e.pending {
			s.counts.NestedPending++
			return windowToken{}
		}
		s.counts.RepeatedCompleted++
		token.repeat = true
		token.old = e.result
		token.sameState = e.state == state
		if token.sameState {
			s.counts.SameObservedState++
		} else {
			s.counts.ChangedObservedState++
		}
	} else {
		s.counts.FirstInWindow++
		if e.serial != 0 {
			s.counts.Evictions++
		}
	}
	s.serial++
	token.serial = s.serial
	*e = windowEntry{key: key, state: state, serial: token.serial, pending: true}
	return token
}
func (s *instantiationWindow) finish(c *Checker, token windowToken, result *Type) {
	if token.serial == 0 {
		return
	}
	e := &s.slots[token.index]
	if e.serial != token.serial {
		s.counts.EvictedBeforeFinish++
		return
	}
	e.pending = false
	e.result = weak.Make(result)
	var descendants uint64
	if c.TotalInstantiationCount < token.before {
		s.counts.CounterWraps++
	} else {
		descendants = uint64(c.TotalInstantiationCount - token.before)
	}
	if token.repeat {
		s.counts.FinishedRepeated++
		s.counts.RepeatedDescendantInstantiations += descendants
		if e.result == token.old {
			s.counts.SameResult++
			if token.sameState {
				s.counts.SameStateAndResult++
			}
		} else {
			s.counts.ChangedResult++
		}
	} else {
		s.counts.FinishedFirst++
		s.counts.FirstDescendantInstantiations += descendants
	}
}

type InstantiationWindowSnapshot struct {
	CheckerID    uint32
	Slots        int
	SamplingMask uint64
	Epoch        uint64
	Pending      int
	Counts       WindowCounts
}

func (c *Checker) InstantiationWindowSnapshot() (InstantiationWindowSnapshot, bool) {
	s := c.instantiationWindow
	if s == nil {
		return InstantiationWindowSnapshot{}, false
	}
	pending := 0
	for _, e := range s.slots {
		if e.pending {
			pending++
		}
	}
	return InstantiationWindowSnapshot{c.id, len(s.slots), s.mask, s.epoch, pending, s.counts}, true
}
func WriteInstantiationWindowSnapshots(path string, owners []InstantiationWindowSnapshot) error {
	f, err := os.OpenFile(path, os.O_CREATE|os.O_EXCL|os.O_WRONLY, 0o644)
	if err != nil {
		return err
	}
	report := struct {
		SchemaVersion int
		Scope         string
		Owners        []InstantiationWindowSnapshot
	}{1, "Alias-free actual instantiation misses, hash-selected1/128keys across execution,4096direct-mapped weak slots per checker. Eviction censors repetition. Selected state and pointer identity do not establish semantic equivalence; descendant counters overlap recursively and are not CPU or removable work.", owners}
	err = json.NewEncoder(f).Encode(report)
	closeErr := f.Close()
	if err != nil {
		return err
	}
	return closeErr
}
