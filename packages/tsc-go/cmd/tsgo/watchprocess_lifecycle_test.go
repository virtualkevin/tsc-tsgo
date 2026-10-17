package main

import (
	"bufio"
	"context"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"testing"
	"time"
)

// Exercise real replacement and parent death independently of compiler work.
// The existing build.test.mjs watch cases cover output and rebuild semantics.
func TestWatchSupervisorReplacesWorkerAndStopsOrphans(t *testing.T) {
	if runtime.GOOS != "linux" {
		t.Skip("process lifecycle regression uses Linux RSS")
	}
	for _, shutdown := range []string{"kill", "terminate", "cancel"} {
		t.Run(shutdown, func(t *testing.T) { testWatchSupervisorShutdown(t, shutdown) })
	}
}

func testWatchSupervisorShutdown(t *testing.T, shutdown string) {
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	directory := t.TempDir()
	reader, writer, err := os.Pipe()
	if err != nil {
		t.Fatal(err)
	}
	defer reader.Close()
	command := exec.Command(executable, "-test.run=^TestWatchSupervisorHelper$")
	for _, entry := range os.Environ() {
		if !strings.HasPrefix(entry, watchProcessVariable+"=") && !strings.HasPrefix(entry, watchParentVariable+"=") && !strings.HasPrefix(entry, "TSC_TS_WATCH_MEMORY=") && !strings.HasPrefix(entry, "TSC_GO_WATCH_TEST_DIR=") {
			command.Env = append(command.Env, entry)
		}
	}
	command.Env = append(command.Env, "TSC_TS_WATCH_MEMORY=1", "TSC_GO_WATCH_TEST_DIR="+directory)
	command.Stdout, command.Stderr = writer, writer
	if err := command.Start(); err != nil {
		writer.Close()
		t.Fatal(err)
	}
	writer.Close()
	waited := false
	var workerPID int
	workersExited := false
	defer func() {
		_ = command.Process.Kill()
		if !waited {
			_ = command.Wait()
		}
		// If the regression fails, clean up its worker rather than leaving it behind.
		if !workersExited && workerPID > 0 {
			if process, err := os.FindProcess(workerPID); err == nil {
				_ = process.Kill()
			}
		}
	}()
	lines := make(chan string, 8)
	done := make(chan struct{})
	go func() {
		defer close(done)
		scanner := bufio.NewScanner(reader)
		for scanner.Scan() {
			lines <- scanner.Text()
		}
	}()
	readWorker := func(wantRole string) int {
		t.Helper()
		select {
		case line := <-lines:
			fields := strings.Fields(line)
			if len(fields) != 2 || fields[0] != wantRole {
				t.Fatalf("worker message = %q, want %s PID", line, wantRole)
			}
			pid, err := strconv.Atoi(fields[1])
			if err != nil || pid <= 0 {
				t.Fatalf("bad worker PID in %q", line)
			}
			workerPID = pid
			return pid
		case <-done:
			t.Fatal("supervisor ended before worker was ready")
		case <-time.After(10 * time.Second):
			t.Fatal("watch worker did not become ready")
		}
		return 0
	}
	first := readWorker("start")
	if err := os.WriteFile(filepath.Join(directory, "rebuild"), nil, 0600); err != nil {
		t.Fatal(err)
	}
	second := readWorker("resume")
	if first == second {
		t.Fatal("memory restart did not replace worker")
	}
	switch shutdown {
	case "kill":
		err = command.Process.Kill()
	case "terminate":
		err = command.Process.Signal(syscall.SIGTERM)
	case "cancel":
		err = os.WriteFile(filepath.Join(directory, "cancel"), nil, 0600)
	}
	if err != nil {
		t.Fatal(err)
	}
	finished := make(chan error, 1)
	go func() { finished <- command.Wait() }()
	select {
	case err := <-finished:
		waited = true
		if shutdown == "cancel" && err != nil {
			t.Fatalf("context shutdown: %v", err)
		}
	case <-time.After(4 * time.Second):
		_ = command.Process.Kill()
		<-finished
		waited = true
		t.Fatal("supervisor did not exit on shutdown")
	}
	// We supplied an actual pipe file instead of StdoutPipe: Wait does not close
	// this read end. EOF proves the inherited worker descriptor also closed.
	select {
	case <-done:
		workersExited = true
	case <-time.After(4 * time.Second):
		t.Fatal("orphan watch worker retained output after supervisor death")
	}
}

func TestWatchSupervisorHelper(t *testing.T) {
	directory := os.Getenv("TSC_GO_WATCH_TEST_DIR")
	if directory == "" {
		return
	}
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	if _, child := os.LookupEnv(watchProcessVariable); !child {
		go func() {
			ticker := time.NewTicker(20 * time.Millisecond)
			defer ticker.Stop()
			for {
				select {
				case <-ctx.Done():
					return
				case <-ticker.C:
					if _, err := os.Stat(filepath.Join(directory, "cancel")); err == nil {
						cancel()
						return
					}
				}
			}
		}()
	}
	system := &osSys{}
	if supervising, status := system.StartWatchProcess(ctx); supervising {
		os.Exit(int(status))
	}
	role := "start"
	if system.WatchProcessResumed() {
		role = "resume"
	}
	fmt.Fprintf(os.Stdout, "%s %d\n", role, os.Getpid())
	system.WatchFirstBuildDone()
	for {
		if role == "start" {
			if _, err := os.Stat(filepath.Join(directory, "rebuild")); err == nil {
				system.RestartWatchBeforeRebuild()
			}
		}
		time.Sleep(20 * time.Millisecond)
	}
}
