"""Reconstruct the early template index relation lookup against the measured compiler."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
path = Path("packages/tsc-go/internal/checker/checker.go")
source = subprocess.check_output(["git", "show", f"e1eeaab:{path}"], cwd=root, text=True)
marker = "func (c *Checker) isApplicableIndexType(source *Type, target *Type) bool {"
assert source.count(marker) == 1
code = """
    // Distinct template types reach recursiveTypeRelatedTo without normalization.
    // Reuse only its completed ordinary entries, including their reliability bits.
    if source.flags == TypeFlagsTemplateLiteral && target.flags == TypeFlagsTemplateLiteral && source != target {
        id, _ := getRelationKey(source, target, IntersectionStateNone, false, false)
        entry := c.assignableRelation.get(id)
        if entry != RelationComparisonResultNone && entry&RelationComparisonResultOverflow == 0 {
            c.reliabilityFlags |= entry & (RelationComparisonResultReportsUnmeasurable | RelationComparisonResultReportsUnreliable)
            return entry&RelationComparisonResultSucceeded != 0
        }
    }
"""
staged = out / path.name
staged.write_text(source.replace(marker, marker + code))
(out / "overlay.json").write_text(json.dumps({"Replace": {str(root/path): str(staged)}}))
