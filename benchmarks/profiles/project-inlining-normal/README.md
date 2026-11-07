# Current production diagnostic profiles

Refresh CPU and sampled allocation profiles after adoption of project-wide
inlining. Use the production artifact and sidecar pinned by the completed
native-project-inlining comparison, with its identical physical input files
and compiler arguments plus pprofDir. Default runtime settings; sequential
captures, decode only after all four finish. No timings enter PERF.md.

Historical CPU profiles identify map access, allocation and GC as major costs,
but predate the adopted build setting. These captures determine whether that
cost distribution still supports a broader representation change. Inclusive
callers overlap; allocation samples are cumulative and may omit recent objects.
No forced final GC, live-memory claim, or predicted speedup.
