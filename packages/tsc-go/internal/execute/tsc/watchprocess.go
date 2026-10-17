package tsc

import "context"

// WatchProcessSystem is optional: real CLI systems can supervise native watch
// processes without adding process lifetime behavior to compiler hosts or mocks.
type WatchProcessSystem interface {
	StartWatchProcess(context.Context) (supervising bool, status ExitStatus)
	WatchProcessResumed() bool
	WatchFirstBuildDone()
	RestartWatchBeforeRebuild() bool
}

func StartWatchProcess(ctx context.Context, sys System) (bool, ExitStatus) {
	if process, ok := sys.(WatchProcessSystem); ok {
		return process.StartWatchProcess(ctx)
	}
	return false, ExitStatusSuccess
}
func WatchProcessResumed(sys System) bool {
	process, ok := sys.(WatchProcessSystem)
	return ok && process.WatchProcessResumed()
}
func WatchFirstBuildDone(sys System) {
	if process, ok := sys.(WatchProcessSystem); ok {
		process.WatchFirstBuildDone()
	}
}
func RestartWatchBeforeRebuild(sys System) bool {
	process, ok := sys.(WatchProcessSystem)
	return ok && process.RestartWatchBeforeRebuild()
}
