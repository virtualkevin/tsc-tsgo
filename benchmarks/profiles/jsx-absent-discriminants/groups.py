"""Build a checked span-reuse prototype against the measured ordinary Go baseline."""
from pathlib import Path
import json
import subprocess
import sys

here = Path(__file__).resolve().parent
root = here.parents[2]/"packages/tsc-go"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
files = {}
def edit(file, changes):
    data = subprocess.check_output(["git","show","a3ca3d9:packages/tsc-go/"+file],cwd=root,text=True)
    for old,new in changes:
        assert data.count(old) == 1
        data = data.replace(old,new)
    path = out/Path(file).name
    path.write_text(data)
    files[str(root/file)] = str(path)
edit("internal/checker/checker.go",[("type Checker struct {","type Checker struct {\n    absentPlans map[*Type]*absentPropertyPlan")])
site = "discriminated := c.discriminateTypeByDiscriminableItems(contextualType, discriminator)"
edit("internal/checker/jsx.go",[(site,"""var plan *absentPropertyPlan
    eligible := len(discriminantProperties)==0 && len(discriminantMembers)>=8 && len(contextualType.Types())<=16
    if eligible {
        plan = c.absentPlans[contextualType]
        if plan!=nil && !slices.Equal(discriminantMembers,plan.members) {plan=nil}
    }
    discriminated := c.discriminateWithAbsentPlan(contextualType, discriminator, plan)
    if eligible && plan==nil {
        if c.absentPlans == nil { c.absentPlans=make(map[*Type]*absentPropertyPlan) }
        c.absentPlans[contextualType]=c.makeAbsentPropertyPlan(contextualType.Types(),discriminantMembers)
    }""")])
site = "func (c *Checker) discriminateTypeByDiscriminableItems(target *Type, discriminator Discriminator) *Type {"
edit("internal/checker/relater.go",[(site,site+"""
    return c.discriminateWithAbsentPlan(target, discriminator, nil)
}

func (c *Checker) discriminateWithAbsentPlan(target *Type, discriminator Discriminator, plan *absentPropertyPlan) *Type {"""),
("for n := range discriminator.len() {","""spanIndex := 0
    for n, count := 0, discriminator.len(); n<count; n++ {
        if plan!=nil && spanIndex<len(plan.spans) && n==plan.spans[spanIndex].start {
            span:=plan.spans[spanIndex]
            spanIndex++
            if c.validAbsentSpan(span, types, plan.members) {
                n=span.end-1
                continue
            }
        }""")])
files[str(root/"internal/checker/absent_groups.go")] = str(here/"groups.go.txt")
if "--linked" in sys.argv[2:]:
    files[str(root/"internal/checker/absent_groups.go")] = str(here/"groups_links.go.txt")
    path = out/"checker.go"
    source = path.read_text()
    site = "cache[name] = prop\n\t\t// Propagate an entry"
    assert source.count(site) == 1
    path.write_text(source.replace(site, "c.publishLookupProperty(cache,name,prop,skipObjectFunctionPropertyAugment)\n\t\t// Propagate an entry"))
    path = out/"relater.go"
    path.write_text(path.read_text().replace("c.validAbsentSpan(span, types, plan.members)", "c.validLinkedSpan(target, plan, span)"))
(out/"overlay.json").write_text(json.dumps({"Replace":files}))
files[str(root/"internal/checker/absent_groups_test.go")] = str(here/"groups_test.go.txt")
if "--linked" in sys.argv[2:]:
    test = (here/"groups_test.go.txt").read_text()
    test = test.replace("compare := func", "c.absentPlans = map[*Type]*absentPropertyPlan{target: plan}\n\tcompare := func")
    test = test.replace('cache["first"] = replacement', 'c.publishLookupProperty(cache, "first", replacement, true)\n\tif c.absentPlans[target] != nil { t.Fatal("replaced property retained the plan") }')
    testPath = out/"linked_test.go"
    testPath.write_text(test)
    files[str(root/"internal/checker/absent_groups_test.go")] = str(testPath)
(out/"test-overlay.json").write_text(json.dumps({"Replace":files}))
