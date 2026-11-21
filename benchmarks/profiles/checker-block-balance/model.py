"""Replay fixed file costs to compare locality in blocks with checker load."""
import gzip
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
inputs = here.parent / "contiguous-checker-locality/file-cost-results"
report = {}


def assign(files, workers, blocks_per_worker):
    # Keep skipped files in their original round-robin affinity.
    owners = [i % workers for i in range(len(files))]
    checked = [(i, max(1, f["Nodes"])) for i, f in enumerate(files) if f["Checked"]]
    target = max(1, sum(weight for _, weight in checked) // (workers * blocks_per_worker))
    blocks = []
    current = []
    cost = 0
    for index, weight in checked:
        if current and cost + weight > target:
            blocks.append((cost, current))
            current, cost = [], 0
        current.append(index)
        cost += weight
    if current:
        blocks.append((cost, current))
    loads = [0] * workers
    for cost, block in sorted(blocks, key=lambda item: -item[0]):
        worker = min(range(workers), key=loads.__getitem__)
        loads[worker] += cost
        for i in block:
            owners[i] = worker
    return owners, len(blocks)


def summarize(rows, owners):
    loads = [0] * 4
    adjacent = visits = 0
    prev = None
    for row, owner in zip(rows, owners, strict=True):
        loads[owner] += row["ElapsedNS"]
        if row["Checked"]:
            if prev is not None:
                visits += 1
                adjacent += int(owner == prev)
            prev = owner
    return {"maxWorkerNS": max(loads), "sumWorkerNS": sum(loads), "adjacentSame": adjacent,
            "adjacentCheckedPairs": visits}


for run in json.loads((inputs / "report.json").read_text())["runs"]:
    project, mode = run["project"], run["scheduler"]
    raw = gzip.decompress((inputs / f"{project}-{mode}.jsonl.gz").read_bytes())
    assert hashlib.sha256(raw).hexdigest() == run["logSha256"]
    batches = []
    for line in raw.splitlines():
        rows = json.loads(line)
        if not any(row["Checked"] for row in rows):
            continue
        assert {r["Checker"] for r in rows} == set(range(4))
        original = summarize(rows, [r["Checker"] for r in rows])
        block_counts = {}
        for splits in (2, 4, 8, 16, 32):
            owners, blocks = assign(rows, 4, splits)
            summary = summarize(rows, owners)
            assert summary["sumWorkerNS"] == original["sumWorkerNS"]
            block_counts[splits] = {**summary, "blocks": blocks}
        peaks = []
        for worker in range(4):
            checked = [row for row in rows if row["Checker"] == worker and row["Checked"]]
            busiest = max(checked, key=lambda row: row["Instantiations"])
            peaks.append({"file": busiest["File"], "worker": worker, "checkedFileIndex": checked.index(busiest),
                          "instantiations": busiest["Instantiations"], "elapsedNS": busiest["ElapsedNS"]})
        batches.append({"observed": original, "blockAssignments": block_counts,
                        "totalInstantiations": sum(row["Instantiations"] for row in rows),
                        "highestInstantiationCallbackPerWorker": peaks})
    assert len(batches) == 1
    report.setdefault(project, {})[mode] = batches[0]
    x = batches[0]
    print(project, mode, [(k, round(original["maxWorkerNS"]/v["maxWorkerNS"], 3),
                           round(v["adjacentSame"]/v["adjacentCheckedPairs"], 3)) for k,v in x["blockAssignments"].items()])
(here / "model.json").write_text(json.dumps(report, indent=2)+"\n")
