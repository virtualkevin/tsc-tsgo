package checker

import "testing"

func TestUnmatchedTemplateIndexKey(t *testing.T) {
	c := templateCacheTestChecker()
	target := c.newTemplateLiteralType([]string{"ab", "bc"}, []*Type{c.stringType}).AsTemplateLiteralType()
	pattern := func(start, end string, placeholder *Type) *Type {
		return c.newTemplateLiteralType([]string{start, end}, []*Type{placeholder})
	}
	for _, tc := range []struct {
		name   string
		source *Type
		reject bool
	}{
		{"overlapping literal ends", c.getStringLiteralType("abc"), true},
		{"empty placeholder", c.getStringLiteralType("abbc"), false},
		{"unicode interior", c.getStringLiteralType("ab🐈bc"), false},
		{"wrong prefix", pattern("a", "bc", c.stringType), true},
		{"wrong suffix", pattern("ab", "c", c.stringType), true},
		{"compatible pattern", pattern("abcd", "xyzbc", c.stringType), false},
		{"nonconcrete placeholder", pattern("x", "y", c.wildcardType), false},
		{"unrestricted string", c.stringType, false},
	} {
		t.Run(tc.name, func(t *testing.T) {
			if got := unmatchedTemplateIndexKey(tc.source, target); got != tc.reject {
				t.Fatalf("early rejection = %v, want %v", got, tc.reject)
			}
		})
	}
}
