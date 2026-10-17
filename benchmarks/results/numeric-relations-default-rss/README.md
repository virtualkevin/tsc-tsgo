# Numeric relation-key experiment — measured and reverted

The controller and recorder completed successfully. `small.json`, `large.json` and `summary.json` preserve all seven small-workload and three large-workload alternating pairs plus warmups. `controller-design.md` is the historical prelaunch plan; its pending-launch wording is superseded by these completed reports.

The candidate did not provide a useful overall runtime gain. TypeORM and VS Code were neutral; tRPC favored the candidate in five of seven pairs (paired median 1.029), while Sentry favored the old compiler in two of three (paired median 0.943). Sentry median peak RSS improved from 5327.0 to 5168.6 MiB. Production numeric relation keys were reverted; representation-independent API regressions remain.

`numeric-relations-host-observation.json` records a transient concurrent scanner observation and its limits. Its exact overlap with a timed sample is unknown; no sample was excluded. The higher small-workload baseline compared with a prior session cannot be attributed to this observation. Use within-run comparisons; this was not an exclusively controlled physical host.

Scripts retain their original /tmp imports/paths; reproduce their layout in /tmp before rerunning. Binary/source provenance is retained in the reports; source and validation evidence are under ../../profiles/numeric-relation-keys/ and ../../validation/.

This compares two Go builds. It does not establish a speedup over original native tsc-ts or meet the 10× goal.
