# CommonJS declaration prepass guard evidence

The archived audits describe the isolated proposal before it was applied. The production change now guards only the CommonJS export-assignment prepass using the bound source file's CommonJSModuleIndicator. The TypeScript expando visitor and declaration diagnostics still run. Current correctness results are recorded separately in ../../validation/cjs-prepass-conformance.json and ../../validation/cjs-prepass-native.json.

The CPU observations come from ../pointer-current/ and identify a bounded opportunity, primarily in TypeORM. Cumulative fractions overlap; the eligible non-CommonJS share was not separately measured. No timing benefit is established by these audits. The source and independent reviews examine the skipped diagnostic and lexical-environment bookkeeping as well as the callback's semantic action. These conclusions apply to the bound compiler pipeline.

The preserved candidate and baseline use the same Go1.26.9 non-PGO build settings. Native differential validation was first unable to launch the preserved candidate because copying its bytes omitted the executable permission. Restoring the original file mode fixes that packaging mistake without changing any compiler or binary bytes. The complete successful rerun, rather than that failed launch, is the correctness evidence.
