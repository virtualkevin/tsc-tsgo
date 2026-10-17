# Indexed symbol links pilot

This is an unapplied experimental implementation of the indexed-storage strategy from the user-supplied OPTI_ANALYSIS_01.md. Production retains the saturated-keybuilder implementation. The analysis document is not copied into this archive.

Read AUDIT.md and metadata.json for the ownership contract, costs, three comparison variants and outstanding gates. Six focused tests pass in each of normal, race and checkptr overlay runs; raw logs and their hashes are preserved. This is not a full compiler correctness or performance result.

The patches are the canonical formatted source changes. handles.patch applies to the restored production source and retains the original PointerLinkStore. indexed-over-handles.patch adds the indexed store to that control. indexed-combined.patch applies both directly to the restored production source. Do not apply both handles.patch and indexed-combined.patch together.

prepare.py and validate-focused.py preserve the exact preparation and execution used here. They use the original absolute workspace and /tmp paths. To reproduce in the same workspace, copy this directory to a fresh /tmp/tsc-indexed-symbol-pilot directory, leaving out focused-validation, then run prepare.py and validate-focused.py. Preparation requires the unchanged base files whose hashes are listed in metadata.json and the original analysis document; it regenerates full formatted overlay copies and absolute overlay mappings. It does not modify production. On a different machine, update those paths explicitly. Generated preparation metadata represents the new run rather than these historical results.

No compiler binary or large full checker/binder overlay copy is archived. The production-source hash in the validation summary identifies the restored baseline; the recorded Git HEAD still includes the relation-cache candidate because its rollback had not yet been committed.
