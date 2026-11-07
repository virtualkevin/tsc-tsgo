# SIMD/AVX opportunity audit

Offline analysis of the preserved current-production CPU profiles, not new
performance measurements. The capture checks the original profile hashes and
retained binary; readback reproduces category totals from archived raw profiles.
Inclusive categories overlap and include callees; they are not removable wall
time or proof that every operation in a category can be vectorized.

| Workload | Scanner CPU % | Byte search/compare CPU % | Memory copy/clear CPU % | Map control matching CPU % | Hashing CPU % | Slice search CPU % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TypeORM | 1.157 | 1.270 | 12.523 | 1.407 | 1.066 | 0.000 |
| tRPC | 1.369 | 1.283 | 8.127 | 0.941 | 1.198 | 0.000 |
| VS Code | 1.406 | 0.793 | 5.496 | 2.652 | 1.759 | 0.025 |
| Sentry | 0.858 | 1.465 | 4.896 | 4.658 | 3.295 | 0.057 |

Kernel-advertised features on this Intel Cascade Lake host include AVX2 and
AVX-512 F/BW/CD/DQ/VL/VNNI. Advertisement does not replace the runtime's CPU/OS
state checks. Production remains GOAMD64=v1 and uses runtime dispatch where
provided; no unconditional ISA requirement is introduced.

GNU objdump of the exact production executable confirms YMM vector paths in
runtime.memclrNoHeapPointers, runtime.memmove, memeqbody, and indexbytebody.
These routines already have SIMD implementations. Their profile cost is not an
untapped scalar budget, and presence in the executable does not prove which
size-dependent path each call took. Runtime source hashes are recorded as well.
The Go map control matcher also already has a compiler intrinsic; the previous
small-string-map SIMD experiment failed its end-to-end acceptance screen.

Decision: do not implement a scanner rewrite as the primary order-of-magnitude
strategy. Its entire observed inclusive CPU envelope is around one percent.
Memory-operation cost still motivates reducing allocation and copied bytes;
it does not justify replacing existing vector routines without size/distribution
evidence. Compact batchable semantic representations remain a possible route,
but must first justify conversion, ownership, and lookup costs on real workloads.
No production change or new PERF row results from this diagnostic audit.
