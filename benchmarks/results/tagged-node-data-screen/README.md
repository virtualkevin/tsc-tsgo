# Tagged concrete AST payload screen: rejected

Tagged AST payload screen completed and rejected (capture cf06918): ratio-of-medians/paired median typeorm 0.948530/0.979233, trpc 0.974007/0.944065, vscode 0.951461/0.951461, sentry 0.940320/0.933789. Aggregate ratios 0.953499/0.951989 both miss 1.01; every workload misses the 0.98 ratio-of-medians gate, and every paired median also misses 0.98. All median RSS gates pass. Integrity and diagnostics passed; this does not mean performance acceptance. No confirmations, extra samples, layout/dispatch retuning, or pooling with prior experiments. Production remains retained source216d40c7/defaultbinary8fe4bd80. No native-relative improvement claimed; 10× goal unmet.

All 28 paired samples and physical-input, diagnostic, and resource evidence are preserved in small.json and large.json. recording/proposal.json records the rejected decision. execution/ contains frozen scripts, policy, configuration, captured stdout/stderr, and their SHA256 manifest. Runner session19717 and recorder10783 both terminated successfully.

The candidate reduces Node from 48 to 40 bytes and Identifier from 72 to 64 bytes, but is slower on every workload by ratio of medians despite lower median peak RSS. These measurements do not establish which dispatch or allocation mechanism caused the regression. The candidate remains separately preserved and unpromoted.
