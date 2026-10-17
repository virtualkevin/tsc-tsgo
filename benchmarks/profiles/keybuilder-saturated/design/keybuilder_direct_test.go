package checker

import (
	"encoding/binary"
	"fmt"
	"strings"
	"testing"
)

// Existing mixed-write tests spill first through uint32. Exercise each new
// direct writer at every prefix alignment, including uint64's first overflow.
func TestBufferedDirectIntegerBoundaryTransitions(t *testing.T) {
	for _, width := range []int{1, 4, 8} {
		for prefix := 0; prefix <= 129; prefix++ {
			t.Run(fmt.Sprintf("width%d/prefix%d", width, prefix), func(t *testing.T) {
				data := strings.Repeat("p", prefix)
				var b keyBuilder
				b.writeString(data)
				assertBufferedKeyBytes(t, &b, []byte(data))
				expected := []byte(data)
				switch width {
				case 1:
					b.writeByte(0xe5)
					expected = append(expected, 0xe5)
				case 4:
					b.writeUint32(0x89abcdef)
					expected = binary.LittleEndian.AppendUint32(expected, 0x89abcdef)
				case 8:
					b.writeUint64(0x0123456789abcdef)
					expected = binary.LittleEndian.AppendUint64(expected, 0x0123456789abcdef)
				}
				assertBufferedKeyBytes(t, &b, expected)
				if (b.overflow != nil) != (prefix+width > 128) {
					t.Fatal("incorrect direct-writer overflow boundary")
				}
				// Exercise continuation after exact fit and after first/existing overflow.
				b.writeUint64(0xfedcba9876543210)
				expected = binary.LittleEndian.AppendUint64(expected, 0xfedcba9876543210)
				assertBufferedKeyBytes(t, &b, expected)
			})
		}
	}
}

// Explicit streaming at a partial prefix must preserve exactly the written
// prefix, then route every primitive continuation through that same stream.
func TestBufferedKeyBuilderSaturatedStreamingLength(t *testing.T) {
	for _, prefix := range []int{0, 1, 120, 121, 124, 125, 127, 128} {
		t.Run(fmt.Sprintf("prefix%d", prefix), func(t *testing.T) {
			var b keyBuilder
			expected := []byte(strings.Repeat("p", prefix))
			b.writeBytes(expected)
			if b.n != prefix || b.overflow != nil {
				t.Fatal("inline length or streaming state changed before transition")
			}
			stream := b.stream()
			if b.n != len(b.buf) || b.overflow != stream || b.stream() != stream {
				t.Fatal("streaming transition did not preserve saturated length and identity")
			}
			assertBufferedKeyBytes(t, &b, expected)
			b.writeBytes(nil)
			b.writeString("")
			assertBufferedKeyBytes(t, &b, expected)
			b.writeByte(0xe5)
			expected = append(expected, 0xe5)
			assertBufferedKeyBytes(t, &b, expected)
			b.writeUint32(0x89abcdef)
			expected = binary.LittleEndian.AppendUint32(expected, 0x89abcdef)
			assertBufferedKeyBytes(t, &b, expected)
			b.writeUint64(0x0123456789abcdef)
			expected = binary.LittleEndian.AppendUint64(expected, 0x0123456789abcdef)
			assertBufferedKeyBytes(t, &b, expected)
			if b.n != len(b.buf) || b.overflow != stream {
				t.Fatal("streaming continuation changed saturated length or identity")
			}
		})
	}
}
