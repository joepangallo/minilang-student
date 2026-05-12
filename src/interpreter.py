# src/interpreter.py
# MILESTONE M4 -- the tree-walking interpreter.
#
# Your job: actually execute MiniLang programs by walking the AST.
#
# What you GET for free:
#   - Interpreter class with scope-stack helpers and the _ReturnSignal trick
#     for implementing `return` cleanly
#   - The i32() helper that wraps Python ints to 32-bit signed semantics
#     (matches wasm i32; arithmetic in `eval_expr` should pass through it)
#   - The run() driver
#   - eval_expr cases for Number, Bool, Var
#
# What you HAVE TO WRITE:
#   - exec_stmt: actually execute each statement type
#   - The rest of eval_expr: Unary, Binary (including short-circuit && and ||), Call
#   - call_fn: how a function call is performed (save scopes, bind args, run body, catch return)
#
# Semantics summary:
#   - Arithmetic wraps as 32-bit signed (use the i32() helper).
#   - / is integer division truncated toward zero; division by zero raises RuntimeError.
#   - && and || short-circuit (don't evaluate the right side if not needed).
#   - print emits 1/0 for booleans, the integer for ints.

from src import parser as P


def i32(x):
    """Coerce a Python int to signed 32-bit (wraps on overflow)."""
    x = x & 0xFFFFFFFF
    if x >= 0x80000000:
        x -= 0x100000000
    return x


class _ReturnSignal(Exception):
    """Raised by `return` and caught at the call site to deliver the value."""
    def __init__(self, value): self.value = value


class Interpreter:
    def __init__(self):
        self.scopes = [{}]
        self.fns = {}

    # ----- scope helpers (DONE) -----

    def push_scope(self): self.scopes.append({})
    def pop_scope(self):  self.scopes.pop()

    def declare(self, name, value): self.scopes[-1][name] = value

    def assign(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value; return
        raise RuntimeError(f"unknown variable '{name}'")

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"unknown variable '{name}'")

    # ----- driver (DONE) -----

    def run(self, program):
        for fn in program.functions:
            self.fns[fn.name] = fn
        self.scopes = [{}]
        for stmt in program.main_body:
            self.exec_stmt(stmt)

    # ----- TODO M4: statements -----

    def exec_stmt(self, stmt):
        # Dispatch on isinstance(stmt, ...).
        # Let:    declare(name, eval_expr(expr))
        # Assign: assign(name, eval_expr(expr))
        # Block:  push_scope, exec each stmt, pop_scope (use try/finally)
        # If:     if eval_expr(cond): exec then else exec else (if present)
        # While:  while eval_expr(cond): exec body
        # Return: raise _ReturnSignal(value)
        # Print:  emit 1 / 0 for True / False, else just print the int
        # ExprStmt: just evaluate, discard result
        # For Let, evaluate the initializer first, then declare the variable.
        # For Assign, evaluate the right-hand side first, then update the nearest binding.
        # For Block, push a new scope before running nested statements.
        # Use try/finally for Block so returns still pop the scope.
        # For If, evaluate the condition and run exactly one branch.
        # For While, keep evaluating the condition before each body execution.
        # For Return, evaluate the expression if present, otherwise use None.
        # Raise _ReturnSignal with the return value so call_fn can catch it.
        # For Print, evaluate the expression before formatting booleans as 1 or 0.
        # For ExprStmt, evaluate the expression and discard the result.
        # If no isinstance case matches, raise RuntimeError for the unknown statement node.
        raise NotImplementedError("exec_stmt (M4)")

    # ----- expressions (Number/Bool/Var done; rest TODO) -----

    def eval_expr(self, expr):
        if isinstance(expr, P.Number): return expr.value
        if isinstance(expr, P.Bool):   return expr.value
        if isinstance(expr, P.Var):    return self.lookup(expr.name)

        # TODO M4:
        #   Unary -:  i32(-operand);  !: not operand
        #   Binary:   short-circuit && and || FIRST, then arithmetic / compare.
        #             Wrap arithmetic with i32(). DIV by zero -> RuntimeError.
        #   Call:     return self.call_fn(name, [eval each arg])
        # For Unary, evaluate the operand once.
        # Unary `-` returns i32(-operand).
        # Unary `!` returns `not operand`.
        # For Binary `&&`, evaluate the left side first and return False if it is falsey.
        # For Binary `||`, evaluate the left side first and return True if it is truthy.
        # For other Binary operators, evaluate left and right operands.
        # Arithmetic operators return i32-wrapped results.
        # Division must check for zero and truncate toward zero.
        # Comparison and equality operators return Python booleans.
        # For Call, evaluate arguments left-to-right and pass their values to call_fn.
        # If no isinstance case matches, raise RuntimeError for the unknown expression node.
        raise NotImplementedError(f"eval_expr: {type(expr).__name__} (M4)")

    # ----- TODO M4: call_fn -----

    def call_fn(self, name, arg_values):
        # Save self.scopes, install a fresh [{}] for the callee, declare each
        # parameter, run the body inside a try/except _ReturnSignal, restore
        # scopes, return the captured value (or None if the function fell
        # through without `return`).
        # Look up the function declaration by name in self.fns.
        # Raise RuntimeError if the function name is unknown.
        # Save the caller's current scope stack.
        # Replace self.scopes with a fresh function-local scope stack.
        # Bind each parameter name to the corresponding value from arg_values.
        # Execute each statement in the function body.
        # If _ReturnSignal is raised, capture and return its value.
        # If the body finishes normally, return None.
        # Restore the caller's original scope stack in finally before returning.
        raise NotImplementedError("call_fn (M4)")


def run(program):
    Interpreter().run(program)
