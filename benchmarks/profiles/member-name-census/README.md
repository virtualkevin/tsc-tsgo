# Materialized-member miss names (diagnostic only)

Extends the resolved-member census with exact occurrence counts for at most 16,384 admitted names per checker, each at most 256 bytes. Clones bound retained string backing storage; no semantic objects or table identities are retained. Serialization uses hex so internal invalid UTF-8 names stay distinct. Counts include nil-valued map entries and recursive calls, and exclude types without an owning checker.

Admission is first-seen, not sampled. Once full, admitted names continue accumulating exact counts; unadmitted events increment overflow. Overlength events have a separate count. If either counter is nonzero, ranked names are not necessarily the population's most frequent names. Even with full coverage, repeated names do not establish repeated requests to the same table, stable missing results, or removable CPU cost.

Validation covers capacity exhaustion, updates after exhaustion, byte lengths, lossless encoding, repeat snapshots, lookup paths, owner isolation and disabled behavior. Capture runs baseline, disabled observer and enabled observer sequentially on the four pinned workloads, checks clean diagnostics and physical input hashes, and requires count conservation. Control durations are not optimization measurements; no PERF rows.

Production instrumentation is temporary. `instrumentation.patch` and the two Go files preserve it after guarded restoration. Build/validation/capture scripts freeze the source hash. All 12 captures passed; guarded restoration returned production source and default binary to the retained baseline. See `restoration.json`.

## Result

Sentry captured all 78,026,843 materialized-member misses across 25,851 distinct byte names. `children` is largest at 485,448 (0.622%); the top ten total 4.052%. This argues against a few-name specialization as a broad solution. It does not establish repeated table/name requests or safe cached results.

TypeORM captured all 679,229 misses across 2,094 names; largest `length` 4.499%, top ten 25.007%. tRPC captured all 43,544 across 911 names; largest `_def` 4.827%, top ten 21.103%.

VS Code captured 9,101,679 of 10,597,748 misses, with 1,496,069 overflow events (14.117%). The admitted union has 40,884 names; counts can omit occurrences from other owners where a name was not admitted. Its recorded ranking is therefore not a population ranking. No workload had overlength events. Counts are per diagnostic run, not CPU fractions or timing gains.

The prior path census totals match for every workload. The next lead is callers that generate broad missing-property queries, especially union/intersection member enumeration; no new cache or production optimization is justified by name frequency alone.
