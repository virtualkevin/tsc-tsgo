package bundled

import (
	"path/filepath"
	"testing"
)

func TestLibraryDirectoryOverride(t *testing.T) {
	path := t.TempDir()
	t.Setenv("TSC_TS_LIB_DIR", path)
	if got := LibPath(); got != filepath.ToSlash(path) {
		t.Fatalf("LibPath() = %q, want %q", got, filepath.ToSlash(path))
	}
}

func TestRelativeLibraryDirectoryOverride(t *testing.T) {
	t.Setenv("TSC_TS_LIB_DIR", "custom-libs")
	want, err := filepath.Abs("custom-libs")
	if err != nil {
		t.Fatal(err)
	}
	if got := LibPath(); got != filepath.ToSlash(want) {
		t.Fatalf("LibPath() = %q, want %q", got, filepath.ToSlash(want))
	}
}

func TestDefaultLibraryDirectory(t *testing.T) {
	t.Setenv("TSC_TS_LIB_DIR", "")
	if got := LibPath(); got != libPath() {
		t.Fatalf("LibPath() = %q, want embedded path %q", got, libPath())
	}
}
