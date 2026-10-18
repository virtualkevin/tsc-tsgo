package ast

import "unique"

// Name is a canonical, exact-byte name. Its zero value represents the empty
// string. It carries no symbol identity: distinct symbols may share one name.
// A live Name owns a strong reference to its canonical string descriptor.
// This experimental type is not yet used by production compiler storage.
type Name struct {
	handle unique.Handle[string]
}

func MakeName(text string) Name {
	if text == "" {
		return Name{}
	}
	return Name{handle: unique.Make(text)}
}

func (name Name) String() string {
	if name == (Name{}) {
		return ""
	}
	return name.handle.Value()
}

// Text marshaling retains string-shaped external representations, including
// map keys. Encoding formats retain their ordinary string encoding rules.
func (name Name) MarshalText() ([]byte, error) {
	return []byte(name.String()), nil
}

func (name *Name) UnmarshalText(text []byte) error {
	*name = MakeName(string(text))
	return nil
}
