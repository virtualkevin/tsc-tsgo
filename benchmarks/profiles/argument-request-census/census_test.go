package checker

import "testing"

func TestArgumentRequestCensus(t *testing.T) {
	p := &argumentRequestCounts{}
	f := p.frame()
	a, b := &Type{}, &Type{}
	k := argumentRequestKey{Context: a}
	f.record(k, a, 2, 0)
	f.record(k, a, 0, 0)
	f.record(k, b, 3, 0)
	for i := 1; i <= 4096; i++ {
		f.record(argumentRequestKey{FlowDepth: i}, a, 0, 0)
	}
	if p.Frames != 1 || p.Requests != 4099 || p.Repeated != 2 || p.SameResult != 1 || p.DifferentResult != 1 || p.BudgetChanged != 2 || p.Untracked != 1 || len(f.seen) != 4096 {
		t.Fatalf("counts: %+v, keys %d", p, len(f.seen))
	}
	g := p.frame()
	g.record(k, a, 0, 0)
	if p.Repeated != 2 {
		t.Fatal("frame leaked keys")
	}
	var disabled *argumentRequestCounts
	if disabled.frame() != nil {
		t.Fatal("disabled frame")
	}
	var nilFrame *argumentRequestFrame
	nilFrame.record(k, a, 0, 0)
}
