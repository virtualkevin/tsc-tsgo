package checker

import (
	"github.com/microsoft/typescript-go/internal/ast"
	"testing"
)

func TestArgumentReuseAuditContextInsensitiveLiteral(t *testing.T) {
	c := lazyPropertyTestChecker()
	f := ast.NodeFactory{}
	arg := f.NewStringLiteral("value", ast.TokenFlagsNone)
	if c.isContextSensitive(arg) {
		t.Fatal("fixture unexpectedly context sensitive")
	}
	regular := c.getStringLiteralType("value")
	broad := c.checkExpressionWithContextualType(arg, c.stringType, nil, CheckModeNormal)
	narrow := c.checkExpressionWithContextualType(arg, regular, nil, CheckModeNormal)
	if broad == narrow || !isFreshLiteralType(broad) || isFreshLiteralType(narrow) || narrow != regular {
		t.Fatal("context-insensitive literal failed to distinguish contextual freshness")
	}
	if c.getRegularTypeOfLiteralType(broad) != narrow {
		t.Fatal("fixture changed literal identity")
	}
	// Revisit the broad context: the result is not a permanently regularized node.
	again := c.checkExpressionWithContextualType(arg, c.stringType, nil, CheckModeNormal)
	if again != broad {
		t.Fatal("contextual query history changed the broad result")
	}
}

func TestArgumentReuseAuditIdenticalRequestResetsBudget(t *testing.T) {
	c := lazyPropertyTestChecker()
	f := ast.NodeFactory{}
	arg := f.NewStringLiteral("value", ast.TokenFlagsNone)
	var previous *Type
	for _, budget := range []uint32{17, 4000000} {
		c.instantiationCount = budget
		result := c.checkExpressionWithContextualType(arg, c.stringType, nil, CheckModeNormal)
		if c.instantiationCount != 0 {
			t.Fatal("expression check did not reset statement/expression budget")
		}
		if previous != nil && previous != result {
			t.Fatal("identical request changed returned identity")
		}
		previous = result
	}
	// Returning the previous pointer alone would omit the reset observed above.
}
