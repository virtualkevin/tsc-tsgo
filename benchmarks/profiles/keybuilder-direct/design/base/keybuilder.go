package checker

import (
	"encoding/binary"

	"github.com/zeebo/xxh3"
)

// keyBuilder owns one serialization. Short keys hash the inline bytes directly;
// longer keys preserve the same streaming hash without retaining the full input.
// A builder must not be copied after its first write.
type keyBuilder struct {
	buf      [128]byte
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
	if b.overflow == nil && b.n < len(b.buf) {
		b.buf[b.n] = c
		b.n++
		return
	}
	b.writeBytes([]byte{c})
}

func (b *keyBuilder) writeUint32(value uint32) {
	var bytes [4]byte
	binary.LittleEndian.PutUint32(bytes[:], value)
	b.writeBytes(bytes[:])
}

func (b *keyBuilder) writeUint64(value uint64) {
	var bytes [8]byte
	binary.LittleEndian.PutUint64(bytes[:], value)
	b.writeBytes(bytes[:])
}
