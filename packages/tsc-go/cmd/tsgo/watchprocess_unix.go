//go:build unix

package main

import (
	"context"
	"os"
	"os/exec"
	"os/signal"
	"runtime"
	"strconv"
	"strings"
	"syscall"
	"time"
)

// RSS, not peak RSS or Go's live heap: the contract covers the whole process.
func residentMemory() float64 {
	if runtime.GOOS == "linux" {
		data, err := os.ReadFile("/proc/self/statm")
		if err != nil {
			return 0
		}
		fields := strings.Fields(string(data))
		if len(fields) < 2 {
			return 0
		}
		pages, err := strconv.ParseUint(fields[1], 10, 64)
		if err != nil {
			return 0
		}
		return float64(pages) * float64(os.Getpagesize())
	}
	// macOS/BSD expose resident KB through ps without cgo. This runs only at
	// build boundaries, and a missing/unresponsive ps disables that reading.
	ctx, cancel := context.WithTimeout(context.Background(), time.Second)
	defer cancel()
	data, err := exec.CommandContext(ctx, "ps", "-o", "rss=", "-p", strconv.Itoa(os.Getpid())).Output()
	if err != nil {
		return 0
	}
	kb, err := strconv.ParseFloat(strings.TrimSpace(string(data)), 64)
	if err != nil {
		return 0
	}
	return kb * 1024
}

func watchChildExitStatus(exit *exec.ExitError) int {
	if status, ok := exit.Sys().(syscall.WaitStatus); ok && status.Signaled() {
		sig := status.Signal()
		signal.Reset(sig)
		_ = syscall.Kill(os.Getpid(), sig)
		return 128 + int(sig)
	}
	return exit.ExitCode()
}
