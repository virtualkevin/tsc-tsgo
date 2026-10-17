package ast

import (
	"github.com/microsoft/typescript-go/internal/core"
	"sync/atomic"
)

// Allocation handles are independent of lazy semantic SymbolIds. Each allocator
// exclusively owns its reserved blocks; blocks are never reused. Exhaustion
// leaves symbols unindexed, so ordinary pointer-key lookup remains available.
var symbolLinkBlock atomic.Uint32

const symbolLinkBlockShift = 8
const symbolLinkBlockSize = 1 << symbolLinkBlockShift
const maxSymbolLinkBlock = ^uint32(0) >> symbolLinkBlockShift

type symbolLinkCursor struct {
	next      uint32
	remaining uint16
	exhausted bool
}

func reserveSymbolLinkBlock(counter *atomic.Uint32) uint32 {
	for {
		old := counter.Load()
		if old >= maxSymbolLinkBlock {
			return 0
		}
		if counter.CompareAndSwap(old, old+1) {
			return old + 1
		}
	}
}

func (c *symbolLinkCursor) take(counter *atomic.Uint32) uint32 {
	if c.remaining == 0 {
		if c.exhausted {
			return 0
		}
		block := reserveSymbolLinkBlock(counter)
		if block == 0 {
			c.exhausted = true
			return 0
		}
		c.next = block << symbolLinkBlockShift
		c.remaining = symbolLinkBlockSize
	}
	result := c.next
	c.next++ // Last valid handle may wrap; remaining reaches zero simultaneously.
	c.remaining--
	return result
}

// SymbolAllocator preserves Arena's typed allocation and published-pointer
// lifetime. Allocation handles are assigned before a symbol is published.
// Like Arena, an allocator requires exclusive mutation and must not be copied
// after use. Resetting it abandons unused handles rather than recycling them.
type SymbolAllocator struct {
	arena  core.Arena[Symbol]
	cursor symbolLinkCursor
}

func (a *SymbolAllocator) New() *Symbol {
	symbol := a.arena.New()
	symbol.linkIndex = a.cursor.take(&symbolLinkBlock)
	return symbol
}
