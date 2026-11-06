# Conditional spread-override table contract

Candidate only; no performance claim. `checkObjectLiteral` currently creates `allPropertiesTable` under strictNullChecks even when the literal has no spread. It records synthesized property symbols in this private table. The only read is `checkSpreadPropOverrides` within the SpreadAssignment branch; the table is neither returned nor passed to any other consumer.

Allocate that table on encountering a spread in the existing computed-name prepass, still before the main property loop. Do not add a second AST walk. No-spread literals then skip the table allocation and its writes. Literals containing a spread keep all writes from the start, including properties preceding the first spread. Strict-null-disabled checking remains without the table.

For a literal with a spread, the table is empty until the main property loop in both versions. Moving the allocation within the prepass cannot expose it: computed-name checks do not receive this local map. Computed-name queries, their ordering, symbol and type construction, contextual stack operations, property/spread merges, diagnostics and inference sites remain unchanged. Grammar checks and the expando early return remain unchanged. Accessors remain excluded from the override table exactly as before.

Assumptions: checker evaluation does not structurally mutate the current object's property list or turn an existing property into a spread during this prepass. This is a source-review obligation, not inferred merely from clean fixtures. Normal allocation/GC scheduling may differ; the optimization does not promise identical allocator events or behavior under resource exhaustion.

This is removal of unused bookkeeping, not a result cache or symbol-identity rewrite. The expected speed benefit is unknown and it is not an established route to 10× by itself. Required gates: exact source inverse audit; retained/candidate normal/race/checkptr API-history comparison; full compiler/services/conformance and CLI/API/emit checks; normal provenance; fixed four-workload screen and confirmations under the existing policy. No promotion based on correctness alone.

Machine-checked model: proof/prove.py discharges five array-state obligations and finds the deliberate main-loop-allocation control counterexample. This is a formal model under the assumptions above, not a whole-compiler or Go memory-safety proof. Source matching checks the seven named local-table sites.
