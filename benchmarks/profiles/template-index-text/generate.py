"""Generate a single file with disjoint template indexes and one query per index."""
from pathlib import Path
import sys

path = Path(sys.argv[1])
count = int(sys.argv[2])
assert count > 0
declarations = ["interface Entries {"]
for i in range(count):
    declarations.append(f"  [key: `k{i}/${{string}}`]: {i};")
declarations.append("}")
for i in range(count):
    declarations.append(f"declare const value{i}: Entries[`k{i}/${{number}}`];")
    declarations.append(f"export const check{i}: {i} = value{i};")
path.write_text("\n".join(declarations) + "\n")
