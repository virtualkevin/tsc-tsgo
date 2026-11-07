# Current production worker scaling

Prepared experiment; no workload measurements collected yet. Run only after all
other validation, compilation, profiling and benchmarking jobs have finished.
The retained project-inlining binary and sidecar are pinned, with unchanged
physical inputs taken from the direct-native milestone. Production code is not
modified. `--checkers` is the only varied compiler setting; GOMAXPROCS stays at
its default so runtime CPU capacity does not vary with checker count.

One warmup per count precedes four balanced rounds at 1/2/4/8 checkers for each
of TypeORM, tRPC, VS Code and Sentry. Each count occupies every position once;
each directed within-round predecessor pair occurs once. This controls ordering
but does not establish statistical confidence or remove environmental drift.
All raw observations, including warmups, are preserved. A failing run remains
failed; do not select favorable samples or overwrite the output directory.

GNU time supplies user/system CPU seconds and maximum command RSS. Wall time
includes launching/waiting for the wrapper. CPU fields have 0.01-second precision.
No heap allocation count or semantic-equivalence inference follows from these
metrics. Clean diagnostics and exact input content are required, but this
experiment does not replace full compiler correctness validation.

The experiment distinguishes worker scaling from changes to runtime CPU limits.
A reduction in elapsed time with increasing CPU or RSS is a tradeoff, not work
elimination. It can guide a later ownership/scheduling experiment; it does not
prove that duplicated semantic computations are safe to share, and does not
compare against original native tsc-ts or establish the 10x goal.
