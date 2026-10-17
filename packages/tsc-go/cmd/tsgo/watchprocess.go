package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"time"

	"github.com/microsoft/typescript-go/internal/execute/tsc"
	"github.com/microsoft/typescript-go/internal/jsnum"
)

const watchProcessVariable = "TSC_TS_WATCH_PROCESS"
const watchRestartStatus = 75
const watchParentVariable = "TSC_GO_WATCH_PARENT_PID"

// Match JavaScript Number semantics, including whitespace, exponent/base
// prefixes and Infinity. Only the exact string "0" disables supervision.
func watchMemoryPolicy(memory string) (enabled bool, limit float64) {
	if memory == "0" {
		return false, 0
	}
	megabytes := float64(jsnum.FromString(memory))
	if memory != "" && megabytes > 0 {
		return true, megabytes * 1048576
	}
	return true, 0
}

var _ tsc.WatchProcessSystem = (*osSys)(nil)

func (s *osSys) StartWatchProcess(ctx context.Context) (bool, tsc.ExitStatus) {
	enabled, limit := watchMemoryPolicy(os.Getenv("TSC_TS_WATCH_MEMORY"))
	if !enabled {
		return false, tsc.ExitStatusSuccess
	}
	if role, child := os.LookupEnv(watchProcessVariable); child {
		s.watchChild = true
		s.watchResumed = role == "resume"
		s.watchLimit = limit
		parent := os.Getppid()
		if expected, err := strconv.Atoi(os.Getenv(watchParentVariable)); err == nil && expected > 0 {
			parent = expected
		}
		if os.Getppid() != parent {
			os.Exit(1)
		}
		// Same-process-group terminal signals reach both processes. A killed
		// supervisor cannot leave a watcher alive, including SIGKILL on the parent.
		go func() {
			ticker := time.NewTicker(time.Second)
			defer ticker.Stop()
			for {
				select {
				case <-ctx.Done():
					return
				case <-ticker.C:
					if os.Getppid() != parent || processAliveSupported && !isProcessAlive(parent) {
						os.Exit(1)
					}
				}
			}
		}()
		return false, tsc.ExitStatusSuccess
	}
	executable, err := os.Executable()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		return true, tsc.ExitStatusDiagnosticsPresent_OutputsSkipped
	}
	role := "start"
	for {
		child := exec.CommandContext(ctx, executable, os.Args[1:]...)
		child.Stdin, child.Stdout, child.Stderr = os.Stdin, os.Stdout, os.Stderr
		child.Env = make([]string, 0, len(os.Environ())+1)
		for _, entry := range os.Environ() {
			if !strings.HasPrefix(entry, watchProcessVariable+"=") && !strings.HasPrefix(entry, watchParentVariable+"=") {
				child.Env = append(child.Env, entry)
			}
		}
		child.Env = append(child.Env, watchProcessVariable+"="+role, watchParentVariable+"="+strconv.Itoa(os.Getpid()))
		err := child.Run()
		// CommandContext kills and waits for the child before returning on shutdown.
		if ctx.Err() != nil {
			return true, tsc.ExitStatusSuccess
		}
		if err == nil {
			return true, tsc.ExitStatusSuccess
		}
		var exit *exec.ExitError
		if !errors.As(err, &exit) {
			fmt.Fprintln(os.Stderr, err)
			return true, tsc.ExitStatusDiagnosticsPresent_OutputsSkipped
		}
		if exit.ExitCode() == watchRestartStatus {
			role = "resume"
			continue
		}
		return true, tsc.ExitStatus(watchChildExitStatus(exit))
	}
}

func (s *osSys) WatchProcessResumed() bool { return s.watchResumed }
func (s *osSys) WatchFirstBuildDone() {
	if s.watchChild && s.watchLimit == 0 {
		s.watchLimit = residentMemory() * 2.5
	}
}
func (s *osSys) RestartWatchBeforeRebuild() bool {
	if s.watchChild && s.watchLimit > 0 && residentMemory() > s.watchLimit {
		os.Exit(watchRestartStatus)
		return true
	}
	return false
}
