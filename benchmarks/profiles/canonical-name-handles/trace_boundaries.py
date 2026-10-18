"""Archive reviewed migration decisions for the 39 remaining typed read sites."""
import hashlib
import json
from pathlib import Path
out = Path(__file__).resolve().parent
root = out.parents[2]
module = root / 'packages/tsc-go'
inventory_path = out.parent / 'canonical-name-flow/inventory.json'
inventory = json.loads(inventory_path.read_text())
# Manual decisions, not inferred interprocedural/dynamic dataflow.
routes = {
'declareSymbolEx': ('declaration', 'Carry a declaration-name handle from getDeclarationName; canonical constants for computed/default/missing. Decode only for existing string classifiableNames until that index is migrated.'),
'bindDeferredExpandoAssignment': ('declaration', 'Use the same getDeclarationName handle as declaration insertion; keep dynamic-name handling unchanged.'),
'lookupEntity': ('syntax', 'Use identifier NameKey directly; property access may also supply string/numeric literals, requiring exact existing Text conversion at that boundary.'),
'lookupName': ('recursive-query', 'Carry one name through locals and exports; identifier caller supplies its stored handle.'),
'declareCommonJSVariable': ('boundary', 'Convert supplied CommonJS name once, reuse for lookup and construction.'),
'Resolve': ('recursive-query', 'Carry one name across scope traversal, lookup callback, module exports and globals. Keep diagnostics/callback string arguments explicit.'),
'lookup': ('recursive-query', 'Match NameResolver.Lookup and checker getSymbol name types so scope traversal does not recanonicalize.'),
'addUndefinedToGlobalsOrErrorOnRedeclaration': ('stored-symbol', 'Local name aliases undefinedSymbol.Name; preserve handle through lookup.'),
'getSymbol': ('recursive-query', 'Carry NameResolver supplied handle through merged-symbol lookup.'),
'getIterationTypesOfMethod': ('boundary', 'Method-name argument is reused in property and generator/iterator table queries; canonicalize once at caller boundary, not each lookup.'),
'checkAliasSymbol': ('syntax', 'PropertyNameOrName can contain module export names; NameKey must preserve non-identifier literal text behavior.'),
'checkPropertyAccessExpressionOrQualifiedName': ('syntax', 'Carry right identifier key through property lookup and globalThis diagnostic lookup.'),
'lookupSymbolForPrivateIdentifierDeclaration': ('synthesized', 'Keep class-specific GetSymbolNameForPrivateIdentifier construction unchanged; canonicalize its result once per containing class and reuse for members/exports. Never intern only the visible private spelling.'),
'resolveExportByName': ('recursive-query', 'Carry same key into export-equals property resolution and module exports; diagnostics decode text.'),
'getExportOfModule': ('recursive-query', 'Pass NameKey from syntax callers or convert once from string API boundary; reuse in export lookup and error paths.'),
'reportNonExportedMember': ('syntax', 'Use NameKey for source module-export-name node, decoding text for diagnostics.'),
'resolveExternalModule': ('string-domain', 'patternAmbientModuleAugmentations is keyed by module-reference text; retain a string-keyed dictionary, rather than making all module resolution strings semantic names.'),
'lateBindMember': ('synthesized', 'getPropertyNameFromType includes string literal bytes, jsnum.Number.String and unique-symbol name. Canonicalize result once and reuse in late/early tables and newSymbolEx.'),
'getExportsOfModuleWorker': ('auxiliary-index', 'id comes from lookupTable range, not SymbolTable range. Migrate that duplicate-export auxiliary index to Name keys alongside exportedSymbols; retain existing duplicate-report ordering rules.'),
'resolveMappedTypeMembers': ('synthesized', 'Canonicalize property-name-type result once per callback and carry to members and constructed symbol; distinct enum types retain their type identities.'),
'getUnionOrIntersectionProperty': ('recursive-query', 'Carry the key through both cache variants, createUnionOrIntersectionProperty, recursive constituents and getResolvedMember; never call MakeName on each constituent.'),
'getUnresolvedSymbolForEntityName': ('string-domain', 'unresolvedSymbols is already map[string]*ast.Symbol, structurally included by the inventory; its key is a composed dotted symbol path; retain this dictionary as string-keyed and keep path construction behavior.'),
'evaluateEntity': ('syntax', 'String-literal element access uses literal text; convert at query boundary, without normalizing numeric-looking strings.'),
'getPropertyTypeForIndexType': ('synthesized', 'getPropertyNameFromIndex yields string/numeric/unique-symbol spelling plus InternalSymbolNameMissing sentinel; preserve hasPropName behavior, convert once and reuse both globalThis reads.'),
'enterNewScope': ('auxiliary-index', 'Migrate addAll callback name, localsRecord and cleanup newLocals together; preserve restoration/delete of previous fake scope members.'),
'ownMember': ('recursive-query', 'Carry the key through source.positions, instantiated members and inherited member resolution; migrate associated positions maps.'),
'pendingInstantiatedTable': ('ordered-index', 'names is copied from table keys and sorted as strings before index assignment. Use Name slice and explicit byte-string comparator, never pointer order; positions uses Name keys.'),
'getResolvedMember': ('recursive-query', 'One handle flows into pendingMembers.get or concrete members, with no conversion in recursive traversal.'),
'getSymbolsInScope': ('stored-symbol', 'id aliases symbol.Name; keep handle through deduplication and table insertion.'),
'TryGetMemberInModuleExports': ('boundary', 'Public string-taking service converts at entry; internal handle-taking lookup can avoid a second conversion.'),
'extractFromSymbol': ('syntax', 'Existing guard limits selected names to identifiers; use stored identifier key.'),
'isUniqueLocalName': ('boundary', 'Generated printer spelling remains a string externally; canonicalize once before the ancestor loop and reuse across scopes.')
}
sites = [s for s in inventory['Sites'] if s['operation'] == 'table-read' and s['origin'] in ['call-result', 'other-identifier', 'parameter']]
assert len(sites) == 39
assert set(routes) == {s['function'] for s in sites}
records = []
for s in sites:
    path = module / s['file']
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    assert digest == inventory['SourceHashes'][s['file']]
    lines = data.decode().splitlines()
    start = max(1, s['line'] - 6)
    category, decision = routes[s['function']]
    records.append(s | {'sourceSha256': digest, 'category': category, 'decision': decision, 'excerptStart': start, 'excerpt': '\n'.join(lines[start-1:s['line']])})
assert len({(r['file'], r['line'], r['column']) for r in records}) == 39
report = {'scope': 'Manual source-boundary migration decisions for all 39 remaining current-platform typed read sites. Not complete transitive call-graph analysis, dynamic conversion counts, implementation or speed evidence.', 'inventorySha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(), 'sites': records}
(out / 'boundaries.json').write_text(json.dumps(report, indent=2) + '\n')
print('Traced', len(records), 'sites in', len(routes), 'functions')
