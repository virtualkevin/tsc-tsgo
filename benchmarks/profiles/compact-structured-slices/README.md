# Compact structured-type slices (isolated candidate)

Eight-file overlay preserves slice capacity and backing identity while reducing
three StructuredType headers from24to16bytes each on amd64. See CONTRACT.md and
the standalone compact-slice-header prototype for representation and assurance.
Production/default compiler remain unchanged. No workload timing yet.

Initial compile failed because compactSliceFrom(nil) cannot infer its generic
element type. Exact staged sources/controller/logs are preserved in
failed-untyped-nil/. The generator now specifies []*Signature(nil) at that site.
No semantic test failed in that attempt because compilation did not complete.

Focused validation passed17test records per mode (normal/race/checkptr) on both
candidate and retained semantic controls. Raw logs and hashes were independently
read back. Full compiler validation passed21,178root records/14packages and219
services records; pinned conformance passed14,915configurations (12,789fully
checked,8partial,2,118unsupported skips,0failures). Compressed full-suite logs were
hash verified. Normal CLI parity80/80 and API/emit integration12/12passed.
Instrumented CLI race and checkptr parity each passed80/80. Independent final
raw-evidence verification passed. The normal production build matched the tested
binary a2974b77 exactly, with8changed/newfiles and5156candidate source files;
source3a16fa1b/sidecar8fd4282a. Retained source/default executable were restored.
Preflight passed; workload timing is next.
Production/default compiler remain unchanged; no speedup or10×claim.
