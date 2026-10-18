# Member materialization selection audit

After rejecting carried canonical names, inspect the retained compiler's temporary member-table construction before proposing another representation change. This is offline analysis of existing normal-flag profiles, not a new workload measurement. `analyze.py --check` reproduces `report.json` and hashes its source/report inputs.

The selected nearest-project map callers are ownTable, addInheritedMembers, getNamedMembers, and keepTableOnDemand. Their disjoint sampled CPU shares total 1.523% on tRPC, 0.176% on TypeORM, 0.710% on VS Code, and 1.144% on Sentry. These are only map-path samples attributed to those functions, not all materialization CPU or removable runtime. The historical allocation profiles put addInheritedMembers at 167.17 MB on Sentry and 39.65 MB on VS Code; cumulative sampled allocation is not live memory or a runtime budget.

Source constraints:

- ownTable visits entries in frozen source order, preserves earlier duplicate-name instantiation side effects, and lets later non-skipped entries overwrite earlier entries. A final-name index alone cannot replace this loop.
- materialize clears pendingMembers before constructing symbols. Recursive observation can therefore differ if a replacement publishes a partially built slice or keeps the pending record visible.
- Inherited members skip static private identifiers and replace existing non-value symbols. Base property access can itself materialize other pending types.
- During recursive base resolution, properties expose only the own-member subset while the published table continues to receive inherited entries. This path must retain a mutable table.
- getNamedMembers filters reserved/non-value entries and sorts declared members before inherited members for classes/interfaces. Alias classification can resolve symbols; reversing or bypassing evaluation is not automatically equivalent.
- Completed materialization already discards the temporary map when every entry is represented by a named property. It retains a shared name layout plus per-instance properties, releasing checker/source/mapper/state/base references. The remaining opportunity is avoiding transient construction, not newly removing a permanent map.
- Members() can demand reconstruction of an actual mutable table later. Existing API and recursive-inheritance tests constrain this boundary.

The earlier pending-member-index experiment changed sparse per-instance lookup caching, not this materialization path, and failed screening. It is not reopened. A no-base-only bypass would cover a narrower subset than the allocation lead and has no measured eligibility or cost evidence. Before implementing complete map-free materialization, establish how frequently completed instances share usable layouts, need inherited merges, or immediately demand tables. Keep construction order and mutable recursive states explicit. No production change or speedup claim is made here.
