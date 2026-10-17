# PointerLinkStore A/B controller and proposed recorder

Drafts prepared under /tmp; no workloads, builds or tests launched by the author. Controller/common frozen after parent static review. Candidate revision label849d873; exact binary/source identities are hard-coded and verified through sidecars.

After the coordinating agent releases the quiet window:

`node /tmp/run-pointer-linkstore-ab.mjs [NEW_RESULTS_DIRECTORY]`

No argument creates a fresh timestamped directory under repository benchmarks/results. Existing directories are rejected. It runs two sequential harness invocations: seven alternating baseline/candidate pairs each for TypeORM and tRPC, then three each for VS Code and Sentry; one warmup per compiler/project. Default GC, scheduler, and checker settings are retained symmetrically, with no candidate overrides or explicit checker flag. The same absolute declaration-library directory is forced for both.

- Reference: preserved Go lazy7ee01da, SHA961e90a7e1d873477233c022716da08acc6f4b3f02df11c70d5e11360ca59ec3, source39b165a093813ad622f9b276a3a9d6c433d0d6a91199ee6c897f3d8e3ed03a59.
- Candidate: PointerLinkStore849d873, SHAb1a592d593d3415603062016bfd35b11b810f31f9a49b008ec2292e661a15322, source6beaa7324ec7dbf09a8b2776bda64b6d5b0d2e93ead3b27ccc4d3aabf5c43d3d.

Both are wrapped with GNU time for all phases. The controller captures binary build metadata, sidecar hashes, Node/wrapper/harness/manifest hashes, exact command lines, cleared environment names, per-side recorded runtime controls, wrapper metadata, cgroup counters and report hashes. Full binary/sidecar/harness snapshots are rechecked between groups and at completion. Workload checkout pins and input-content parity/immutability are enforced by the existing hashed runner and independently rechecked against reported hashes. Source build digests identify the actual preserved binaries; current HEAD is not assumed to equal either build source.

The shared validator checks full pass status, exact arguments including discovery/wrapper invocations, null candidate-only checker override, equal environments, absence of diagnostic output, file lists and contents, warmup/pair counts, alternating order, real-binary provenance, resource exit status, RSS sample bounds, and recomputed timing/RSS medians and ratios. Per-sample diagnostics are validated inside the hashed runner; raw diagnostic text for every timed invocation is not separately retained, so the recorder does not claim independent output reexecution.

Runtime/profile controls are explicitly removed, including known Go/native flags, node options, coverage/tracing/profile and allocator variables, plus discovered TSC_/TS_GO_/SCRIPTC_/MIMALLOC_/MI_ controls. A unique inert `_TSC_BENCH_OWNER` marker is added to runner and children for cleanup; its name/token are recorded separately from compiler controls. Secret environment values are never printed or stored. Other ordinary environment variables remain inherited (for example PATH and locale); this is not a hermetic environment claim.

Each compiler invocation is limited to180seconds; the controller has a30minute total deadline. Signals first reach the resource runner, which kills its detached wrapper/compiler group. On terminal exit/failure the controller scans /proc for its unique ownership marker, verifies PID start identity and kills surviving marked processes/groups; a5second grace timer supplies fallback cleanup if a runner fails to stop. No /proc polling occurs during measurements. Cleanup depends on Linux /proc visibility and inherited marker retention, which hold for these compiler processes; external SIGKILL of the controller itself is outside cooperative cleanup guarantees.

After completion:

`node /tmp/record-pointer-linkstore-ab.mjs COMPLETED_RESULTS_DIRECTORY [NEW_TMP_PROPOSAL_DIRECTORY]`

The recorder repeats integrity/result checks, rejects duplicate stage labels in the existing8column PERF table and NOTES marker, and creates only `/tmp/.../PERF.rows.md`, `NOTES.entry.md`, and `proposal.json`. It never changes repository documentation or commits. Output must be a new directory beneath /tmp. Current documentation hashes are captured for later application review. If results were saved outside benchmarks/, their links must be relocated before commit.

Interpretation is deliberately limited: ratios above1favor the candidate relative to preserved Go. This is not a comparison against the original native tsc-ts target and cannot establish the10× goal. All timings are GNU-time-wrapped and cannot compare with historical unwrapped timings. RSS means command peak resident memory, not aggregate process-tree memory, allocated bytes or Go heap. Separate conformance/API/race validation remains necessary; timing validation does not substitute for it.
