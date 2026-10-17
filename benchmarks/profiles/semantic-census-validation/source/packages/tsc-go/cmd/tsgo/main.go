package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/microsoft/typescript-go/internal/checker"
	"github.com/microsoft/typescript-go/internal/core"
	"github.com/microsoft/typescript-go/internal/execute"
)

func main() {
	os.Exit(runMain())
}

func runMain() int {
	core.ApplyDebugStackLimit()
	args := os.Args[1:]
	if os.Getenv("TSC_GO_CENSUS") != "" {
		for _, arg := range args {
			if !strings.HasPrefix(arg, "-") {
				continue
			}
			switch strings.ToLower(strings.TrimLeft(strings.SplitN(arg, "=", 2)[0], "-")) {
			case "api", "lsp", "w", "watch", "b", "build":
				fmt.Fprintln(os.Stderr, "semantic census supports ordinary one-shot CLI compilation only")
				return 1
			}
		}
	}
	if len(args) > 0 {
		switch args[0] {
		case "--lsp":
			return runLSP(args[1:])
		case "--api":
			return runAPI(args[1:])
		}
	}
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()
	result := execute.CommandLine(ctx, newSystem(), args, nil)
	if err := checker.FlushSemanticCensus(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		return 1
	}
	return int(result.Status)
}
