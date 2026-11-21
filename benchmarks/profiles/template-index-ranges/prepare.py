"""Stage a checker-local prefix index for wide template index-signature lists."""
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
path = Path("packages/tsc-go/internal/checker/checker.go")
source = subprocess.check_output(["git", "show", f"a6444de:{path}"], cwd=root, text=True)
marker = "type Checker struct {"
assert source.count(marker) == 1
source = source.replace(marker, marker + "\n templateIndexRanges map[templateListKey]*templatePrefixRanges")
marker = "func (c *Checker) findApplicableIndexInfo(indexInfos []*IndexInfo, keyType *Type) *IndexInfo {"
assert source.count(marker) == 1
source = source.replace(marker, """
type templateListKey struct {
	first **IndexInfo
	length int
}

type templatePrefixRanges struct {
	width int
	spans map[string][2]int
}

// All keys in an eligible list have at least width bytes of fixed prefix.
// Read the current entries from the original backing array: merging index
// signatures can replace the value for an existing key in place.
func makeTemplatePrefixRanges(infos []*IndexInfo) *templatePrefixRanges {
	width := 32
	for _, info := range infos {
		if info.keyType.flags != TypeFlagsTemplateLiteral {
			return nil
		}
		width = min(width, len(info.keyType.AsTemplateLiteralType().texts[0]))
		if width == 0 {
			return nil
		}
	}
	ranges := &templatePrefixRanges{width: width, spans: make(map[string][2]int)}
	for i, info := range infos {
		key := info.keyType.AsTemplateLiteralType().texts[0][:width]
		span, ok := ranges.spans[key]
		if !ok {
			span[0] = i
		}
		span[1] = i + 1
		ranges.spans[key] = span
	}
	if len(ranges.spans) == 1 {
		return nil
	}
	return ranges
}

func (c *Checker) narrowTemplateIndexRange(infos []*IndexInfo, source *Type) []*IndexInfo {
	var prefix string
	switch {
	case source.flags&TypeFlagsStringLiteral != 0:
		prefix = getStringLiteralValue(source)
	case source.flags&TypeFlagsTemplateLiteral != 0:
		t := source.AsTemplateLiteralType()
		for _, placeholder := range t.types {
			if placeholder.flags&(TypeFlagsString|TypeFlagsNumber|TypeFlagsBigInt) == 0 {
				return infos
			}
		}
		prefix = t.texts[0]
	default:
		return infos
	}
	key := templateListKey{&infos[0], len(infos)}
	ranges, seen := c.templateIndexRanges[key]
	if !seen {
		ranges = makeTemplatePrefixRanges(infos)
		if c.templateIndexRanges == nil {
			c.templateIndexRanges = make(map[templateListKey]*templatePrefixRanges)
		}
		c.templateIndexRanges[key] = ranges
	}
	if ranges == nil {
		return infos
	}
	if len(prefix) < ranges.width {
		return nil
	}
	span := ranges.spans[prefix[:ranges.width]]
	return infos[span[0]:span[1]]
}

""" + marker + """
	if len(indexInfos) >= 32 {
		indexInfos = c.narrowTemplateIndexRange(indexInfos, keyType)
	}""")
out = Path(sys.argv[1]).resolve()
out.mkdir(exist_ok=True, parents=True)
staged = out/path.name
staged.write_text(source)
(out/"overlay.json").write_text(json.dumps({"Replace": {str(root/path): str(staged)}}))
