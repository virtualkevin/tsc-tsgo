"""Charge each sample once to the outermost body-return inference and its branch."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

here = Path(__file__).resolve().parent
profiles = here.parent / "shipped-cpu-costs"
manifest = json.loads((profiles / "manifest.json").read_text())
report = {}
for name, project in manifest["projects"].items():
    path = profiles / f"{name}-cpu.pb.gz"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == project["profiles"]["cpu"]
    raw = subprocess.check_output([sys.argv[1], "tool", "pprof", "-raw", path], text=True)
    samples, locations = raw.split("Locations\n", 1)
    frames = {}
    for line in locations.split("Mappings\n")[0].splitlines():
        location = re.match(r"^\s*(\d+):\s+0x[\da-f]+(?: M=\d+)?\s+(.*)", line)
        if location:
            slot = frames[int(location[1])] = []
            line = location[2]
        frame = re.fullmatch(r"\s*(.+?) (\S+):\d+:\d+(?: s=\d+.*)?", line)
        if frame:
            slot.append(frame[1])
    costs = Counter()
    deferred = Counter()
    block = Counter()
    statement_calls = Counter()
    applicable = Counter()
    total = 0
    for weight, stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$", samples, re.M):
        total += int(weight)
        methods = [f.split(".(*Checker).")[1] for loc in reversed(stack.split())
                   for f in reversed(frames[int(loc)]) if "internal/checker.(*Checker)." in f]
        for i, method in enumerate(methods):
            if method == "checkFunctionExpressionOrObjectLiteralMethodDeferred":
                branch = methods[i+1] if i+1 < len(methods) else "<local>"
                deferred[branch] += int(weight)
                if branch == "checkSourceElement":
                    suffix = methods[i+1:]
                    statement = next((m for m in suffix if m.endswith("Statement") or m in {
                        "checkVariableDeclaration", "checkVariableLikeDeclaration", "checkFunctionDeclaration",
                        "checkClassDeclaration", "checkExpressionStatement"}), "<other>")
                    expression = next((m for m in suffix if m in {
                        "checkCallExpression", "checkNewExpression", "checkObjectLiteral", "checkBinaryExpression",
                        "checkIdentifier", "checkArrayLiteral", "checkPropertyAccessExpression",
                        "checkJsxElement", "checkJsxSelfClosingElement"}), "<other>")
                    block[(statement, expression)] += int(weight)
                    if statement == "checkExpressionStatement" and expression == "checkCallExpression":
                        rest = suffix[suffix.index(expression)+1:]
                        direct = rest[0] if rest else "<local>"
                        category = next((m for m in rest if m in {"isSignatureApplicable",
                            "inferTypeArguments", "checkExpressionOrQualifiedName", "getApparentType",
                            "getReturnTypeOfSignature", "getTypeOfSymbol", "getSignaturesOfType",
                            "checkPropertyAccessExpression", "checkIdentifier"}), "<other>")
                        statement_calls[(direct, category)] += int(weight)
                        if category == "isSignatureApplicable":
                            children = rest[rest.index(category)+1:]
                            child = children[0] if children else "<local>"
                            arg = next((m for m in children if m in {
                                "checkObjectLiteral", "checkFunctionExpressionOrObjectLiteralMethod",
                                "checkArrayLiteral", "checkCallExpression", "checkNewExpression",
                                "checkPropertyAccessExpression", "checkIdentifier", "checkBinaryExpression",
                                "checkConditionalExpression", "checkJsxAttributes"}), "<other>")
                            applicable[(child, arg)] += int(weight)
                break
        if "getReturnTypeFromBody" not in methods:
            continue
        i = methods.index("getReturnTypeFromBody")
        path = methods[i+1:]
        # Preserve the first concrete expression handler along the selected path.
        leaf = next((m for m in path if m in {
            "checkCallExpression", "checkIdentifier", "checkPropertyAccessExpression", "checkElementAccessExpression",
            "checkBinaryExpression", "checkArrayLiteral", "checkObjectLiteral", "checkNewExpression",
            "checkConditionalExpression", "checkFunctionExpressionOrObjectLiteralMethod", "checkJsxElement",
            "checkJsxSelfClosingElement", "checkAwaitExpression", "checkAsExpression"}), "<other>")
        costs[(methods[i-1] if i else "<other>", path[0] if path else "<local>", leaf)] += int(weight)
    report[name] = {
        "totalCPUSeconds": total / 1e9,
        "statementCallPaths": [
            dict(child=child, descendant=descendant, cpuSeconds=ns / 1e9)
            for (child, descendant), ns in statement_calls.most_common()
        ],
        "applicabilityPaths": [
            dict(child=child, expression=arg, cpuSeconds=ns / 1e9)
            for (child, arg), ns in applicable.most_common()
        ],
        "deferredBlockPaths": [
            dict(statement=statement, expression=expression, cpuSeconds=ns / 1e9)
            for (statement, expression), ns in block.most_common()
        ],
        "deferredBranchesCPUSeconds": {key: ns / 1e9 for key, ns in deferred.most_common()},
        "paths": [
            dict(caller=caller, branch=branch, expression=expression, cpuSeconds=ns / 1e9)
            for (caller, branch, expression), ns in costs.most_common()
        ],
    }
(here / "cpu.json").write_text(json.dumps(report, indent=2) + "\n")
