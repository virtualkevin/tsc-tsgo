# Direct instantiation loops

Isolated compiler candidate based on retained production at 9896df6. Four typed
list functions execute the existing generic instantiateList body with direct
instantiation method calls. The generic helper remains unchanged as a test
reference. No compiler source or default executable has been replaced.

The proposed mechanism is removing callback/dictionary dispatch and exposing
concrete pointer element operations to the Go compiler. It does not remove
semantic instantiations or their effects. This is a local execution experiment,
not evidence of an order-of-magnitude compiler gain. Generated code and workload
performance remain unmeasured at preparation.

## Correspondence contract

Each direct traversal executes exactly the same element calls in the same order,
using the same Checker and TypeMapper. Until the first changed result it returns
and retains the original backing slice, including nilness and capacity. At the
first changed result it allocates the same length, then copies the current prefix,
stores that result, and reads/instantiates later elements one at a time. It does
not pre-copy or snapshot later inputs: callbacks may change them. Allocation
identity of returned semantic objects, query effects, recursive state and limit
checks remain delegated to the same methods. Signature return types remain lazy.

source-audit.py reconstructs all four candidate functions directly from the
unchanged generic body and requires exact equality of the complete file. This is
a source correspondence check, not formal Go compiler verification. Focused tests
compare actual generic/direct operations on independent checkers, normalized
identity, slice alias/capacity, invocation histories, counters, mutable later
inputs, symbols, index metadata and lazy signature state. The same tests run with
both candidate and retained overlays in normal, race and checkptr modes.

No promotion before full pinned conformance, API/CLI/emit parity and the fixed
paired compiler workload policy. PERF.md receives only actual compiler workload
measurements. The 10× target remains unmet.

## Generated code evidence

Normal test builds completed on both overlays. Independent readback reproduced
both objdump outputs from their hashed binaries. Each retained generic loop has
two indirect CALL DI sites; each candidate typed loop instead has two direct
instantiation callsites and no register-indirect calls. The type and signature
wrappers inline to instantiateTypeWithAlias and instantiateSignatureEx. Candidate
bodies contain 110/104/110/104 instructions (453/443/467/443 instruction bytes).
These counts are static code size, not executed instructions or runtime savings.
Generic helpers still occur in the candidate test binary because the differential
tests explicitly call them. The baseline thin wrappers were inlined into callers.

## Validation checkpoint

Candidate and retained focused runs passed four tests each in normal, race and
checkptr modes (24 total records). Full compiler validation passed 21179 root
records across 14 packages, 219 services records, and all 14915 pinned conformance
configurations: 12789 fully checked, 8 partially checked, 2118 unsupported, zero
failures. CLI parity passed 80 normal, 80 race and 80 checkptr tests; API/emit
integration passed 12. Independent verification checks archived logs, source
identity, instrumented flags and current binary hashes. Duplicate full raw logs
were removed only after exact gzip readback; archives and manifest remain.

Normal production provenance build succeeded with exactly two source differences,
5155 candidate files versus 5154 retained, and matches the validated normal
executable. Retained source and default binary were restored. Frozen screen input
and provenance preflight passed. No performance capture has run at this checkpoint.
