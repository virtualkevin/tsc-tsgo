"""Exercise substitution of optional generic event handlers under one mapper."""
from pathlib import Path
import sys

width = int(sys.argv[2])
assert width > 0
lines = [
    "interface SyntheticEvent<T> { currentTarget: T }",
    'type EventHandler<E> = { bivarianceHack(event: E): void }["bivarianceHack"];',
    "type ReactEventHandler<T> = EventHandler<SyntheticEvent<T>>;",
    "interface Props<T, U> {",
    "    context: U;",
]
lines.extend(f"    onEvent{i}?: ReactEventHandler<T>;" for i in range(width))
lines.extend(["}", "declare const props: Props<HTMLDivElement, string>;"])
if sys.argv[3:] == ["--array"]:
    lines.append("export const callbacks = [")
    lines.extend(f"    props.onEvent{i}," for i in range(width))
    lines.append("];")
else:
    lines.extend(f"export const callback{i} = props.onEvent{i};" for i in range(width))
Path(sys.argv[1]).write_text("\n".join(lines)+"\n")
