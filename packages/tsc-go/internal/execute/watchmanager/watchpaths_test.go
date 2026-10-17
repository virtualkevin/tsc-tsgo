package watchmanager

import (
	"io"
	"reflect"
	"testing"
)

func TestResolveDesiredDirsKeepsConcreteShallowProjects(t *testing.T) {
	exists := map[string]bool{
		"/": true, "/project": true, "/tmp": true, "/tmp/project": true, "/tmp/project/src": true,
		"/work": true, "/work/project": true, "/home": true, "/home/user": true,
		"/home/user/project": true, "/home/user/project/src": true,
	}
	manager := NewWatchManager(io.Discard, func(path string) bool { return exists[path] })
	for _, test := range []struct {
		name    string
		desired map[string]bool
		want    map[string]bool
	}{
		{"temporary project and inputs", map[string]bool{"/tmp/project": false, "/tmp/project/src": true}, map[string]bool{"/tmp/project": false, "/tmp/project/src": true}},
		{"shallow mounted project", map[string]bool{"/work/project": true}, map[string]bool{"/work/project": true}},
		{"absolute roots remain watchable", map[string]bool{"/": false, "/tmp": false, "/home": false}, map[string]bool{"/": false, "/tmp": false, "/home": false}},
		{"root-level checkout", map[string]bool{"/project": true}, map[string]bool{"/project": true}},
		{"removed project keeps shallow parent nonrecursive", map[string]bool{"/tmp/project/missing": true}, map[string]bool{"/tmp/project": false}},
		{"missing checkout watches temporary root nonrecursively", map[string]bool{"/tmp/gone/project": true}, map[string]bool{"/tmp": false}},
		{"missing root-level checkout", map[string]bool{"/removed/src": true}, map[string]bool{"/": false}},
		{"explicit parent remains after child removal", map[string]bool{"/tmp/project": false, "/tmp/project/missing": true}, map[string]bool{"/tmp/project": false}},
		{"deep ancestor fallback remains nonrecursive", map[string]bool{"/home/user/project/src/missing": true}, map[string]bool{"/home/user/project/src": false}},
	} {
		t.Run(test.name, func(t *testing.T) {
			if got := manager.ResolveDesiredDirs(test.desired); !reflect.DeepEqual(got, test.want) {
				t.Fatalf("watches = %v, want %v", got, test.want)
			}
		})
	}
}

func TestKnownWatchDirectoriesAcceptAllAbsoluteDepths(t *testing.T) {
	for _, path := range []string{"/", "/tmp", "/project", "/tmp/project", "/tmp/project/shared", "C:/", "C:/Users", "C:/work/project", "//server/share/", "//server/share/project/src"} {
		if !CanWatchKnownDirectory(path) {
			t.Errorf("known project/dependency directory rejected: %s", path)
		}
	}
	for _, path := range []string{"", "relative/project/src", "https://host/project"} {
		if CanWatchKnownDirectory(path) {
			t.Errorf("non-disk or unrooted path accepted: %s", path)
		}
	}
}

func TestRemovedTemporaryProjectKeepsNearestExistingWatch(t *testing.T) {
	exists := map[string]bool{"/": true, "/tmp": true, "/tmp/project": true}
	manager := NewWatchManager(io.Discard, func(path string) bool { return exists[path] })
	desired := map[string]bool{"/tmp/project": true}
	if got := manager.ResolveDesiredDirs(desired); !reflect.DeepEqual(got, desired) {
		t.Fatalf("initial project watch = %v", got)
	}
	delete(exists, "/tmp/project")
	if got := manager.ResolveDesiredDirs(desired); !reflect.DeepEqual(got, map[string]bool{"/tmp": false}) {
		t.Fatalf("removed project fallback = %v, want nonrecursive /tmp", got)
	}
	exists["/tmp/project"] = true
	if got := manager.ResolveDesiredDirs(desired); !reflect.DeepEqual(got, desired) {
		t.Fatalf("recreated project watch = %v", got)
	}
}

func TestReplacedWatchTerminationDoesNotScheduleObsoleteRebuild(t *testing.T) {
	manager := NewWatchManager(io.Discard, func(string) bool { return true })
	old, replacement := &watchedDir{}, &watchedDir{}
	manager.watchedDirs["/tmp/project"] = replacement
	manager.handleWatchTerminated("/tmp/project", old)
	if manager.watchedDirs["/tmp/project"] != replacement {
		t.Fatal("stale callback removed replacement watch")
	}
	if _, overflow := manager.DrainEvents(); overflow {
		t.Fatal("stale callback forced an obsolete rebuild")
	}
	select {
	case <-manager.DoCycleCh():
		t.Fatal("stale callback scheduled a cycle")
	default:
	}
	delete(manager.watchedDirs, "/tmp/project")
	manager.handleWatchTerminated("/tmp/project", old)
	if _, overflow := manager.DrainEvents(); overflow {
		t.Fatal("removed watch callback forced an obsolete rebuild")
	}
}
