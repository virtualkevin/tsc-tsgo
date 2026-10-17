package main

import (
 "debug/dwarf"
 "debug/elf"
 "encoding/json"
 "fmt"
 "os"
 "strings"
)

func main() {
 f, err := elf.Open(os.Args[1]); if err != nil { panic(err) }; defer f.Close()
 d, err := f.DWARF(); if err != nil { panic(err) }
 names := make(map[dwarf.Offset]string)
 r := d.Reader()
 for { e, err := r.Next(); if err != nil { panic(err) }; if e == nil { break }; if e.Tag == dwarf.TagSubprogram { if n,ok := e.Val(dwarf.AttrName).(string); ok { names[e.Offset]=n } } }
 target := func(name string) bool {
  if !strings.Contains(name,"/checker.") {return false}
  for _,suffix := range []string{"(*Type).AsConstrainedType","(*Type).AsStructuredType","(*Type).AsObjectType","(*Type).AsTypeReference","(*Type).AsInterfaceType","(*Type).AsUnionOrIntersectionType","(*Checker).newType","(*Checker).newIntrinsicTypeEx","(*Checker).newObjectType"} {if strings.HasSuffix(name,suffix) {return true}}
  return false
 }
 type Evidence struct {Count int `json:"inlineInstanceCount"`; CallLines []int64 `json:"sampleCallLines"`; Containers []string `json:"sampleContainers"`}
 result := make(map[string]*Evidence)
 for _, name := range names {if target(name) {result[name]=&Evidence{}}}
 r = d.Reader(); var stack []string
 for {e,err:=r.Next();if err!=nil{panic(err)};if e==nil{break};if e.Tag==0 {if len(stack)>0 {stack=stack[:len(stack)-1]};continue}
  container:="";if len(stack)>0 {container=stack[len(stack)-1]}
  if e.Tag==dwarf.TagSubprogram {if name,ok:=e.Val(dwarf.AttrName).(string);ok{container=name}}
  if e.Tag==dwarf.TagInlinedSubroutine {origin,_:=e.Val(dwarf.AttrAbstractOrigin).(dwarf.Offset);name:=names[origin];if item:=result[name];item!=nil {item.Count++;if len(item.CallLines)<8 {line,_:=e.Val(dwarf.AttrCallLine).(int64);item.CallLines=append(item.CallLines,line);item.Containers=append(item.Containers,container)}}}
  if e.Children {stack=append(stack,container)}
 }
 data,err:=json.MarshalIndent(result,"","  ");if err!=nil{panic(err)};fmt.Println(string(data))
}
