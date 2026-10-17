package execute

import (
	"io"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/collections"
	"github.com/microsoft/typescript-go/internal/compiler"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/execute/tsc"
	"github.com/microsoft/typescript-go/internal/execute/watchmanager"
	"github.com/microsoft/typescript-go/internal/fswatch"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/tspath"
	"github.com/microsoft/typescript-go/internal/vfs"
	"github.com/microsoft/typescript-go/internal/vfs/osvfs"
)

type linkedWatchTestSystem struct {
	tsc.System
	cwd string
}

func (s linkedWatchTestSystem) FS() vfs.FS                  { return osvfs.FS() }
func (s linkedWatchTestSystem) GetCurrentDirectory() string { return s.cwd }

func TestWatchSourceCacheDetectsSameTimeLinkReplacement(t *testing.T) {
	dir := filepath.ToSlash(t.TempDir())
	first, second, link := dir+"/one.ts", dir+"/two.ts", dir+"/link.ts"
	stamp := time.Unix(1234567890, 0)
	for name, text := range map[string]string{first: "export const value = 1;", second: "export const value = 2;"} {
		if err := os.WriteFile(name, []byte(text), 0600); err != nil {
			t.Fatal(err)
		}
		if err := os.Chtimes(name, stamp, stamp); err != nil {
			t.Fatal(err)
		}
	}
	if err := os.Symlink(first, link); err != nil {
		t.Skipf("symlinks unavailable: %v", err)
	}
	host := &watchCompilerHost{
		CompilerHost: compiler.NewCompilerHost(dir, osvfs.FS(), dir, nil, nil),
		cache:        &collections.SyncMap[tspath.Path, *cachedSourceFile]{},
	}
	opts := ast.SourceFileParseOptions{FileName: link, Path: tspath.ToPath(link, dir, host.FS().UseCaseSensitiveFileNames())}
	original := host.GetSourceFile(opts)
	if original == nil {
		t.Fatal("initial linked input missing")
	}
	if host.GetSourceFile(opts) != original {
		t.Fatal("unchanged linked input should reuse parsed source")
	}
	if err := os.Remove(link); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(second, link); err != nil {
		t.Fatal(err)
	}
	replacement := host.GetSourceFile(opts)
	if replacement == nil || replacement == original || replacement.Text() != "export const value = 2;" {
		t.Fatal("same-time link replacement reused the old source")
	}
	if host.GetSourceFile(opts) != replacement {
		t.Fatal("new target should be cached")
	}
}

func TestWatchTracksPhysicalTargetsAndEvictsAllAliases(t *testing.T) {
	dir := filepath.ToSlash(t.TempDir())
	for _, subdir := range []string{"src", "shared", "next"} {
		if err := os.Mkdir(dir+"/"+subdir, 0700); err != nil {
			t.Fatal(err)
		}
	}
	target, next := dir+"/shared/value.ts", dir+"/next/value.ts"
	for _, name := range []string{target, next} {
		if err := os.WriteFile(name, []byte("export const value = 1;"), 0600); err != nil {
			t.Fatal(err)
		}
	}
	aliases := []string{dir + "/src/first.ts", dir + "/src/second.ts"}
	for _, alias := range aliases {
		if err := os.Symlink(target, alias); err != nil {
			t.Skipf("symlinks unavailable: %v", err)
		}
	}
	sys := linkedWatchTestSystem{cwd: dir}
	w := &Watcher{sys: sys, config: &tsoptions.ParsedCommandLine{ParsedConfig: &core.ParsedOptions{}}, sourceFileCache: &collections.SyncMap[tspath.Path, *cachedSourceFile]{}, wm: watchmanager.NewWatchManager(io.Discard, sys.FS().DirectoryExists)}
	caseSensitive := sys.FS().UseCaseSensitiveFileNames()
	physical := tspath.ToPath(target, dir, caseSensitive)
	seen := w.trackSeenFiles(aliases, dir, caseSensitive)
	if len(seen) != 3 || !w.seenFiles.Has(physical) {
		t.Fatalf("target not tracked once with both aliases: %v", seen)
	}
	desired := w.computeDesiredWatches(seen)
	if _, ok := desired[dir+"/shared"]; !ok {
		t.Fatalf("target directory not watched: %v", desired)
	}
	for _, alias := range aliases {
		w.sourceFileCache.Store(tspath.ToPath(alias, dir, caseSensitive), &cachedSourceFile{realPath: physical})
	}
	untouched := tspath.ToPath(dir+"/unrelated.ts", dir, caseSensitive)
	w.sourceFileCache.Store(untouched, &cachedSourceFile{realPath: untouched})
	changed := map[string]fswatch.EventKind{target: 0}
	if !w.isRelevantChange(changed) {
		t.Fatal("physical target edit deemed irrelevant")
	}
	w.evictChangedSourceFiles(changed)
	for _, alias := range aliases {
		if _, ok := w.sourceFileCache.Load(tspath.ToPath(alias, dir, caseSensitive)); ok {
			t.Fatalf("target edit left alias cached: %s", alias)
		}
	}
	if _, ok := w.sourceFileCache.Load(untouched); !ok {
		t.Fatal("unrelated source evicted")
	}
	for _, alias := range aliases {
		if err := os.Remove(alias); err != nil {
			t.Fatal(err)
		}
		if err := os.Symlink(next, alias); err != nil {
			t.Fatal(err)
		}
	}
	seen = w.trackSeenFiles(aliases, dir, caseSensitive)
	if w.seenFiles.Has(physical) || !w.seenFiles.Has(tspath.ToPath(next, dir, caseSensitive)) {
		t.Fatalf("retarget did not refresh dependencies: %v", seen)
	}
	desired = w.computeDesiredWatches(seen)
	if _, ok := desired[dir+"/next"]; !ok {
		t.Fatalf("replacement target directory not watched: %v", desired)
	}
	if _, ok := desired[dir+"/shared"]; ok {
		t.Fatalf("old target watch retained: %v", desired)
	}
}

