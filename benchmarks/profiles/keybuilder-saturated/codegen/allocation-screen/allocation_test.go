package checker

import (
 "fmt"
 "strings"
 "testing"

 "github.com/zeebo/xxh3"
)

var hashSink CacheHashKey
var resultSink uint32

// This is allocation screening of the exact production primitive source, not
// compiler workload timing. Inputs/cache setup are outside AllocsPerRun.
func TestAllocationScreen(t *testing.T) {
 for _,n:=range []int{0,5,13,64,127,128,129,256,1089,4096} {
  data:=strings.Repeat("x",n)
  for _,mode:=range []string{"string","bytes","bytewise"} {
   t.Run(fmt.Sprintf("%s/%d",mode,n),func(t *testing.T){
    bytes:=[]byte(data)
    allocs:=testing.AllocsPerRun(1000,func(){
     var b keyBuilder
     switch mode {
     case "string":b.writeString(data)
     case "bytes":b.writeBytes(bytes)
     case "bytewise":for _,v:=range bytes { b.writeByte(v) }
     }
     hashSink=b.hash()
    })
    t.Logf("allocations_per_call=%g",allocs)
    if n<=128 && allocs!=0 {t.Errorf("short builder allocated: %g",allocs)}
   })
  }
  t.Run(fmt.Sprintf("legacy/%d",n),func(t *testing.T){
   allocs:=testing.AllocsPerRun(1000,func(){var h xxh3.Hasher;_,_=h.WriteString(data);hashSink=CacheHashKey(h.Sum128())})
   t.Logf("allocations_per_call=%g",allocs)
  })
  t.Run(fmt.Sprintf("hash-only/%d",n),func(t *testing.T){
   var b keyBuilder;b.writeString(data)
   allocs:=testing.AllocsPerRun(1000,func(){hashSink=b.hash()})
   t.Logf("allocations_per_call=%g",allocs)
   if allocs!=0 {t.Errorf("hash-only query allocated: %g",allocs)}
  })
 }
 t.Run("indexed-key-map-hit",func(t *testing.T){
  key:=func() CacheHashKey {var b keyBuilder;b.writeUint32(123);b.writeUint32(456);b.writeUint32(3);b.writeByte(0);return b.hash()}
  cache:=map[CacheHashKey]uint32{key():77}
  allocs:=testing.AllocsPerRun(1000,func(){resultSink=cache[key()]})
  t.Logf("allocations_per_call=%g",allocs)
  if allocs!=0||resultSink!=77 {t.Fatalf("cache hit allocations=%g result=%d",allocs,resultSink)}
 })
}
