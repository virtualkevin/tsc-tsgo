"""Attribute full CPU stacks and leaf instructions from verified production profiles."""
from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
manifest = json.loads((here / "manifest.json").read_text())
categories = {
    "gcMark": ("runtime.gcDrain", "runtime.gcAssistAlloc", "runtime.gcBgMarkWorker", "runtime.scanObject"),
    "checker": ("typescript-go/internal/checker.",),
    "binder": ("typescript-go/internal/binder.",),
    "parseScan": ("typescript-go/internal/parser.", "typescript-go/internal/scanner."),
    "relations": ("internal/checker.(*Relater).isRelatedToEx",),
    "instantiation": ("internal/checker.(*Checker).instantiateTypeWithAlias",),
    "symbolType": ("internal/checker.(*Checker).getTypeOfSymbol",),
    "allocation": ("runtime.mallocgc",),
    "unionNormalize": ("internal/checker.(*Checker).getUnionTypeWorker",),
    "goMap": ("internal/runtime/maps.", "runtime.mapaccess", "runtime.mapassign"),
    "pointerLinks": ("internal/core.(*PointerLinkStore[", "internal/core.pointerLinkHash["),
}
report = {"families":categories,"projects":{}}
for pname,p in manifest["projects"].items():
    path = here / f"{pname}-cpu.pb.gz"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == p["profiles"]["cpu"]
    raw = subprocess.check_output([sys.argv[1],"tool","pprof","-raw",path],text=True)
    samples,locations = raw.split("Locations\n",1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        m = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)",line)
        if m:
            key = int(m[1])
            frames[key] = []
            line = m[2]
        f = re.fullmatch(r"\s*(.+?) (\S+):(\d+):\d+(?: s=\d+.*)?",line)
        if f:
            frames[key].append((f[1],f[2],int(f[3])))
    cum,only,leaf,callers = Counter(),Counter(),Counter(),Counter()
    initializerCallees = Counter()
    semanticPaths = {family:Counter() for family in ("symbolResolution","relationBranch","instantiateCaller","variableResolution","variableRequest","initializerPath","initializerExpression","initializerOverloadLine","initializerInferenceLine","inferredArgumentHandler")}
    for ns,stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$",samples,re.M):
        weight = int(ns)
        entries = [frame for i in stack.split() for frame in frames[int(i)]]
        if not stack.split() or not frames[int(stack.split()[0])]:
            entries.insert(0, ("<unsymbolized>", "", 0))
        hit = [cat for cat,terms in categories.items() if any(any(t in func for t in terms) for func,_,_ in entries)]
        if "symbolType" in hit:
            # Outermost symbol dispatch assigns each sample to one resolver branch.
            indexes = [i for i,(f,_,_) in enumerate(entries) if f.endswith(".(*Checker).getTypeOfSymbol")]
            name = "<other symbol entry>"
            if indexes:
                i = indexes[-1]
                name = entries[i-1][0].split(".")[-1] if i else "<dispatch>"
            semanticPaths["symbolResolution"][name] += weight
        vi = next((i for i in range(len(entries)-1,-1,-1) if entries[i][0].endswith(".(*Checker).getTypeOfVariableOrParameterOrProperty")),None)
        if vi is not None:
            inner = entries[:vi]
            worker = next((i for i in range(len(inner)-1,-1,-1) if inner[i][0].endswith(".getTypeOfVariableOrParameterOrPropertyWorker")),None)
            if worker is None:
                name = "<links or outer resolver>"
            elif worker == 0:
                name = "<worker dispatch>"
            else:
                name = inner[worker-1][0].split(".")[-1]
            semanticPaths["variableResolution"][name] += weight
            caller = next((f.split("internal/checker.")[-1] for f,_,_ in entries[vi+1:]
                           if "internal/checker." in f and not f.endswith(".getTypeOfSymbol")), "<outside checker>")
            semanticPaths["variableRequest"][caller] += weight
        init = next((i for i in range(len(entries)-1,-1,-1) if entries[i][0].endswith(".(*Checker).checkDeclarationInitializer")),None)
        if init is not None:
            inner = entries[:init]
            overload = next((line for f,_,line in reversed(inner) if f.endswith(".(*Checker).chooseOverload")),None)
            if overload is not None:
                semanticPaths["initializerOverloadLine"][overload] += weight
            inference = next((line for f,_,line in reversed(inner) if f.endswith(".(*Checker).inferTypeArguments")),None)
            if inference is not None:
                semanticPaths["initializerInferenceLine"][inference] += weight
            for opname in ("resolveCallExpression","chooseOverload","inferTypeArguments","getSignatureApplicabilityError","getResolvedSignature","getReturnTypeOfSignature"):
                if any(f.endswith("."+opname) for f,_,_ in inner):
                    initializerCallees[opname] += weight
            if any(f.endswith(".resolveCallExpression") and line == 8475 for f,_,line in inner):
                initializerCallees["resolveCallCalleeExpression"] += weight
            name = inner[-1][0].split("internal/checker.")[-1] if inner else "<dispatch>"
            semanticPaths["initializerPath"][name] += weight
            handlers = {"checkObjectLiteral","checkArrayLiteral","checkFunctionExpressionOrObjectLiteralMethod",
                        "checkArrowFunction","checkCallExpression","checkNewExpression","checkTaggedTemplateExpression",
                        "checkIdentifier","checkPropertyAccessExpression","checkElementAccessExpression",
                        "checkBinaryExpression","checkConditionalExpression","checkJsxElement","checkJsxSelfClosingElement"}
            expr = next((f.rsplit(".",1)[-1] for f,_,_ in reversed(inner) if "(*Checker)." in f and f.rsplit(".",1)[-1] in handlers),"<other>")
            semanticPaths["initializerExpression"][expr] += weight
            if inference == 9464:
                outer = max(i for i,(f,_,_) in enumerate(inner) if f.endswith(".(*Checker).inferTypeArguments"))
                handler = next((f.rsplit(".",1)[-1] for f,_,_ in reversed(inner[:outer]) if "(*Checker)." in f and f.rsplit(".",1)[-1] in handlers),"<other>")
                semanticPaths["inferredArgumentHandler"][handler] += weight
        if "relations" in hit:
            branches = {"propertiesRelatedTo","propertyRelatedTo","signaturesRelatedTo","signatureRelatedTo",
                        "indexSignaturesRelatedTo","typeRelatedToSomeType","eachTypeRelatedToType",
                        "typeRelatedToEachType","unionOrIntersectionRelatedTo","structuredTypeRelatedTo"}
            branch = next((f.rsplit(".",1)[-1] for f,_,_ in entries if "(*Relater)." in f and f.rsplit(".",1)[-1] in branches), "<other relation work>")
            semanticPaths["relationBranch"][branch] += weight
        if "instantiation" in hit:
            i = max(i for i,(f,_,_) in enumerate(entries) if "internal/checker.(*Checker).instantiateTypeWithAlias" in f)
            name = next((f.split("internal/checker.")[-1] for f,_,_ in entries[i+1:] if "internal/checker." in f and not f.endswith(".instantiateType")), "<outside checker>")
            semanticPaths["instantiateCaller"][name] += weight
        only["+".join(hit) or "other"] += weight
        for cat in hit:
            cum[cat] += weight
        if "goMap" in hit:
            # Innermost sampled map operation, then the nearest compiler caller.
            start = next(i for i,(f,_,_) in enumerate(entries) if any(t in f for t in categories["goMap"]))
            source = next(((file,line) for _,file,line in entries[start+1:]
                           if "typescript-go/" in file), None)
            key = ("%s:%d" % source).split("typescript-go/")[-1] if source else "<runtime or other>"
            callers[key] += weight
        _,file,line = entries[0]
        if file.endswith("/pointerlinkstore.go"):
            leaf[line] += weight
    phases = Counter()
    for bucket,weight in only.items():
        families = set(bucket.split("+"))
        phase = next((x for x in ("gcMark","checker","binder","parseScan") if x in families), "other")
        phases[phase] += weight
    total = only.total()
    assert phases.total() == total
    assert total > 0 and callers.total() == cum["goMap"]
    report["projects"][pname] = dict(initializerOperationNs=initializerCallees,semanticPathsNs={k:dict(v.most_common()) for k,v in semanticPaths.items()},totalCpuNs=total,exclusivePhasesNs=phases,inclusiveNs=cum,exclusiveNs=only,pointerLinkLeafLineNs=leaf,goMapCallerNs=dict(callers.most_common()))
    print(pname, {k: round(v*100/total,2) for k,v in cum.items()}, leaf.most_common(4))
(here/"costs.json").write_text(json.dumps(report,indent=2)+"\n")
