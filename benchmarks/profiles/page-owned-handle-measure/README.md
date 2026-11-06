# Cost and retention of page-owned compact edges

This measures the isolated page-owned-handle-graph prototype from19469bc against
a stable typed pointer-page baseline. No compiler implementation changes. Source
hashes, overlay, toolchain and built test executable are frozen by validation.json.
Normal/race/checkptr validation passed all nine selected tests per mode, including
the original seven ownership tests and two fixture/lifetime checks. No measurement
has run at this preparation checkpoint.

Both representations have kind, payload, stable identity and four edges. Pointer
records are48bytes and compact records32bytes; both use256-record typed pages.
The pointer allocator and compact allocator root only their current page. The
compact representation additionally owns its remote-page tables/maps; count all
of those costs. The pointer constructor needs no runtime owner decoder/checks for
these valid prior-node inputs. Temporary construction tables store public Ref
values on the compact side and pointers on the baseline side, with their actual
sizes and allocation costs included. Traversal excludes construction/setup.

Two timed shapes retain all constructed records through the first-edge chain:
linked includes deterministic distant references; local uses within-page edges
except at page boundaries. This exposes the tradeoff between remote-table cost
and the local decode path. Sparse has no edges and is used only for retention:
with only the final root alive, both baselines may collect old pages. Fixtures
are independently checked at1/255/256/257/4096/262144records with exact IDs, edge
identities, values and checksums. These shapes are not compiler edge statistics.

The fixed config measures construction, internal traversal and public adaptation
at4096and262144records, nine alternating fresh-process pairs per timed case,200ms
Go benchmark targets, default runtime settings and every sample retained. This is
216timing observations. Separate retention probes use five alternating pairs at
each size for linked/local/sparse (60observations). Each forces two GCs before and
after construction and holds only the final root. HeapAlloc/HeapObjects deltas are
runtime endpoints, not precise object accounting or peak RSS. TotalAlloc includes
the completed construction/GC interval. Compact metadata is counted after the
memory snapshot, excluding that diagnostic traversal's allocations from endpoints.

No builds, edits, tests or Git work during timing. Failed observations stop capture;
keep partial evidence, do not discard outliers or retune based on results. Report
both timing summaries, paired ranges, allocations and all retention data. These
are standalone storage experiments, not compiler workload measurements; do not
append them to PERF.md, extrapolate a10xgain or compare these times to historical
compiler/native runs. A useful result would justify only a concrete compiler-family
ownership/mapping investigation followed by full compatibility and workload gates.
