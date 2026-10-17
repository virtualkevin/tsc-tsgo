//go:build !unix && !windows

package main

import "os/exec"

// As in the original driver, an unavailable resident-memory reading is zero.
func residentMemory() float64 { return 0 }
func watchChildExitStatus(exit *exec.ExitError) int {
	if code := exit.ExitCode(); code >= 0 {
		return code
	}
	return 1
}
