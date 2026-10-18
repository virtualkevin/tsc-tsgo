package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"runtime"
	"testing"
	"weak"
)

//go:noinline
func makeInstantiationWindowWeakRoots() (*instantiationWindow, weak.Pointer[Type], weak.Pointer[TypeMapper], weak.Pointer[Type], weak.Pointer[ast.Node]) {
	s := &instantiationWindow{slots: make([]windowEntry, 1)}
	input := &Type{id: 1}
	mapper := &TypeMapper{}
	result := &Type{id: 2}
	node := &ast.Node{}
	c := &Checker{currentNode: node}
	token := s.begin(c, input, mapper, nil)
	s.finish(c, token, result)
	return s, weak.Make(input), weak.Make(mapper), weak.Make(result), weak.Make(node)
}
func TestInstantiationWindowWeakRoots(t *testing.T) {
	s, input, mapper, result, node := makeInstantiationWindowWeakRoots()
	for range 4 {
		runtime.GC()
	}
	if input.Value() != nil || mapper.Value() != nil || result.Value() != nil || node.Value() != nil {
		t.Fatal("observer retained semantic objects")
	}
	if s.counts.FinishedFirst != 1 {
		t.Fatal("fixture did not populate record")
	}
	runtime.KeepAlive(s)
}
