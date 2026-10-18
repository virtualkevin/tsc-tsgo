package ast

import (
	"encoding/json"
	"fmt"
	"runtime"
	"strings"
	"sync"
	"testing"
)

func TestCanonicalNameExactBytes(t *testing.T) {
	texts := []string{"", "a", "__call", "\xfecall", "#private", "a\x00b", "\xff", "é", "e\u0301", "01", "1"}
	for i, text := range texts {
		name := MakeName(text)
		if name.String() != text || name != MakeName(strings.Clone(text)) {
			t.Fatalf("round trip/canonical identity failed for %q", text)
		}
		for j, other := range texts {
			if (name == MakeName(other)) != (i == j) {
				t.Fatalf("byte identity changed: %q / %q", text, other)
			}
		}
	}
	if MakeName("") != (Name{}) || (Name{}).String() != "" {
		t.Fatal("empty name has multiple representations")
	}
}

func TestCanonicalNameConcurrentLifetime(t *testing.T) {
	text := "live-name-" + strings.Repeat("x", 1024)
	root := MakeName(text)
	var wg sync.WaitGroup
	for range 8 {
		wg.Go(func() {
			for range 1000 {
				if got := MakeName(strings.Clone(text)); got != root || got.String() != text {
					t.Error("live canonical identity changed")
					return
				}
			}
		})
	}
	for range 3 {
		runtime.GC()
	}
	wg.Wait()
	if root != MakeName(text) {
		t.Fatal("live handle failed across GC")
	}
	runtime.KeepAlive(root)
}

func TestCanonicalNameTextBoundary(t *testing.T) {
	for _, text := range []string{"", "plain", "\xfecall", "\x00\xff", "\"\\\n", "é"} {
		name := MakeName(text)
		bytes, err := name.MarshalText()
		if err != nil || string(bytes) != text {
			t.Fatal("raw text marshaling changed bytes")
		}
		var decoded Name
		if err := decoded.UnmarshalText(bytes); err != nil || decoded != name {
			t.Fatal("raw text decode changed canonical identity")
		}
		if len(bytes) != 0 {
			bytes[0] ^= 0x7f
			if decoded.String() != text {
				t.Fatal("decoded name aliases mutable input")
			}
		}
		want, _ := json.Marshal(text)
		got, err := json.Marshal(name)
		if err != nil || string(got) != string(want) {
			t.Fatalf("JSON representation changed: %s / %s", got, want)
		}
		// JSON's existing string behavior replaces invalid UTF-8; compare to
		// string decoding, not an impossible lossless invalid-UTF8 round trip.
		var decodedString string
		if err := json.Unmarshal(want, &decodedString); err != nil {
			t.Fatal(err)
		}
		if err := json.Unmarshal(got, &decoded); err != nil || decoded.String() != decodedString {
			t.Fatal("JSON decoding differs from string decoding")
		}
		if fmt.Sprintf("%s / %q", name, name) != fmt.Sprintf("%s / %q", text, text) {
			t.Fatal("string/quoted diagnostic formatting changed")
		}
	}
}
