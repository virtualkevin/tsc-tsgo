"""Generate distinct generic properties with one shared union type."""
from pathlib import Path
import sys

width = int(sys.argv[2])
assert width > 0
lines = ["interface Fields<A, B> {"]
lines.extend(f"    p{i}: string | A | B;" for i in range(width))
lines.extend(["}", "declare const fields: Fields<number, boolean>;"])
lines.extend(f"export const value{i} = fields.p{i};" for i in range(width))
Path(sys.argv[1]).write_text("\n".join(lines)+"\n")
