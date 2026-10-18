// Inventory by-value expressions containing StructuredType for manual copy review.
package main
import (
 "encoding/json"
 "fmt"
 "go/ast"
 "go/format"
 "go/token"
 "go/types"
 "bytes"
 "os"
 "path/filepath"
 "strings"
 "golang.org/x/tools/go/packages"
)
func contains(t types.Type, seen map[types.Type]bool) bool {
 if t == nil || seen[t] { return false }; seen[t]=true
 t=types.Unalias(t)
 if n,ok:=t.(*types.Named);ok {
  if n.Obj().Pkg()!=nil && n.Obj().Pkg().Path()=="github.com/microsoft/typescript-go/internal/checker" && n.Obj().Name()=="StructuredType" {return true}
  return contains(n.Underlying(),seen)
 }
 switch x:=t.(type) {
 case *types.Struct: for i:=0;i<x.NumFields();i++ {if contains(x.Field(i).Type(),seen){return true}}
 case *types.Array: return contains(x.Elem(),seen)
 case *types.Tuple: for i:=0;i<x.Len();i++ {if contains(x.At(i).Type(),seen){return true}}
 }
 return false
}
type entry struct { Position, Type, Expression, Parent string }
func main(){
 fs:=token.NewFileSet()
 ps,err:=packages.Load(&packages.Config{Fset:fs,Tests:true,Mode:packages.NeedName|packages.NeedFiles|packages.NeedCompiledGoFiles|packages.NeedSyntax|packages.NeedTypes|packages.NeedTypesInfo|packages.NeedImports|packages.NeedDeps},"./...")
 if err!=nil {panic(err)};if packages.PrintErrors(ps)!=0 {panic("type errors")}
 cwd,_:=os.Getwd();seen:=map[string]bool{};entries:=[]entry{}
 for _,p:=range ps {for _,f:=range p.Syntax {
  path:=fs.Position(f.Pos()).Filename;rel,_:=filepath.Rel(cwd,path)
  if seen[path]||filepath.IsAbs(rel)||strings.HasPrefix(rel,"../"){continue};seen[path]=true
  stack:=[]ast.Node{}
  ast.Inspect(f,func(n ast.Node)bool {
   if n==nil {stack=stack[:len(stack)-1];return false}
   if e,ok:=n.(ast.Expr);ok {
    tv,exists:=p.TypesInfo.Types[e]
    if exists && tv.IsValue() && contains(tv.Type,map[types.Type]bool{}) {
     var b bytes.Buffer;format.Node(&b,fs,e);parent:="";if len(stack)>0 {parent=fmt.Sprintf("%T",stack[len(stack)-1])}
     entries=append(entries,entry{fs.Position(e.Pos()).String(),tv.Type.String(),b.String(),parent})
    }
   }
   stack=append(stack,n);return true
  })
 }}
 enc:=json.NewEncoder(os.Stdout);enc.SetIndent("","  ");enc.Encode(struct{Packages,Files int; Entries []entry}{len(ps),len(seen),entries})
}
