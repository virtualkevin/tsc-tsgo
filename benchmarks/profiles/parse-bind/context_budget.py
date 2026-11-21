"""Partition contextual expression checks by the first expression handler they invoke."""
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
    children = {}
    details = {}
    total = 0
    for weight, stack in re.findall(r"^\s*\d+\s+(\d+):\s*([\d ]+)$", samples, re.M):
        total += int(weight)
        methods = [f.split(".(*Checker).")[1] for loc in reversed(stack.split())
                   for f in reversed(frames[int(loc)]) if "internal/checker.(*Checker)." in f]
        if "checkExpressionWithContextualType" in methods:
            index = methods.index("checkExpressionWithContextualType")
            path = methods[index+1:]
            # Outermost entry charges nested contexts only once.
            handlers = {"checkObjectLiteral", "checkArrayLiteral", "checkCallExpression",
                        "checkFunctionExpressionOrObjectLiteralMethod", "checkArrowFunction",
                        "checkJsxAttributes", "checkBinaryExpression", "checkIdentifier",
                        "checkPropertyAccessExpression", "checkElementAccessExpression",
                        "checkConditionalExpression", "checkJsxSelfClosingElement", "checkJsxElement"}
            key = next((method for method in path if method in handlers), "other")
            costs[key] += int(weight)
            if key != "other":
                index = path.index(key) + 1
                child = path[index] if index < len(path) else "<handler or non-checker code>"
                if child in {"contextuallyCheckFunctionExpressionOrObjectLiteralMethod", "getResolvedSignature",
                             "createJsxAttributesTypeFromAttributesProperty", "checkPropertyAssignment"}:
                    inner = path[index+1:]
                    branch = next((m for m in inner if m not in {
                        "checkExpression", "checkExpressionEx", "checkExpressionWorker", "checkExpressionCached",
                        "checkExpressionCachedEx", "getResolvedSignatureWorker", "getResolvedSignatureEx",
                        "doWithContext"}), "<local work>")
                    details.setdefault(f"{key}/{child}", Counter())[branch] += int(weight)
                children.setdefault(key, Counter())[child] += int(weight)
    report[name] = dict(totalCPUSeconds=total/1e9, contextualCPUSeconds=sum(costs.values())/1e9,
                        byHandlerCPUSeconds={k:v/1e9 for k,v in costs.most_common()},
                        nextCheckerMethodCPUSeconds={handler: {k:v/1e9 for k,v in rows.most_common()}
                                                     for handler,rows in children.items()},
                        detailCPUSeconds={label: {k:v/1e9 for k,v in rows.most_common()}
                                          for label,rows in details.items()})
(here / "context-budget.json").write_text(json.dumps(report, indent=2) + "\n")
