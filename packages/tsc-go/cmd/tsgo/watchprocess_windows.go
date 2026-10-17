//go:build windows

package main

import (
	"os/exec"
	"syscall"
	"unsafe"
)

// PROCESS_MEMORY_COUNTERS as defined by Windows; pointer-sized counters follow
// the two DWORD fields on both 32- and 64-bit targets.
type processMemoryCounters struct {
	size                  uint32
	pageFaults            uint32
	peakWorkingSet        uintptr
	workingSet            uintptr
	quotaPeakPagedPool    uintptr
	quotaPagedPool        uintptr
	quotaPeakNonPagedPool uintptr
	quotaNonPagedPool     uintptr
	pagefile              uintptr
	peakPagefile          uintptr
}

var getProcessMemoryInfo = syscall.NewLazyDLL("psapi.dll").NewProc("GetProcessMemoryInfo")

func residentMemory() float64 {
	var counters processMemoryCounters
	counters.size = uint32(unsafe.Sizeof(counters))
	handle, err := syscall.GetCurrentProcess()
	if err != nil {
		return 0
	}
	result, _, _ := getProcessMemoryInfo.Call(uintptr(handle), uintptr(unsafe.Pointer(&counters)), uintptr(counters.size))
	if result == 0 {
		return 0
	}
	return float64(counters.workingSet)
}
func watchChildExitStatus(exit *exec.ExitError) int {
	if code := exit.ExitCode(); code >= 0 {
		return code
	}
	return 1
}
