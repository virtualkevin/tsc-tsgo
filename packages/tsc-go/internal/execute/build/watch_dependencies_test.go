package build

import (
	"sync/atomic"
	"testing"

	"github.com/microsoft/typescript-go/internal/ast"
	"github.com/microsoft/typescript-go/internal/collections"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/fswatch"
	"github.com/microsoft/typescript-go/internal/tsoptions"
	"github.com/microsoft/typescript-go/internal/tspath"
)

func TestWatchMissingConfigRetriesOnlyItsOwnDirectoryEvents(t *testing.T) {
	for _, test := range []struct {
		name, path string
		kind       fswatch.EventKind
		want       bool
	}{
		{"recreated project", "/tmp/project/proj", fswatch.EventUpdate, true},
		{"already removed project duplicate", "/tmp/project/proj", fswatch.EventDelete, false},
		{"created config", "/tmp/project/proj/tsconfig.json", fswatch.EventUpdate, true},
		{"unrelated temporary checkout", "/tmp/another-project", fswatch.EventUpdate, false},
		{"similarly named checkout", "/tmp/project/proj-other", fswatch.EventUpdate, false},
	} {
		t.Run(test.name, func(t *testing.T) {
			const config = "/tmp/project/proj/tsconfig.json"
			o := &Orchestrator{host: &host{}, tasks: &collections.SyncMap[tspath.Path, *BuildTask]{}, order: []string{config}, comparePathsOptions: tspath.ComparePathsOptions{CurrentDirectory: "/tmp/project", UseCaseSensitiveFileNames: true}}
			path := o.toPath(config)
			task := &BuildTask{config: config, configMissing: true}
			o.tasks.Store(path, task)
			o.host.resolvedReferences.store(path, nil) // Cached failure from the previous deleted-project build.
			var needsConfig, needsBuild atomic.Bool
			o.checkTasksForEventChanges(map[string]fswatch.EventKind{test.path: test.kind}, &needsConfig, &needsBuild)
			if needsConfig.Load() != test.want || needsBuild.Load() != test.want || task.dirty != test.want {
				t.Fatalf("dirty/config/build = %v/%v/%v, want %v", task.dirty, needsConfig.Load(), needsBuild.Load(), test.want)
			}
			_, cached := o.host.resolvedReferences.entries.Load(path)
			if cached == test.want {
				t.Fatalf("cached missing config retained=%v, want %v", cached, !test.want)
			}
			if test.kind == fswatch.EventDelete {
				// A failed parse of an existing file is not a previously missing config.
				task.configMissing = false
				o.checkTasksForEventChanges(map[string]fswatch.EventKind{test.path: test.kind}, &needsConfig, &needsBuild)
				if !needsConfig.Load() || !needsBuild.Load() || !task.dirty {
					t.Fatal("existing invalid config deletion was suppressed")
				}
			}
		})
	}
}

func TestWatchReadinessWaitsForWatchReconciliation(t *testing.T) {
	var reports []*ast.Diagnostic
	o := &Orchestrator{opts: Options{Command: &tsoptions.ParsedBuildCommandLine{CompilerOptions: &core.CompilerOptions{Watch: core.TSTrue}}}, watchStatusReporter: func(d *ast.Diagnostic) { reports = append(reports, d) }}
	result := orchestratorResult{}
	result.report(o)
	if len(reports) != 0 || o.pendingWatchStatus == nil {
		t.Fatal("build reported readiness before watches could be installed")
	}
	o.reportWatchReady()
	if len(reports) != 1 || o.pendingWatchStatus != nil {
		t.Fatal("ready status was not delivered after reconciliation")
	}
	o.reportWatchReady()
	if len(reports) != 1 {
		t.Fatal("ready status delivered twice")
	}
}
