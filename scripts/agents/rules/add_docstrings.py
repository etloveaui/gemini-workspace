import ast
from .base import RuleBase

class AddDocstringsRule(RuleBase):
    """AST를 순회하며 함수와 클래스에 누락된 docstring을 추가하는 규칙."""
    
    name = "add_docstrings"
    summary = "Adds a TODO docstring to functions and classes that are missing one."
    idempotent = True

    def apply(self, source: str, **kwargs: str) -> str:
        """소스 코드를 파싱하여 docstring이 없는 노드에 추가합니다."""
        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            raise ValueError(f"Cannot parse file due to syntax error: {e}")

        transformer = _DocstringTransformer()
        new_tree = transformer.visit(tree)
        
        if not transformer.is_changed:
            return source # 변경 사항이 없으면 원본 코드 그대로 반환

        return ast.unparse(new_tree)

class _DocstringTransformer(ast.NodeTransformer):
    def __init__(self):
        self.is_changed = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.generic_visit(node)
        if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], "value", None), ast.Str)):
            docstring_node = ast.Expr(value=ast.Str(s='"""TODO: Add docstring."""'))
            node.body.insert(0, docstring_node)
            ast.fix_missing_locations(node)
            self.is_changed = True
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self.generic_visit(node)
        if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(getattr(node.body[0], "value", None), ast.Str)):
            docstring_node = ast.Expr(value=ast.Str(s='"""TODO: Add docstring."""'))
            node.body.insert(0, docstring_node)
            ast.fix_missing_locations(node)
            self.is_changed = True
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        # 비동기 함수도 처리하도록 visit_FunctionDef 로직을 재사용합니다.
        return self.visit_FunctionDef(node)