func TestWatchAncestorEventsExcludeUnrelatedDirectories(t *testing.T) {
	dir := filepath.ToSlash(t.TempDir())
	project, unrelated := dir+"/project", dir+"/unrelated"
	for _, path := range []string{project, unrelated} {
		if err := os.Mkdir(path, 0700); err != nil {
			t.Fatal(err)
		}
	}
	sys := linkedWatchTestSystem{cwd: dir}
	w := &Watcher{
		sys:       sys,
		config:    &tsoptions.ParsedCommandLine{ParsedConfig: &core.ParsedOptions{}},
		seenFiles: collections.NewSetFromItems(tspath.ToPath(project+"/input.ts", dir, sys.FS().UseCaseSensitiveFileNames())),
		wm:        watchmanager.NewWatchManager(io.Discard, sys.FS().DirectoryExists),
	}
	w.wm.EnsureDefaultBackend()
	w.wm.Lock()
	err := w.wm.ReconcileWatches(map[string]bool{dir: false})
	w.wm.Unlock()
	if err != nil {
		t.Fatal(err)
	}
	defer w.wm.CloseAllWatches()
	for _, path := range []string{project, project + "/input.ts"} {
		if !w.isRelevantChange(map[string]fswatch.EventKind{path: fswatch.EventUpdate}) {
			t.Fatalf("input or ancestor creation is relevant: %s", path)
		}
	}
	if w.isRelevantChange(map[string]fswatch.EventKind{unrelated: fswatch.EventUpdate}) {
		t.Fatal("unrelated directory must not rebuild a project watched through its ancestor")
	}
	if err := os.Remove(project); err != nil {
		t.Fatal(err)
	}
	if !w.isRelevantChange(map[string]fswatch.EventKind{project: fswatch.EventDelete}) {
		t.Fatal("deleted dependency ancestor must still trigger a rebuild")
	}
}

func TestWatchAncestorReplacementEvictsSameTimeSources(t *testing.T) {
	dir := filepath.ToSlash(t.TempDir())
	project, file := dir+"/project", dir+"/project/input.ts"
	stamp := time.Unix(1234567890, 0)
	writeProject := func(text string) {
		t.Helper()
		if err := os.Mkdir(project, 0700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(file, []byte(text), 0600); err != nil {
			t.Fatal(err)
		}
		if err := os.Chtimes(file, stamp, stamp); err != nil {
			t.Fatal(err)
		}
	}
	writeProject("export const value = 1;")
	sys := linkedWatchTestSystem{cwd: dir}
	cache := &collections.SyncMap[tspath.Path, *cachedSourceFile]{}
	host := &watchCompilerHost{CompilerHost: compiler.NewCompilerHost(dir, sys.FS(), dir, nil, nil), cache: cache}
	opts := ast.SourceFileParseOptions{FileName: file, Path: tspath.ToPath(file, dir, sys.FS().UseCaseSensitiveFileNames())}
	original := host.GetSourceFile(opts)
	if original == nil {
		t.Fatal("initial source missing")
	}
	if err := os.Rename(project, dir+"/old-project"); err != nil {
		t.Fatal(err)
	}
	writeProject("export const value = 2;")
	w := &Watcher{sys: sys, sourceFileCache: cache, wm: watchmanager.NewWatchManager(io.Discard, sys.FS().DirectoryExists)}
	w.evictChangedSourceFiles(map[string]fswatch.EventKind{project: fswatch.EventUpdate})
	updated := host.GetSourceFile(opts)
	if updated == nil || updated == original || updated.Text() != "export const value = 2;" {
		t.Fatal("directory-only replacement reused stale source with unchanged path and timestamp")
	}
}
