# src/typecheck.py
# MILESTONE M3 -- the type checker.
#
# Your job: walk the AST and verify that every operator and assignment sees
# operands of the types it expects. If something is wrong, raise TypeError_
# with a clear message naming the variable / function / operator at fault.
#
# What you GET for free:
#   - TypeError_ exception class
#   - TypeChecker scope-stack helpers (push_scope, pop_scope, declare, lookup)
#   - The check() driver that does the two-pass function check
#   - stmts_always_return / stmt_always_returns helper (M8: catches missing returns)
#   - check_expr cases for Number, Bool, Var (the trivial ones) as examples
#
# What you HAVE TO WRITE:
#   - check_stmt: dispatch on each statement type
#   - The rest of check_expr (Unary, Binary, Call)
#
# Type rules summary:
#   + - * /         int, int  -> int
#   < <= > >=       int, int  -> bool
#   == !=           same-type -> bool
#   && ||           bool, bool -> bool
#   unary -         int  -> int
#   unary !         bool -> bool
#   if/while cond   bool
#   print           int or bool
#   let:T = e       e must have type T
#   call f(args)    each arg type matches signature; result is fn's return type

from src import parser as P


class TypeError_(Exception):
    """Type-check failure. Trailing underscore avoids Python's TypeError."""
    pass


class TypeChecker:
    def __init__(self):
        self.scopes = [{}]
        self.fns = {}                # name -> (param_types, return_type)
        self.current_return = None

    # ----- scope helpers (DONE) -----

    def push_scope(self): self.scopes.append({})
    def pop_scope(self):  self.scopes.pop()
    def declare(self, name, type_): self.scopes[-1][name] = type_
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # ----- driver (DONE) -----

    def check(self, program):
        # Two-pass: first record all signatures so mutual recursion works,
        # then check each function body.
        for fn in program.functions:
            param_types = [t for (_n, t) in fn.params]
            self.fns[fn.name] = (param_types, fn.return_type)
        for fn in program.functions:
            self.check_fn(fn)
        self.scopes = [{}]
        self.current_return = None
        for stmt in program.main_body:
            self.check_stmt(stmt)

    def check_fn(self, fn):
        self.scopes = [{}]
        for (name, type_) in fn.params:
            self.declare(name, type_)
        self.current_return = fn.return_type
        for stmt in fn.body:
            self.check_stmt(stmt)
        if fn.return_type != "void" and not stmts_always_return(fn.body):
            raise TypeError_(
                f"function '{fn.name}' may finish without returning {fn.return_type}"
            )

    # ----- TODO M3: statements -----

    def check_stmt(self, stmt):
        # Dispatch on isinstance(stmt, ...) for each P.<NodeClass>.
        # For each case:
        #   Let:       check_expr(e); type must equal declared; declare(name, type)
        #   Assign:    name must already exist; rhs type must match
        #   Block:     push_scope; check each stmt; pop_scope
        #   If/While:  condition must be "bool"; recurse on body / branches
        #   Return:    if expr is None, current_return must be void; else types must match
        #   Print:     expr type must be int or bool
        #   ExprStmt:  just check_expr
        raise NotImplementedError("check_stmt (M3)")

    # ----- expressions (Number/Bool/Var done; rest TODO) -----

    def check_expr(self, expr):
        if isinstance(expr, P.Number): return "int"
        if isinstance(expr, P.Bool):   return "bool"
        if isinstance(expr, P.Var):
            t = self.lookup(expr.name)
            if t is None:
                raise TypeError_(f"unknown variable '{expr.name}'")
            return t

        # TODO M3: handle Unary, Binary, Call. See "Type rules summary"
        # in the file header. Raise TypeError_ with a useful message on any mismatch.
        raise NotImplementedError(f"check_expr: {type(expr).__name__} (M3)")


# ---------------------------------------------------------------------------
# All-paths-return analysis (DONE) -- used by check_fn above.
# ---------------------------------------------------------------------------

def stmt_always_returns(stmt):
    if isinstance(stmt, P.Return): return True
    if isinstance(stmt, P.Block):  return stmts_always_return(stmt.stmts)
    if isinstance(stmt, P.If):
        if stmt.else_stmt is None: return False
        return (stmt_always_returns(stmt.then_stmt)
                and stmt_always_returns(stmt.else_stmt))
    return False


def stmts_always_return(stmts):
    for s in stmts:
        if stmt_always_returns(s): return True
    return False


def check(program):
    TypeChecker().check(program)
