# Optional symbol storage: proposed refinement contract

This is a reviewed design argument, not a proof or implemented optimization.
The current census is diagnostic only. A future candidate must map each retained
Symbol to one stable candidate Symbol for its entire promised lifetime. Flags,
CheckFlags, Name, Declarations, ValueDeclaration, id and Parent remain unchanged.

For each old Symbol s and corresponding candidate t:

- t with no optional record represents exactly three nil fields.
- Reading Members/Exports/ExportSymbol must return the original map or pointer,
  without allocating or resolving anything; nil and non-nil empty maps differ.
- Field assignment must install precisely the supplied map or Symbol pointer.
  Reassigning one field cannot overwrite either other field.
- GetMembers/GetExports retain their lazy map initialization. They return the
  same map on repeated calls; mutations through previously returned maps remain
  visible. Assigning a replacement map does not mutate the old map.
- Assigning nil must preserve observable values. Whether an empty optional record
  remains allocated is a storage choice, but the census cannot measure peak or
  historical occupancy and cannot justify a reclamation policy.
- cloneSymbol and cloneTypeAsModuleType continue independently cloning Members
  and Exports. A shallow copy of a cold-record pointer would be insufficient.
  Other merge/clone/literal construction paths need a complete type-aware audit.
- All references remain typed Go pointers/maps. No uintptr decoder or implicit
  checker-wide strong symbol registry is introduced. Reachability of values
  returned before replacement must follow the existing language/API rules.
- The change does not add support for arbitrary concurrent mutation of a Symbol.
  Initialization/publication must retain the existing binder/checker ordering;
  race instrumentation is required to detect implementation mistakes.

Source anchors in retained packages/tsc-go:
internal/ast/symbol.go (fields), internal/ast/utilities.go (GetMembers/GetExports),
internal/checker/checker.go (cloneSymbol, cloneTypeAsModuleType,
getGlobalImportMetaExpressionType), internal/binder/binder.go (declareModuleMember).
These examples identify obligations, not an exhaustive access inventory.

Nominal amd64 record arithmetic is 96 bytes versus 80 + 24*p, where p is the
fraction requiring the optional record. The nominal break-even point p < 2/3
excludes allocator rounding, arena retention, transient states, pointer scanning,
lookup indirection, write barriers and the extra allocation's CPU cost. Surviving
weak samples are not a population estimate of p. No end-to-end gain follows from
this arithmetic; full correctness and the frozen workload gates remain necessary.
