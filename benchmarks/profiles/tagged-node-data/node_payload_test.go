package ast

import (
	"reflect"
	"runtime"
	"testing"
	"unsafe"
)

func TestNodePayloadAllConcreteTypes(t *testing.T) {
	values := []nodeData{
		&ArrayLiteralExpression{},
		&ArrayTypeNode{},
		&ArrowFunction{},
		&AsExpression{},
		&AwaitExpression{},
		&BigIntLiteral{},
		&BinaryExpression{},
		&BindingElement{},
		&BindingPattern{},
		&Block{},
		&BreakStatement{},
		&CallExpression{},
		&CallSignatureDeclaration{},
		&CaseBlock{},
		&CaseOrDefaultClause{},
		&CatchClause{},
		&ClassDeclaration{},
		&ClassExpression{},
		&ClassStaticBlockDeclaration{},
		&ComputedPropertyName{},
		&ConditionalExpression{},
		&ConditionalTypeNode{},
		&ConstructSignatureDeclaration{},
		&ConstructorDeclaration{},
		&ConstructorTypeNode{},
		&ContinueStatement{},
		&DebuggerStatement{},
		&Decorator{},
		&DeleteExpression{},
		&DoStatement{},
		&ElementAccessExpression{},
		&EmptyStatement{},
		&EnumDeclaration{},
		&EnumMember{},
		&ExportAssignment{},
		&ExportDeclaration{},
		&ExportSpecifier{},
		&ExpressionStatement{},
		&ExpressionWithTypeArguments{},
		&ExternalModuleReference{},
		&FlowReduceLabelData{},
		&FlowSwitchClauseData{},
		&ForInOrOfStatement{},
		&ForStatement{},
		&FunctionDeclaration{},
		&FunctionExpression{},
		&FunctionTypeNode{},
		&GetAccessorDeclaration{},
		&HeritageClause{},
		&Identifier{},
		&IfStatement{},
		&ImportAttribute{},
		&ImportAttributes{},
		&ImportClause{},
		&ImportDeclaration{},
		&ImportEqualsDeclaration{},
		&ImportSpecifier{},
		&ImportTypeNode{},
		&IndexSignatureDeclaration{},
		&IndexedAccessTypeNode{},
		&InferTypeNode{},
		&InterfaceDeclaration{},
		&IntersectionTypeNode{},
		&JSDoc{},
		&JSDocAllType{},
		&JSDocAugmentsTag{},
		&JSDocCallbackTag{},
		&JSDocDeprecatedTag{},
		&JSDocImplementsTag{},
		&JSDocImportTag{},
		&JSDocLink{},
		&JSDocLinkCode{},
		&JSDocLinkPlain{},
		&JSDocNameReference{},
		&JSDocNonNullableType{},
		&JSDocNullableType{},
		&JSDocOptionalType{},
		&JSDocOverloadTag{},
		&JSDocOverrideTag{},
		&JSDocParameterOrPropertyTag{},
		&JSDocPrivateTag{},
		&JSDocProtectedTag{},
		&JSDocPublicTag{},
		&JSDocReadonlyTag{},
		&JSDocReturnTag{},
		&JSDocSatisfiesTag{},
		&JSDocSeeTag{},
		&JSDocSignature{},
		&JSDocTemplateTag{},
		&JSDocText{},
		&JSDocThisTag{},
		&JSDocThrowsTag{},
		&JSDocTypeExpression{},
		&JSDocTypeLiteral{},
		&JSDocTypeTag{},
		&JSDocTypedefTag{},
		&JSDocUnknownTag{},
		&JSDocVariadicType{},
		&JsxAttribute{},
		&JsxAttributes{},
		&JsxClosingElement{},
		&JsxClosingFragment{},
		&JsxElement{},
		&JsxExpression{},
		&JsxFragment{},
		&JsxNamespacedName{},
		&JsxOpeningElement{},
		&JsxOpeningFragment{},
		&JsxSelfClosingElement{},
		&JsxSpreadAttribute{},
		&JsxText{},
		&KeywordExpression{},
		&KeywordTypeNode{},
		&LabeledStatement{},
		&LiteralTypeNode{},
		&MappedTypeNode{},
		&MetaProperty{},
		&MethodDeclaration{},
		&MethodSignatureDeclaration{},
		&MissingDeclaration{},
		&ModuleBlock{},
		&ModuleDeclaration{},
		&NamedExports{},
		&NamedImports{},
		&NamedTupleMember{},
		&NamespaceExport{},
		&NamespaceExportDeclaration{},
		&NamespaceImport{},
		&NewExpression{},
		&NoSubstitutionTemplateLiteral{},
		&NonNullExpression{},
		&NotEmittedStatement{},
		&NotEmittedTypeElement{},
		&NumericLiteral{},
		&ObjectLiteralExpression{},
		&OmittedExpression{},
		&OptionalTypeNode{},
		&ParameterDeclaration{},
		&ParenthesizedExpression{},
		&ParenthesizedTypeNode{},
		&PartiallyEmittedExpression{},
		&PostfixUnaryExpression{},
		&PrefixUnaryExpression{},
		&PrivateIdentifier{},
		&PropertyAccessExpression{},
		&PropertyAssignment{},
		&PropertyDeclaration{},
		&PropertySignatureDeclaration{},
		&QualifiedName{},
		&RegularExpressionLiteral{},
		&RestTypeNode{},
		&ReturnStatement{},
		&SatisfiesExpression{},
		&SemicolonClassElement{},
		&SetAccessorDeclaration{},
		&ShorthandPropertyAssignment{},
		&SourceFile{},
		&SpreadAssignment{},
		&SpreadElement{},
		&StringLiteral{},
		&SwitchStatement{},
		&SyntaxList{},
		&SyntheticExpression{},
		&SyntheticReferenceExpression{},
		&TaggedTemplateExpression{},
		&TemplateExpression{},
		&TemplateHead{},
		&TemplateLiteralTypeNode{},
		&TemplateLiteralTypeSpan{},
		&TemplateMiddle{},
		&TemplateSpan{},
		&TemplateTail{},
		&ThisTypeNode{},
		&ThrowStatement{},
		&Token{},
		&TryStatement{},
		&TupleTypeNode{},
		&TypeAliasDeclaration{},
		&TypeAssertion{},
		&TypeLiteralNode{},
		&TypeOfExpression{},
		&TypeOperatorNode{},
		&TypeParameterDeclaration{},
		&TypePredicateNode{},
		&TypeQueryNode{},
		&TypeReferenceNode{},
		&UnionTypeNode{},
		&VariableDeclaration{},
		&VariableDeclarationList{},
		&VariableStatement{},
		&VoidExpression{},
		&WhileStatement{},
		&WithStatement{},
		&YieldExpression{},
	}
	for _, value := range values {
		n := newNode(KindUnknown, value, NodeFactoryHooks{})
		if n.nodeDataValue() != value || n.nodeDataValue().AsNode() != n {
			t.Fatalf("identity %T", value)
		}
		// Concrete type identity must survive semantic Kind changes.
		n.Kind = KindIdentifier
		if reflect.TypeOf(n.nodeDataValue()) != reflect.TypeOf(value) {
			t.Fatalf("kind retag %T", value)
		}
	}
}
func TestNodePayloadCopiedHeaderLifetime(t *testing.T) {
	makeCopy := func() *Node {
		f := &NodeFactory{}
		original := f.NewIdentifier("kept through copied header")
		// A separate Node header must refer to the original concrete allocation.
		return &Node{Kind: original.Kind, Flags: original.Flags, Loc: original.Loc, dataTag: original.dataTag, dataPointer: original.dataPointer}
	}
	copied := makeCopy()
	for i := 0; i < 3; i++ {
		runtime.GC()
	}
	if copied.AsIdentifier().Text != "kept through copied header" || copied.AsIdentifier().AsNode() == copied {
		t.Fatal("copied header lost original payload")
	}
	runtime.KeepAlive(copied)
}
func TestNodePayloadCheckedAssertions(t *testing.T) {
	f := &NodeFactory{}
	n := f.NewIdentifier("x")
	n.Kind = KindSourceFile
	if n.AsIdentifier().Text != "x" {
		t.Fatal("kind affected payload")
	}
	assertPanic := func(fn func()) {
		t.Helper()
		defer func() {
			if _, ok := recover().(*runtime.TypeAssertionError); !ok {
				t.Error("expected type assertion panic")
			}
		}()
		fn()
	}
	assertPanic(func() { n.AsSourceFile() })
	assertPanic(func() { (&Node{}).AsIdentifier() })
	nilPayload := &Node{}
	nilPayload.setNodeData((*Identifier)(nil))
	if nilPayload.AsIdentifier() != nil || reflect.TypeOf(nilPayload.nodeDataValue()) != reflect.TypeOf((*Identifier)(nil)) {
		t.Fatal("typed nil")
	}
}
func TestNodePayloadLayout(t *testing.T) {
	if unsafe.Sizeof(uintptr(0)) != 8 {
		t.Skip("amd64 layout audit")
	}
	if unsafe.Sizeof(Node{}) != 40 || unsafe.Sizeof(Identifier{}) != 64 {
		t.Fatal("unexpected layout", unsafe.Sizeof(Node{}), unsafe.Sizeof(Identifier{}))
	}
	if unsafe.Offsetof(Node{}.dataTag) != 2 {
		t.Fatal("tag not in prior padding")
	}
}
