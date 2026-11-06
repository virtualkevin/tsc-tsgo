package checker

// setFreshType preserves the distinction between an allocated fresh form and a
// completed pair. The regular form owns the forward link; the fresh form owns
// the backward link and uses its canonical embedded header as the forward link.
func (t *LiteralType) setFreshType(f *Type) {
	if t.literalState&2 != 0 {
		if f != t.data.AsType() {
			panic("fresh literal must point to itself")
		}
		t.literalState |= 4
	} else {
		t.literalPartner = f
	}
}
