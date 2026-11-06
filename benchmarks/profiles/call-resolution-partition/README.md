# Call-resolution CPU partition

After the compact structured-slice rejection, this reanalyzes preserved normal
CPU profiles from retained production. No new compiler query, workload timing or
production change. Five parser/ownership tests pass; complete report reproduction
passes with original raw-profile hashes, manifest pins, source hashes and exact
agreement with the earlier initializer-work-budget call-resolution totals.

Every sample belongs to its innermost selected call resolver. Its nearest listed
inner phase receives the sample; unclassified call-body and callee/dispatch work
remain explicit. Nested calls are not charged again to outer inference or
applicability. Phase percentages below are disjoint within this definition, not
inclusive function totals. They include callees other than nested selected calls.

| Workload | Call-resolution CPU % | Applicability phase % | Argument inference phase % | Candidate ordering % | Subtype chooseOverload path % | Assignable chooseOverload path % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TypeORM | 23.571 | 9.938 | 6.596 | 0.440 | 7.300 | 10.466 |
| tRPC | 12.183 | 3.046 | 5.076 | 0 sampled | 2.538 | 6.599 |
| VS Code | 42.027 | 18.653 | 11.415 | 0.361 | 8.936 | 23.793 |
| Sentry | 46.063 | 26.861 | 14.965 | 0.148 | 8.745 | 33.970 |

Pass columns are another partition, not additions to phase columns. They identify
source callsites in resolveCall, not how many calls retried, duplicated work, or
whether a result is reusable. No unknown chooseOverload callsite appears in these
profiles. Zero sampled CPU is not zero execution. Historical small-workload
sampling is coarse. None of these percentages are wall-time forecasts or a
removable-work budget.

The source-line detail identifies a more concrete direction:

- VS Code: samples attributed to the contextual argument-expression calls within
  applicability and inference are12.955% and4.443% of total CPU respectively.
  The ordinary argument compatibility call in applicability is4.341%.
- Sentry: the JSX applicability delegation accounts for17.145% and JSX inference
  delegation6.318% of total CPU. These disjoint sample groups total23.463%.
  Ordinary contextual argument-expression calls add5.915% and4.401% in their
  respective phases; ordinary applicability comparison is3.348%.

These are samples at selected caller lines, including their descendants within
the innermost call scope. They do not prove expensive rechecking of the same node
or removable allocation. Source evidence is bound to checker.go and jsx.go hashes.

The original resolveCall already omits the subtype pass for a single candidate.
chooseOverload mutates argument check mode, inference contexts and error candidate
lists; it can perform a second inference/applicability round after contextual
arguments are enabled. Failed resolution publishes a signature before reporting
errors to preserve recursive observations. Removing those passes wholesale would
change compiler behavior.

JSX inference calls checkExpressionWithContextualType with its inference context;
JSX applicability passes nil and may use an instantiated parameter type. Attribute
construction queries contextual type, creates fresh property symbols/links,
reports deprecation suggestions and registers context-sensitive inference sites.
A cache keyed only by JSX node would lose these effects and identities.

Decision: do not optimize candidate ordering or assume the entire call-resolution
budget is overload retry. Next isolate actual JSX contextual attribute requests,
parameter/check-mode/inference-context distinctions and construction/effect costs
before proposing reuse or a representation that shares completed immutable facts.
Keep every unknown/context-sensitive request explicit. This is a larger measured
path than the recent header changes, but no10×mechanism or speedup is established.
PERF.md remains unchanged. The rejected layouts remain rejected.

Reproduce with `python3 -B -m unittest discover -s benchmarks/profiles/call-resolution-partition`
and `python3 -B benchmarks/profiles/call-resolution-partition/analyze.py`.
