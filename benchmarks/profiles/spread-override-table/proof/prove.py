"""Map-state refinement model, not a Go or whole-compiler proof."""
from pathlib import Path
import hashlib,json
import z3
p=Path(__file__).resolve().parent;profile=p.parent
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
s=(profile/'staged/checker.go').read_text();a=s.index('func (c *Checker) checkObjectLiteral(');b=s.index('func (c *Checker) checkSpreadPropOverrides(',a);body=s[a:b]
# Fail closed if the named private table obtains additional consumers/writers.
uses=[line.strip() for line in body.splitlines() if 'allPropertiesTable' in line]
expected=['var allPropertiesTable ast.SymbolTable','if elem.Kind == ast.KindSpreadAssignment && c.strictNullChecks && allPropertiesTable == nil {','allPropertiesTable = make(ast.SymbolTable)','if allPropertiesTable != nil {','allPropertiesTable[prop.Name] = prop','if allPropertiesTable != nil {','c.checkSpreadPropOverrides(mergedType, allPropertiesTable, memberDecl)']
assert uses==expected
strict,has_spread,read_spread,property_write=z3.Bools('strict has_spread read_spread property_write')
name=z3.BitVec('name',32);symbol=z3.BitVec('symbol',32);lookup=z3.BitVec('lookup',32)
Map=z3.ArraySort(z3.BitVecSort(32),z3.BitVecSort(32));old,new=z3.Consts('old new',Map);empty=z3.K(z3.BitVecSort(32),z3.BitVecVal(0,32))
old_enabled=strict;new_enabled=z3.And(strict,has_spread)
rows=[]
def prove(name, assumptions, counterexample, want='unsat'):
 solver=z3.Solver();solver.add(*assumptions,counterexample);result=str(solver.check());assert result==want,(name,result)
 row={'name':name,'result':result,'assertions':[str(x) for x in solver.assertions()]}
 if result=='sat':row['model']=str(solver.model())
 rows.append(row)
# Reachable spread implies the prepass found one, so allocation eligibility matches.
prove('spread-read-eligibility',[z3.Implies(read_spread,has_spread)],z3.And(read_spread,old_enabled!=new_enabled))
# In the spread domain both tables start empty, and every arbitrary property store
# preserves array equality, including duplicate keys and arbitrary symbol identities.
prove('spread-domain-initial-state',[strict,has_spread],z3.If(old_enabled,empty,old)!=z3.If(new_enabled,empty,old))
old_next=z3.If(z3.And(property_write,old_enabled),z3.Store(old,name,symbol),old)
new_next=z3.If(z3.And(property_write,new_enabled),z3.Store(new,name,symbol),new)
prove('spread-domain-step',[strict,has_spread,old==new],old_next!=new_next)
prove('spread-query-equality',[strict,read_spread,z3.Implies(read_spread,has_spread),old==new],z3.Select(old_next,lookup)!=z3.Select(new_next,lookup))
prove('no-spread-domain-unobservable',[z3.Not(has_spread),z3.Implies(read_spread,has_spread)],read_spread)
# A deliberately broken policy allocates at the first spread in the MAIN loop.
# Its empty map loses a preceding property and must have a counterexample.
prove('broken-main-loop-lazy-allocation-control',[symbol!=0],z3.Select(z3.Store(empty,name,symbol),name)!=z3.Select(empty,name),'sat')
report={'scope':'Machine-checked array-state induction obligations under a fixed prepass classification and reads only at spreads. Source text pins the named local table sites; it does not prove AST immutability, Go execution, diagnostic equivalence, GC behavior, or whole-compiler correctness. Name/symbol bitvectors model arbitrary equality classes, not actual Go pointer encoding.','solverVersion':z3.get_version_string(),'controllerSha256':sha(__file__),'checkerSha256':sha(profile/'staged/checker.go'),'tableSites':uses,'lemmas':rows}
print(json.dumps(report,indent=2))
