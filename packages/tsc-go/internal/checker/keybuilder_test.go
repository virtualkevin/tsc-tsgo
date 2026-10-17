package checker

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"strings"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/zeebo/xxh3"
)

func assertBufferedKeyBytes(t *testing.T, b *keyBuilder, expected []byte) {
	t.Helper()
	var legacy xxh3.Hasher
	// An independent streaming oracle: does not call the new builder writers.
	for start := 0; start < len(expected); {
		end := min(start+7, len(expected))
		_, _ = legacy.Write(expected[start:end])
		start = end
	}
	want := CacheHashKey(legacy.Sum128())
	if got := b.hash(); got != want || got != CacheHashKey(xxh3.Hash128(expected)) {
		t.Fatalf("%d-byte key hash mismatch: got %v, want %v", len(expected), got, want)
	}
	if b.hash() != want {
		t.Fatal("hash changed without a write")
	}
	if b.overflow == nil && !bytes.Equal(b.buf[:b.n], expected) {
		t.Fatal("inline serialization bytes changed")
	}
}

func TestBufferedKeyBuilderStreamingBoundaries(t *testing.T) {
	lengths := []int{0, 1, 3, 4, 8, 9, 16, 17, 31, 32, 64, 127, 128, 129, 239, 240, 241, 1023, 1024, 1087, 1088, 1089, 4096, 4097}
	for _, n := range lengths {
		for _, chunk := range []int{1, 3, 4, 7, 8, 31, 127, 128, 129, 1025} {
			t.Run(fmt.Sprintf("length%d/chunk%d", n, chunk), func(t *testing.T) {
				data := make([]byte, n)
				for i := range data {
					data[i] = byte(i*37 + 11)
				}
				var b keyBuilder
				assertBufferedKeyBytes(t, &b, nil)
				for start := 0; start < n; {
					end := min(start+chunk, n)
					// Alternating string/byte writes exercise both transition paths.
					if start%2 == 0 {
						b.writeString(string(data[start:end]))
					} else {
						b.writeBytes(data[start:end])
					}
					assertBufferedKeyBytes(t, &b, data[:end])
					start = end
				}
				if (b.overflow == nil) != (n <= 128) {
					t.Fatal("incorrect overflow boundary")
				}
				b.writeString("")
				b.writeBytes(nil)
				assertBufferedKeyBytes(t, &b, data)
				// A hash query is nonfinal: a later write must extend the same stream.
				b.writeByte(0xff)
				assertBufferedKeyBytes(t, &b, append(data, 0xff))
			})
		}
	}
}

func TestBufferedKeyBuilderIntegerEncoding(t *testing.T) {
	var b keyBuilder
	var expected []byte
	for i := 0; i < 20; i++ {
		b.writeByte(byte(i))
		expected = append(expected, byte(i))
		b.writeUint32(^uint32(0) - uint32(i))
		expected = binary.LittleEndian.AppendUint32(expected, ^uint32(0)-uint32(i))
		b.writeUint64(uint64(i)<<48 | 0x01020304)
		expected = binary.LittleEndian.AppendUint64(expected, uint64(i)<<48|0x01020304)
		b.writeInt(-i - 1)
		expected = binary.LittleEndian.AppendUint64(expected, uint64(-i-1))
		b.writeString("\x00é\xff")
		expected = append(expected, []byte("\x00é\xff")...)
		assertBufferedKeyBytes(t, &b, expected)
	}
}

func TestBufferedKeyBuilderPreservesLazyIdAssignmentOrder(t *testing.T) {
	symbol, marker := &ast.Symbol{}, &ast.Symbol{}
	node, nodeMarker := &ast.Node{}, &ast.Node{}
	var b keyBuilder
	b.writeSymbol(symbol)
	markerID := ast.GetSymbolId(marker)
	b.writeNode(node)
	nodeMarkerID := ast.GetNodeId(nodeMarker)
	// IDs must be assigned at the write, not deferred until hash().
	if ast.GetSymbolId(symbol) >= markerID || ast.GetNodeId(node) >= nodeMarkerID {
		t.Fatal("lazy ID assignment moved past the write")
	}
	expected := binary.LittleEndian.AppendUint64(nil, uint64(ast.GetSymbolId(symbol)))
	expected = binary.LittleEndian.AppendUint64(expected, uint64(ast.GetNodeId(node)))
	b.writeNode(nil)
	assertBufferedKeyBytes(t, &b, expected)
}

func TestBufferedKeyBuilderAliasAndTypeEncoding(t *testing.T) {
	for _, count := range []int{0, 1, 28, 40} {
		t.Run(fmt.Sprint(count), func(t *testing.T) {
			types := make([]*Type, count)
			for i := range types {
				types[i] = &Type{id: TypeId(i + 1)}
			}
			alias := &TypeAlias{symbol: &ast.Symbol{}, typeArguments: types}
			var b keyBuilder
			b.writeType(&Type{id: ^TypeId(0)})
			b.writeAlias(nil)
			b.writeAlias(alias)
			expected := binary.LittleEndian.AppendUint32(nil, ^uint32(0))
			expected = append(expected, 0, 1)
			expected = binary.LittleEndian.AppendUint64(expected, uint64(ast.GetSymbolId(alias.symbol)))
			expected = binary.LittleEndian.AppendUint64(expected, uint64(count))
			for _, typ := range types {
				expected = binary.LittleEndian.AppendUint32(expected, uint32(typ.id))
			}
			assertBufferedKeyBytes(t, &b, expected)
		})
	}
}

func TestBufferedKeyBuilderNestedBuildersAreIndependent(t *testing.T) {
	var outer keyBuilder
	outer.writeString(strings.Repeat("outer", 30))
	before := outer.hash()
	for _, n := range []int{0, 10, 128, 129, 2048} {
		var inner keyBuilder
		data := strings.Repeat("x", n)
		inner.writeString(data)
		assertBufferedKeyBytes(t, &inner, []byte(data))
		if outer.hash() != before {
			t.Fatal("nested builder modified outer stream")
		}
	}
	outer.writeString("suffix")
	assertBufferedKeyBytes(t, &outer, []byte(strings.Repeat("outer", 30)+"suffix"))
}

func TestBufferedTemplateKeyRetainsTextBoundaries(t *testing.T) {
	types := []*Type{{id: 3}, {id: 17}}
	for _, texts := range [][]string{{"a\x00", "b"}, {"a", "\x00b"}, {strings.Repeat("p", 200), "", "tail"}} {
		expected := binary.LittleEndian.AppendUint64(nil, uint64(len(types)))
		for _, typ := range types {
			expected = binary.LittleEndian.AppendUint32(expected, uint32(typ.id))
		}
		expected = append(expected, '|')
		for _, s := range texts {
			expected = binary.LittleEndian.AppendUint64(expected, uint64(len(s)))
		}
		expected = append(expected, '|')
		for _, s := range texts {
			expected = append(expected, s...)
		}
		var legacy xxh3.Hasher
		_, _ = legacy.Write(expected)
		if getTemplateTypeKey(texts, types) != CacheHashKey(legacy.Sum128()) {
			t.Fatal("template serialization changed")
		}
	}
	if getTemplateTypeKey([]string{"a\x00", "b"}, types) == getTemplateTypeKey([]string{"a", "\x00b"}, types) {
		t.Fatal("text boundaries merged")
	}
}
