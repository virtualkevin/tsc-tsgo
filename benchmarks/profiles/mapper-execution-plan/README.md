# Ordered mapper execution plans — isolated prototype

## Current-state reconciliation

Prepared at main 02a45c3. Production Go source and preserved Go binary remain unchanged. Correctness ancestor remains 2bd066d87f5bafd315be9f40889d0a60b9e58e0b; native tsc-ts is the performance target, not the correctness oracle. The completed instantiation-family observer is diagnostic evidence, not a production candidate. User-provided OPTI_ANALYSIS_01.md and tsc-tsgo-correctness-verification-agent-handoff.md remain untouched.

This implements the handoff's reusable-plan/refinement direction at a bounded component boundary. It does not claim a whole-compiler proof or an order-of-magnitude gain. The interpreter is not yet connected to production mapper constructors or dispatch. Its supported stateful tests compare with the existing local evaluator, not a separately built upstream API replay adapter.

## Representation and effect contract — reviewed argument, not proof

A plan represents the same immutable mapper topology as its source graph. Leaf instructions keep typed references to the original mapper; arrays and callbacks remain live and are not copied or evaluated at compilation. Merged nodes concatenate their ordered child execution. Composite nodes save the input, execute the first child, and either instantiate the changed result with the second mapper, or execute the second child directly. This preserves the original branch and invocation sequence, including inference/callback effects and diagnostic-budget-bearing instantiateType calls. No result or counter delta is memoized.

Correspondence: at each instruction boundary, the current type and saved input stack correspond to the current value and pending composite activations of recursive evaluation. The same leaf implementation is invoked with the same pointer input. Identity is compared within independent fixture executions by fixture identity and operation trace, never by cross-process pointer addresses. Typed instruction roots retain all referenced mapper leaves and their transitive objects. Published plan code is read-only; compilation requires ownership. The existing source assigns merged/composite child pointers only in constructors. Arbitrary concurrent mutation or post-publication rewiring is outside this prototype's contract.

Compilation is bounded to 512 visited graph nodes, 256 instructions, and 32 saved composite inputs. Cycles or exceeded bounds return nil before semantic effects. A future integration must use the original evaluator when compilation fails. The plan itself uses a fixed typed stack and does not reconstruct pointers. Repeated DAG nodes expand with their original multiplicity, not shared result caching.

## Evidence and limits

Four tests cover pure evaluator agreement across repeated queries and borrowed-array mutation; independent stateful callback/result histories for both composite branches; bounded and cyclic fallback without callbacks; and typed target retention across GC. Normal/race/checkptr validation is recorded separately. A synthetic 32-link merged-chain microbenchmark is prepared, not a four-workload performance measurement. Compilation cost, retained instruction memory, ordinary shallow-chain overhead, and interface dispatch may erase any benefit.

Remaining obligations before compiler integration/promotion: nested composite branch coverage; panic/diagnostic histories; pinned-oracle stateful API replay; constructor/dispatch ownership audit and immutable publication; full compiler conformance, API/emit and CLI race coverage; ordinary build provenance; all four frozen workload performance gates. No formal proof has run. No performance improvement is claimed. A failing relevant invariant or observable mismatch blocks promotion.

The next experiment should measure whether removing recursive mapper control flow warrants integration. If it does, constructor-built plans must account for added mapper layout and plan memory against unchanged production, with no reuse of diagnostic timings. This mechanism preserves work effects; it does not establish that the small mapper subsystem can deliver the entire 10× target.

## Completed first pilot

Validation63568 and benchmark75008 exited0. Four focused tests passed normal/race/checkptr; verify.py independently checked raw coverage, source hashes and five observations per mechanism. Median recursive259.2ns, plan87.45ns (2.964× ratio), zero query allocations for both. Fixed-order synthetic32-link chain excludes construction and retained memory and is not a compiler performance claim. Proceed to nested history coverage and construction/shallow-chain cost evaluation before integration. Production remains unchanged.
