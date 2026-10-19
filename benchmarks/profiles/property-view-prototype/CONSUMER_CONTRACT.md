# Consumer integration obligations

Reviewed against retained production at7e593fc; not a proof or implemented consumer.

1. `getUnmatchedPropertiesWorker` obtains target enumeration first, then calls `isUnmatchedProperty` in its contractual order. Do not substitute source-entry order for `getNamedMembers` order: it groups declared versus inherited members and invokes the checker symbol comparator.
2. `isUnmatchedProperty` skips static private identifiers and optional/partial members before source lookup. Non-discriminant mode needs only source presence. Discriminant mode then queries target type and, for unit targets, source type. Preserve those operations and order.
3. Source presence is not a bare pending-name lookup. `getPropertyOfTypeEx` reduces apparent types, resolves members, handles module type-only exports/value classification, and falls back to Function/Object augmentation. A pending own view is usable only after proving it denotes the same successful value property. Absent or unsupported must use the full original path.
4. `propertyRelatedTo` checks nominal accessibility, readonly strict subtyping, type relation, then optionality. Optionality rejection cannot be moved before the type query merely because metadata is available: it would remove ordered effects.
5. `getDeclarationModifierFlagsFromSymbolEx` can inspect accessor declarations, parent class flags and synthetic check flags. The current metadata tuple is insufficient as a general replacement Symbol. Resolve a symbol or extend the explicit view contract; do not silently drop declaration-list behavior.
6. The target property's type is queried before the source's in `isPropertySymbolTypeRelated`. An any/unknown target may short-circuit the source query. Preserve this along with reportErrors and relation kind.
7. View materialization must use the owner cache after any Properties/Members transition. Keep original symbol pointer-equality distinctions and private declaration identity; equal name/type text is insufficient.

Next supported consumer domain should be a precise successful own-property presence check over an already resolved, non-module object, with fallback before additional semantic effects. This does not itself justify a general property-relation rewrite. Measure eligibility and allocation reduction before expanding; no performance budget can be inferred from the full property-path CPU union for this restricted domain.
