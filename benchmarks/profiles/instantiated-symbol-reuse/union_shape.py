"""Inspect the repeated Sentry union/array requests without resolving new types."""
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
subprocess.run([sys.executable, here/"classify.py", out], check=True)
p = out / "checker.go"
s = p.read_text().replace("if kind == 1 {", """if _,ok:=key.mapperData().(*ArrayTypeMapper); kind == 1 && ok && key.input.flags&TypeFlagsUnion!=0 {""")
s = s.replace("label := observedClass(key.input, key.mapper)", """t:=key.input
            source:=t
            if origin:=t.AsUnionType().origin; origin!=nil && origin.flags&TypeFlagsUnionOrIntersection!=0 {source=origin}
            var param, concrete, other int
            for _,arm:=range source.Types() {
                switch {
                case arm.flags&TypeFlagsTypeParameter!=0 && arm.alias==nil: param++
                case arm.flags&(TypeFlagsStringLiteral|TypeFlagsNumberLiteral|TypeFlagsBooleanLiteral|TypeFlagsBigIntLiteral|TypeFlagsNull|TypeFlagsUndefined|TypeFlagsString|TypeFlagsNumber|TypeFlagsNever)!=0 && arm.alias==nil: concrete++
                default: other++
                }
            }
            label:=fmt.Sprintf("params=%d constants=%d other=%d origin=%t alias=%t active=%t depth=%d",min(param,16),min(concrete,16),min(other,16),source!=t,t.alias!=nil,c.findActiveMapper(key.mapper)>=0,min(c.instantiationDepth,8))""")
s += """
func (key observedSubstitution) mapperData() TypeMapperData {
    if key.mapper==nil {return nil}
    return key.mapper.data
}
"""
p.write_text(s)
