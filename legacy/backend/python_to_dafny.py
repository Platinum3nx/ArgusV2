"""
Python to Dafny Translator

Translates Python code with loops to Dafny for verification.
Dafny is better suited for loops because it has built-in loop invariant support.
"""

import ast
import re
from typing import Optional, List, Tuple, Set


class PythonToDafnyTranslator(ast.NodeVisitor):
    """
    AST-based translator from Python to Dafny.
    
    Handles:
    - Functions → Methods with pre/post conditions
    - For loops → While loops with invariants
    - Lists → Sequences or arrays
    - Basic arithmetic and comparisons
    """
    
    def __init__(self):
        self.indent_level = 0
        self.methods = []
        self.current_method_params = []
        self.declared_vars: Set[str] = set()  # Track declared variables
        self.requires_nonneg_result = False  # Track if function ensures result >= 0
    
    def translate(self, python_code: str) -> str:
        """Translate Python code to Dafny."""
        try:
            tree = ast.parse(python_code)
            
            # Collect all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Reset declared vars for each function
                    self.declared_vars = set()
                    method_code = self.translate_function(node)
                    if method_code:
                        self.methods.append(method_code)
            
            return "\n\n".join(self.methods)
            
        except SyntaxError as e:
            return f"// PARSE_ERROR: {e}"
    
    def translate_function(self, node: ast.FunctionDef) -> str:
        """Translate a Python function to a Dafny method."""
        func_name = self._capitalize_first(node.name)
        
        # Get parameters
        params = []
        self.current_method_params = []
        for arg in node.args.args:
            param_name = arg.arg
            param_type = self._infer_type(arg)
            params.append(f"{param_name}: {param_type}")
            self.current_method_params.append((param_name, param_type))
        
        params_str = ", ".join(params)
        
        # Get return type
        return_type = self._get_return_type(node)
        
        # Extract specifications from docstring
        specs = self._extract_specs(node)
        
        # Determine if this function ensures result >= 0
        # This controls whether we add accumulator invariants
        ensures_list = specs.get("ensures", [])
        self.requires_nonneg_result = any("result >= 0" in e or "result>=0" in e for e in ensures_list)
        # Also true if no ensures specified (we add default result >= 0)
        if not ensures_list:
            self.requires_nonneg_result = True
        
        # Build method signature
        lines = [f"method {func_name}({params_str}) returns (result: {return_type})"]
        
        # Add specifications
        for spec in specs.get("requires", []):
            lines.append(f"  requires {spec}")
        for spec in specs.get("ensures", []):
            lines.append(f"  ensures {spec}")
        
        # Add default non-negative specifications for balance-like parameters
        if not specs.get("requires"):
            for param_name, param_type in self.current_method_params:
                if param_type == "int" and any(kw in param_name.lower() for kw in ["balance", "amount", "total"]):
                    lines.append(f"  requires {param_name} >= 0")
        
        if not specs.get("ensures"):
            lines.append("  ensures result >= 0")
        
        # Translate body
        lines.append("{")
        body_code = self._translate_body(node.body, indent=1)
        lines.append(body_code)
        lines.append("}")
        
        return "\n".join(lines)
    
    def _translate_body(self, body: List[ast.stmt], indent: int = 0) -> str:
        """Translate a list of statements to Dafny."""
        prefix = "  " * indent
        result_lines = []
        
        for stmt in body:
            translated = self._translate_stmt(stmt, indent)
            if translated:
                result_lines.append(translated)
        
        return "\n".join(result_lines)
    
    def _translate_stmt(self, stmt: ast.stmt, indent: int) -> str:
        """Translate a single statement to Dafny."""
        prefix = "  " * indent
        
        # Skip docstrings
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
            if isinstance(stmt.value.value, str):
                return ""  # Skip docstring
        
        # Return statement
        if isinstance(stmt, ast.Return):
            if stmt.value:
                expr = self._translate_expr(stmt.value)
                # CRITICAL: Add return; after result assignment to stop execution
                # Without this, subsequent statements would overwrite result
                return f"{prefix}result := {expr};\n{prefix}return;"
            return f"{prefix}return;"
        
        # Assignment
        if isinstance(stmt, ast.Assign):
            target = stmt.targets[0]
            if isinstance(target, ast.Name):
                value = self._translate_expr(stmt.value)
                var_name = target.id
                # Check if this is first assignment (needs var declaration)
                if var_name in self.declared_vars:
                    # Variable already declared, just reassign
                    return f"{prefix}{var_name} := {value};"
                else:
                    # First time seeing this variable, declare it
                    self.declared_vars.add(var_name)
                    return f"{prefix}var {var_name} := {value};"
        
        # Augmented assignment (+=, -=, etc.)
        if isinstance(stmt, ast.AugAssign):
            target = self._translate_expr(stmt.target)
            value = self._translate_expr(stmt.value)
            op = self._translate_aug_op(stmt.op)
            return f"{prefix}{target} := {target} {op} {value};"
        
        # If statement
        if isinstance(stmt, ast.If):
            return self._translate_if(stmt, indent)
        
        # For loop
        if isinstance(stmt, ast.For):
            return self._translate_for(stmt, indent)
        
        # While loop
        if isinstance(stmt, ast.While):
            return self._translate_while(stmt, indent)
        
        # Expression statement
        if isinstance(stmt, ast.Expr):
            return f"{prefix}{self._translate_expr(stmt.value)};"
        
        return f"{prefix}// Unsupported: {type(stmt).__name__}"
    
    def _translate_if(self, node: ast.If, indent: int) -> str:
        """Translate if statement to Dafny."""
        prefix = "  " * indent
        cond = self._translate_expr(node.test)
        
        lines = [f"{prefix}if ({cond}) {{"]
        lines.append(self._translate_body(node.body, indent + 1))
        
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                # elif
                lines.append(f"{prefix}}} else {self._translate_if(node.orelse[0], indent).lstrip()}")
                return "\n".join(lines)
            else:
                lines.append(f"{prefix}}} else {{")
                lines.append(self._translate_body(node.orelse, indent + 1))
        
        lines.append(f"{prefix}}}")
        return "\n".join(lines)
    
    def _translate_for(self, node: ast.For, indent: int) -> str:
        """
        Translate Python for loop to Dafny while loop.
        
        Python: for x in range(n):
        Dafny: var x := 0; while (x < n) invariant ... { ... x := x + 1; }
        
        Python: for x in items:
        Dafny: var i := 0; while (i < |items|) invariant ... { var x := items[i]; ... }
        """
        prefix = "  " * indent
        
        # Handle range() pattern
        if isinstance(node.iter, ast.Call) and isinstance(node.iter.func, ast.Name):
            if node.iter.func.id == "range":
                return self._translate_range_for(node, indent)
        
        # Handle iteration over sequence
        return self._translate_seq_for(node, indent)
    
    def _translate_range_for(self, node: ast.For, indent: int) -> str:
        """Translate for x in range(n) to Dafny while loop."""
        prefix = "  " * indent
        var_name = node.target.id if isinstance(node.target, ast.Name) else "i"
        
        # Parse range arguments
        args = node.iter.args
        if len(args) == 1:
            start = "0"
            end = self._translate_expr(args[0])
            step = "1"
        elif len(args) == 2:
            start = self._translate_expr(args[0])
            end = self._translate_expr(args[1])
            step = "1"
        else:
            start = self._translate_expr(args[0])
            end = self._translate_expr(args[1])
            step = self._translate_expr(args[2])
        
        lines = [
            f"{prefix}var {var_name} := {start};",
            f"{prefix}while ({var_name} < {end})",
            f"{prefix}  invariant {start} <= {var_name} <= {end}",
            f"{prefix}  decreases {end} - {var_name}",
        ]
        
        # Detect and add accumulator invariants (only if function ensures result >= 0)
        if self.requires_nonneg_result:
            accumulators = self._find_accumulator_vars(node.body)
            for acc_var in accumulators:
                lines.append(f"{prefix}  invariant {acc_var} >= 0")
        
        lines.append(f"{prefix}{{")
        
        # Translate loop body
        lines.append(self._translate_body(node.body, indent + 1))
        
        # Increment
        lines.append(f"{prefix}  {var_name} := {var_name} + {step};")
        lines.append(f"{prefix}}}")
        
        return "\n".join(lines)
    
    def _translate_seq_for(self, node: ast.For, indent: int) -> str:
        """Translate for x in sequence to Dafny while loop."""
        prefix = "  " * indent
        item_var = node.target.id if isinstance(node.target, ast.Name) else "item"
        seq_name = self._translate_expr(node.iter)
        idx_var = f"idx_{item_var}"
        
        # Detect accumulator variables that should have invariants
        # These are variables that start at 0 and are only increased
        accumulators = self._find_accumulator_vars(node.body)
        
        lines = [
            f"{prefix}var {idx_var} := 0;",
            f"{prefix}while ({idx_var} < |{seq_name}|)",
            f"{prefix}  invariant 0 <= {idx_var} <= |{seq_name}|",
        ]
        
        # Add invariants for accumulator variables (only if function ensures result >= 0)
        if self.requires_nonneg_result:
            for acc_var in accumulators:
                lines.append(f"{prefix}  invariant {acc_var} >= 0")
        
        lines.append(f"{prefix}  decreases |{seq_name}| - {idx_var}")
        lines.append(f"{prefix}{{")
        lines.append(f"{prefix}  var {item_var} := {seq_name}[{idx_var}];")
        
        # Translate loop body
        lines.append(self._translate_body(node.body, indent + 1))
        
        # Increment
        lines.append(f"{prefix}  {idx_var} := {idx_var} + 1;")
        lines.append(f"{prefix}}}")
        
        return "\n".join(lines)
    
    def _find_accumulator_vars(self, body: List[ast.stmt]) -> List[str]:
        """
        Find accumulator variables in loop body.
        
        An accumulator is a variable that:
        - Is assigned to with += or = var + expr
        - The increment is guarded by a condition (if x > 0)
        """
        accumulators = []
        
        for stmt in body:
            if isinstance(stmt, ast.AugAssign):
                # x += value pattern
                if isinstance(stmt.target, ast.Name):
                    if isinstance(stmt.op, ast.Add):
                        accumulators.append(stmt.target.id)
            elif isinstance(stmt, ast.If):
                # Check inside if body for accumulator patterns
                for inner in stmt.body:
                    if isinstance(inner, ast.Assign):
                        target = inner.targets[0]
                        if isinstance(target, ast.Name):
                            # Check if right side is var + something
                            if isinstance(inner.value, ast.BinOp):
                                if isinstance(inner.value.left, ast.Name):
                                    if inner.value.left.id == target.id:
                                        accumulators.append(target.id)
                    elif isinstance(inner, ast.AugAssign):
                        if isinstance(inner.target, ast.Name):
                            if isinstance(inner.op, ast.Add):
                                accumulators.append(inner.target.id)
        
        return list(set(accumulators))  # Remove duplicates
    
    def _translate_while(self, node: ast.While, indent: int) -> str:
        """Translate Python while loop to Dafny."""
        prefix = "  " * indent
        cond = self._translate_expr(node.test)
        
        lines = [
            f"{prefix}while ({cond})",
            f"{prefix}  // TODO: Add invariant and decreases clause",
            f"{prefix}{{",
        ]
        
        lines.append(self._translate_body(node.body, indent + 1))
        lines.append(f"{prefix}}}")
        
        return "\n".join(lines)
    
    def _translate_expr(self, node: ast.expr) -> str:
        """Translate a Python expression to Dafny."""
        if node is None:
            return "null"
        
        if isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                return "true" if node.value else "false"
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        
        if isinstance(node, ast.Name):
            # Map some common names
            name = node.id
            if name == "True":
                return "true"
            if name == "False":
                return "false"
            if name == "None":
                return "null"
            return name
        
        if isinstance(node, ast.BinOp):
            left = self._translate_expr(node.left)
            right = self._translate_expr(node.right)
            op = self._translate_binop(node.op)
            return f"({left} {op} {right})"
        
        if isinstance(node, ast.UnaryOp):
            operand = self._translate_expr(node.operand)
            if isinstance(node.op, ast.Not):
                return f"!({operand})"
            if isinstance(node.op, ast.USub):
                return f"-({operand})"
            return operand
        
        if isinstance(node, ast.Compare):
            left = self._translate_expr(node.left)
            parts = [left]
            for op, comparator in zip(node.ops, node.comparators):
                dafny_op = self._translate_cmpop(op)
                right = self._translate_expr(comparator)
                parts.append(f"{dafny_op} {right}")
            return " ".join(parts)
        
        if isinstance(node, ast.BoolOp):
            op = " && " if isinstance(node.op, ast.And) else " || "
            values = [self._translate_expr(v) for v in node.values]
            return f"({op.join(values)})"
        
        if isinstance(node, ast.IfExp):
            # Ternary: a if cond else b → if cond then a else b
            cond = self._translate_expr(node.test)
            then_val = self._translate_expr(node.body)
            else_val = self._translate_expr(node.orelse)
            return f"(if {cond} then {then_val} else {else_val})"
        
        if isinstance(node, ast.Call):
            func_name = self._translate_expr(node.func)
            args = [self._translate_expr(a) for a in node.args]
            
            # Handle some built-in functions
            if func_name == "len":
                return f"|{args[0]}|"
            if func_name == "abs":
                arg = args[0]
                return f"(if {arg} >= 0 then {arg} else -{arg})"
            if func_name == "max":
                if len(args) == 2:
                    return f"(if {args[0]} >= {args[1]} then {args[0]} else {args[1]})"
            if func_name == "min":
                if len(args) == 2:
                    return f"(if {args[0]} <= {args[1]} then {args[0]} else {args[1]})"
            
            return f"{self._capitalize_first(func_name)}({', '.join(args)})"
        
        if isinstance(node, ast.Subscript):
            value = self._translate_expr(node.value)
            slice_val = self._translate_expr(node.slice)
            return f"{value}[{slice_val}]"
        
        if isinstance(node, ast.List):
            elements = [self._translate_expr(e) for e in node.elts]
            return f"[{', '.join(elements)}]"
        
        if isinstance(node, ast.Attribute):
            value = self._translate_expr(node.value)
            return f"{value}.{node.attr}"
        
        return f"/* unsupported: {type(node).__name__} */"
    
    def _translate_binop(self, op: ast.operator) -> str:
        """Translate binary operator."""
        ops = {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
            ast.FloorDiv: "/",
            ast.Mod: "%",
        }
        return ops.get(type(op), "?")
    
    def _translate_cmpop(self, op: ast.cmpop) -> str:
        """Translate comparison operator."""
        ops = {
            ast.Eq: "==",
            ast.NotEq: "!=",
            ast.Lt: "<",
            ast.LtE: "<=",
            ast.Gt: ">",
            ast.GtE: ">=",
            ast.In: "in",
            ast.NotIn: "!in",
        }
        return ops.get(type(op), "?")
    
    def _translate_aug_op(self, op: ast.operator) -> str:
        """Translate augmented assignment operator."""
        return self._translate_binop(op)
    
    def _infer_type(self, arg: ast.arg) -> str:
        """Infer Dafny type from Python type annotation."""
        if arg.annotation is None:
            return "int"
        
        annotation = arg.annotation
        
        if isinstance(annotation, ast.Name):
            type_map = {
                "int": "int",
                "float": "real",
                "bool": "bool",
                "str": "string",
                "list": "seq<int>",
                "List": "seq<int>",
            }
            return type_map.get(annotation.id, "int")
        
        if isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                container = annotation.value.id
                if container in ("list", "List"):
                    # Get element type
                    if isinstance(annotation.slice, ast.Name):
                        elem_map = {"int": "int", "float": "real", "str": "string", "bool": "bool"}
                        elem_type = elem_map.get(annotation.slice.id, "int")
                        return f"seq<{elem_type}>"
                    return "seq<int>"
        
        return "int"
    
    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Get return type from function annotation."""
        if node.returns is None:
            return "int"
        
        if isinstance(node.returns, ast.Name):
            type_map = {
                "int": "int",
                "float": "real",
                "bool": "bool",
                "str": "string",
                "None": "()",
            }
            return type_map.get(node.returns.id, "int")
        
        if isinstance(node.returns, ast.Constant):
            if node.returns.value is None:
                return "()"
        
        return "int"
    
    def _extract_specs(self, node: ast.FunctionDef) -> dict:
        """Extract specifications from docstring."""
        specs = {"requires": [], "ensures": []}
        
        if not node.body:
            return specs
        
        # Check for docstring
        first_stmt = node.body[0]
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant):
            if isinstance(first_stmt.value.value, str):
                docstring = first_stmt.value.value
                
                # Look for @requires and @ensures annotations
                for line in docstring.split("\n"):
                    line = line.strip()
                    if line.startswith("@requires"):
                        spec = line.replace("@requires", "").strip().strip(":")
                        if spec:
                            specs["requires"].append(self._normalize_spec(spec))
                    elif line.startswith("@ensures"):
                        spec = line.replace("@ensures", "").strip().strip(":")
                        if spec:
                            specs["ensures"].append(self._normalize_spec(spec))
                    elif line.startswith("Requires:"):
                        spec = line.replace("Requires:", "").strip()
                        if spec:
                            specs["requires"].append(self._normalize_spec(spec))
                    elif line.startswith("Ensures:"):
                        spec = line.replace("Ensures:", "").strip()
                        if spec:
                            specs["ensures"].append(self._normalize_spec(spec))
        
        return specs
    
    def _normalize_spec(self, spec: str) -> str:
        """Normalize a spec string for Dafny compatibility."""
        # Convert Python boolean literals to Dafny
        spec = spec.replace("True", "true").replace("False", "false")
        return spec.strip()
    
    def _capitalize_first(self, name: str) -> str:
        """Capitalize first letter (Dafny convention for methods)."""
        if not name:
            return name
        return name[0].upper() + name[1:]


def translate_to_dafny(python_code: str) -> str:
    """
    Convenience function to translate Python code to Dafny.
    
    Args:
        python_code: Python source code string
        
    Returns:
        Dafny code string
    """
    translator = PythonToDafnyTranslator()
    return translator.translate(python_code)


# Test
if __name__ == "__main__":
    test_code = '''
def sum_positive(items: List[int]) -> int:
    """
    Sum all positive numbers in the list.
    
    @requires: all items >= 0
    @ensures: result >= 0
    """
    total = 0
    for x in items:
        if x > 0:
            total = total + x
    return total


def deposit(balance: int, amount: int) -> int:
    """Add amount to balance."""
    if amount <= 0:
        return balance
    return balance + amount
'''
    
    result = translate_to_dafny(test_code)
    print(result)
