package checker

import (
	"encoding/binary"

	"github.com/zeebo/xxh3"
)

// keyBuilder owns one serialization. Short keys hash the inline bytes directly;
// longer keys preserve the same streaming hash without retaining the full input.
// A builder must not be copied after its first write or explicit stream creation.
type keyBuilder struct {
	buf [128]byte
	// n is the inline length, saturated to len(buf) after entering streaming mode.
	n        int
	overflow *xxh3.Hasher
}

func (b *keyBuilder) hash() CacheHashKey {
	if b.overflow != nil {
		return CacheHashKey(b.overflow.Sum128())
	}
	return CacheHashKey(xxh3.Hash128(b.buf[:b.n]))
}

func (b *keyBuilder) stream() *xxh3.Hasher {
	if b.overflow == nil {
		b.overflow = new(xxh3.Hasher)
		_, _ = b.overflow.Write(b.buf[:b.n])
		b.n = len(b.buf)
	}
	return b.overflow
}

func (b *keyBuilder) writeBytes(data []byte) {
	if b.overflow == nil && len(data) <= len(b.buf)-b.n {
		b.n += copy(b.buf[b.n:], data)
		return
	}
	_, _ = b.stream().Write(data)
}

func (b *keyBuilder) writeString(s string) {
	if b.overflow == nil && len(s) <= len(b.buf)-b.n {
		b.n += copy(b.buf[b.n:], s)
		return
	}
	_, _ = b.stream().WriteString(s)
}

func (b *keyBuilder) writeByte(c byte) {
	if b.n < len(b.buf) {
		b.buf[b.n] = c
		b.n++
	} else {
		b.writeByteOverflow(c)
	}
}

func (b *keyBuilder) writeUint32(value uint32) {
	if b.n <= len(b.buf)-4 {
		binary.LittleEndian.PutUint32(b.buf[b.n:], value)
		b.n += 4
	} else {
		b.writeUint32Overflow(value)
	}
}

func (b *keyBuilder) writeUint64(value uint64) {
	if b.n <= len(b.buf)-8 {
		binary.LittleEndian.PutUint64(b.buf[b.n:], value)
		b.n += 8
	} else {
		b.writeUint64Overflow(value)
	}
}

// Separate the temporary payload and streaming calls from the short writers.
// These paths run only after the complete integer no longer fits inline.
func (b *keyBuilder) writeByteOverflow(value byte) {
	_, _ = b.stream().Write([]byte{value})
}

func (b *keyBuilder) writeUint32Overflow(value uint32) {
	var bytes [4]byte
	binary.LittleEndian.PutUint32(bytes[:], value)
	_, _ = b.stream().Write(bytes[:])
}

func (b *keyBuilder) writeUint64Overflow(value uint64) {
	var bytes [8]byte
	binary.LittleEndian.PutUint64(bytes[:], value)
	_, _ = b.stream().Write(bytes[:])
}
