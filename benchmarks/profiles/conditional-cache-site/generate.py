"""Generate a distributed Extract input with independent object union sources."""
from pathlib import Path
import sys
count=int(sys.argv[2])
assert count>=1
lines=["interface Base { stamp: number }"]
for i in range(count):
    lines.append(f'interface Input{i} extends Base {{ type: "e{i}"; value: {i}; }}')
sources=" | ".join(f"Input{i}" for i in range(count))
events=" | ".join(f'(Base & {{ type: "e{i}"; value: {i} }})' for i in range(count))
lines += [f"type Events = {events};", f"declare const input: {sources};",
          'declare function inferKey<K extends string>(value: Extract<Events, { type: K }>): K;',
          'export const key = inferKey(input);']
Path(sys.argv[1]).write_text("\n".join(lines)+"\n")
