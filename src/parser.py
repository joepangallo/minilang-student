# src/parser.py
# MILESTONE M2 -- the parser.
#
# Your job: turn a list of Tokens into an Abstract Syntax Tree (a tree of
# the AST node classes defined below). We use recursive descent -- one
# method per grammar rule.
#
# What you GET for free:
#   - All AST node classes (Number, Binary, If, FnDecl, etc.)
#   - Token helpers (peek, advance, check, match, expect)
#   - Error recovery (synchronize) and the top-level parse() loop
#   - parse_let() as a worked example of a statement parser
#   - parse_or() as a worked example of an expression parser
#   - print_ast() so the `ast` command works once parse() does
#
# What you HAVE TO WRITE:
#   - parse_stmt and the statement methods (parse_if, parse_while, parse_return,
#     parse_print, parse_assign_or_expr)
#   - parse_fn and parse_param
#   - The expression chain (parse_and, parse_equality, parse_comparison,
#     parse_term, parse_factor, parse_unary, parse_call, parse_primary)
#
# The grammar (full BNF, copied here for convenience). One method per rule:
#
#     program     = (fnDecl | stmt)*
#     fnDecl      = 'fun' IDENT '(' params? ')' ':' type block
#     params      = param (',' param)*
#     param       = IDENT ':' type
#     type        = IDENT                   # "int" or "bool"
#     block       = '{' stmt* '}'
#     stmt        = block
#                 | 'let' IDENT ':' type '=' expr ';'
#                 | 'if' '(' expr ')' stmt ('else' stmt)?
#                 | 'while' '(' expr ')' stmt
#                 | 'return' expr? ';'
#                 | 'print' '(' expr ')' ';'
#                 | IDENT '=' expr ';'      # assignment
#                 | expr ';'                # expression statement
#
#     expr        = logicOr
#     logicOr     = logicAnd ('||' logicAnd)*
#     logicAnd    = equality ('&&' equality)*
#     equality    = compare (('==' | '!=') compare)*
#     compare     = term (('<' | '<=' | '>' | '>=') term)*
#     term        = factor (('+' | '-') factor)*
#     factor      = unary (('*' | '/') unary)*
#     unary       = ('-' | '!')? call
#     call        = primary ('(' args? ')')?
#     args        = expr (',' expr)*
#     primary     = NUMBER | 'true' | 'false' | IDENT | '(' expr ')'

from src import lexer as L


# ---------------------------------------------------------------------------
# AST node classes -- ALL DEFINED FOR YOU. Just construct them in your methods.
# ---------------------------------------------------------------------------

class Number:
    def __init__(self, value): self.value = value
class Bool:
    def __init__(self, value): self.value = value
class Var:
    def __init__(self, name): self.name = name
class Binary:
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
class Unary:
    def __init__(self, op, operand):
        self.op, self.operand = op, operand
class Call:
    def __init__(self, name, args):
        self.name, self.args = name, args

class Let:
    def __init__(self, name, type_, expr):
        self.name, self.type, self.expr = name, type_, expr
class Assign:
    def __init__(self, name, expr):
        self.name, self.expr = name, expr
class Block:
    def __init__(self, stmts):
        self.stmts = stmts
class If:
    def __init__(self, cond, then_stmt, else_stmt):
        self.cond, self.then_stmt, self.else_stmt = cond, then_stmt, else_stmt
class While:
    def __init__(self, cond, body):
        self.cond, self.body = cond, body
class Return:
    def __init__(self, expr): self.expr = expr
class Print:
    def __init__(self, expr): self.expr = expr
class ExprStmt:
    def __init__(self, expr): self.expr = expr

class FnDecl:
    def __init__(self, name, params, return_type, body):
        self.name, self.params, self.return_type, self.body = name, params, return_type, body
class Program:
    def __init__(self, functions, main_body):
        self.functions, self.main_body = functions, main_body


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    # ----- token helpers (DONE) -----

    def peek(self): return self.tokens[self.pos]
    def peek_kind(self, offset=0):
        i = self.pos + offset
        return self.tokens[i].kind if i < len(self.tokens) else L.EOF
    def advance(self):
        tok = self.tokens[self.pos]; self.pos += 1; return tok
    def check(self, kind): return self.peek().kind == kind
    def match(self, *kinds):
        if self.peek().kind in kinds:
            self.advance(); return True
        return False
    def expect(self, kind):
        if self.peek().kind != kind:
            tok = self.peek()
            raise SyntaxError(
                f"line {tok.line}: expected {kind}, got {tok.kind} ({tok.text!r})"
            )
        return self.advance()

    # ----- top-level + error recovery (DONE) -----

    def parse(self):
        functions, main_body = [], []
        while not self.check(L.EOF):
            try:
                if self.check(L.FUN):
                    functions.append(self.parse_fn())
                else:
                    main_body.append(self.parse_stmt())
            except SyntaxError as e:
                self.errors.append(str(e))
                self.synchronize()
        if self.errors:
            raise SyntaxError("\n  " + "\n  ".join(self.errors))
        return Program(functions, main_body)

    def synchronize(self):
        starters = (L.LET, L.IF, L.WHILE, L.FUN, L.RETURN, L.PRINT, L.LBRACE)
        while not self.check(L.EOF):
            if self.peek().kind == L.SEMI: self.advance(); return
            if self.peek().kind in starters: return
            if self.peek().kind == L.RBRACE: self.advance(); return
            self.advance()

    # ----- block helper (DONE) -----

    def parse_braced_stmts(self):
        """Parse `{ stmt* }` -- returns a flat list of statements."""
        self.expect(L.LBRACE)
        stmts = []
        while not self.check(L.RBRACE) and not self.check(L.EOF):
            stmts.append(self.parse_stmt())
        self.expect(L.RBRACE)
        return stmts

    # =======================================================================
    # WORKED EXAMPLE -- read these before writing your own.
    # =======================================================================

    # stmt = 'let' IDENT ':' type '=' expr ';'
    def parse_let(self):
        self.expect(L.LET)
        name = self.expect(L.IDENT).text
        self.expect(L.COLON)
        type_ = self.expect(L.IDENT).text
        self.expect(L.EQ)
        expr = self.parse_expr()
        self.expect(L.SEMI)
        return Let(name, type_, expr)

    # logicOr = logicAnd ('||' logicAnd)*
    def parse_or(self):
        left = self.parse_and()
        while self.check(L.OR):
            self.advance()
            right = self.parse_and()
            left = Binary("||", left, right)
        return left

    # =======================================================================
    # YOUR WORK -- M2.
    # =======================================================================

    # stmt = block | let | if | while | return | print | assignOrExpr
    def parse_stmt(self):
        # Hint: peek at self.peek().kind and dispatch. LBRACE -> Block(parse_braced_stmts()).
        # If the next token is `{`, parse the braced statements and wrap them in Block.
        # If the next token is `let`, call the completed parse_let helper.
        # If the next token is `if`, call parse_if.
        # If the next token is `while`, call parse_while.
        # If the next token is `return`, call parse_return.
        # If the next token is `print`, call parse_print.
        # Otherwise parse either an assignment statement or an expression statement.
        raise NotImplementedError("parse_stmt (M2)")

    # stmt = 'if' '(' expr ')' stmt ('else' stmt)?
    def parse_if(self):
        # Consume `if`.
        # Consume `(`.
        # Parse the condition expression.
        # Consume `)`.
        # Parse the then statement.
        # If `else` is present, parse the else statement; otherwise use None.
        # Return an If node with the condition, then branch, and optional else branch.
        raise NotImplementedError("parse_if (M2)")

    # stmt = 'while' '(' expr ')' stmt
    def parse_while(self):
        # Consume `while`.
        # Consume `(`.
        # Parse the loop condition expression.
        # Consume `)`.
        # Parse the loop body statement.
        # Return a While node with the condition and body.
        raise NotImplementedError("parse_while (M2)")

    # stmt = 'return' expr? ';'
    def parse_return(self):
        # Consume `return`.
        # If the next token is `;`, this is a bare return with expr = None.
        # Otherwise parse the return expression.
        # Consume the trailing `;`.
        # Return a Return node containing the expression or None.
        raise NotImplementedError("parse_return (M2)")

    # stmt = 'print' '(' expr ')' ';'
    def parse_print(self):
        # Consume `print`.
        # Consume `(`.
        # Parse the expression to print.
        # Consume `)`.
        # Consume the trailing `;`.
        # Return a Print node containing the expression.
        raise NotImplementedError("parse_print (M2)")

    # stmt = IDENT '=' expr ';'  |  expr ';'
    # Hint: peek two tokens ahead. If they are IDENT then EQ, it's an assignment.
    def parse_assign_or_expr(self):
        # If the next token is IDENT and the following token is `=`, parse assignment.
        # For assignment, consume the name, consume `=`, parse the expression, then consume `;`.
        # Return an Assign node for the assignment case.
        # Otherwise parse a normal expression.
        # Consume the trailing `;`.
        # Return an ExprStmt node for the expression-statement case.
        raise NotImplementedError("parse_assign_or_expr (M2)")

    # fnDecl = 'fun' IDENT '(' params? ')' ':' type block
    def parse_fn(self):
        # Consume `fun`.
        # Consume the function name identifier.
        # Consume `(`.
        # Parse zero or more comma-separated params until `)`.
        # Consume `)`.
        # Consume `:`.
        # Consume the return type identifier.
        # Parse the braced function body.
        # Return an FnDecl node with name, params, return type, and body.
        raise NotImplementedError("parse_fn (M2)")

    # param = IDENT ':' type
    def parse_param(self):
        # Consume the parameter name identifier.
        # Consume `:`.
        # Consume the parameter type identifier.
        # Return the `(name, type)` pair expected by FnDecl.
        raise NotImplementedError("parse_param (M2)")

    # ----- expressions (one method per precedence level) -----

    def parse_expr(self):
        return self.parse_or()

    # logicAnd = equality ('&&' equality)*
    def parse_and(self):
        # Parse the left operand with the next tighter precedence method.
        # While the next token is `&&`, consume it and parse the right operand.
        # Wrap each pair in a Binary("&&", left, right) node.
        # Return the final left-associated expression tree.
        raise NotImplementedError("parse_and (M2)")

    # equality = compare (('==' | '!=') compare)*
    def parse_equality(self):
        # Parse the left operand with parse_comparison.
        # While the next token is `==` or `!=`, save the operator text.
        # Consume the operator and parse the right operand with parse_comparison.
        # Wrap the pieces in a Binary(op, left, right) node.
        # Return the final left-associated expression tree.
        raise NotImplementedError("parse_equality (M2)")

    # compare = term (('<' | '<=' | '>' | '>=') term)*
    def parse_comparison(self):
        # Parse the left operand with parse_term.
        # While the next token is `<`, `<=`, `>`, or `>=`, save the operator text.
        # Consume the operator and parse the right operand with parse_term.
        # Wrap the pieces in a Binary(op, left, right) node.
        # Return the final left-associated expression tree.
        raise NotImplementedError("parse_comparison (M2)")

    # term = factor (('+' | '-') factor)*
    def parse_term(self):
        # Parse the left operand with parse_factor.
        # While the next token is `+` or `-`, save the operator text.
        # Consume the operator and parse the right operand with parse_factor.
        # Wrap the pieces in a Binary(op, left, right) node.
        # Return the final left-associated expression tree.
        raise NotImplementedError("parse_term (M2)")

    # factor = unary (('*' | '/') unary)*
    def parse_factor(self):
        # Parse the left operand with parse_unary.
        # While the next token is `*` or `/`, save the operator text.
        # Consume the operator and parse the right operand with parse_unary.
        # Wrap the pieces in a Binary(op, left, right) node.
        # Return the final left-associated expression tree.
        raise NotImplementedError("parse_factor (M2)")

    # unary = ('-' | '!')? call
    def parse_unary(self):
        # If the next token is unary `-` or `!`, save and consume the operator.
        # Recursively parse the operand with parse_unary.
        # Return a Unary node for the prefix operator case.
        # Otherwise parse and return a call expression.
        raise NotImplementedError("parse_unary (M2)")

    # call = primary ('(' args? ')')?
    # Hint: check IDENT followed by LPAREN to detect a call. Otherwise just parse_primary.
    def parse_call(self):
        # If the next two tokens are IDENT then `(`, parse a function call.
        # For a call, consume the function name and the opening `(`.
        # Parse zero or more comma-separated argument expressions until `)`.
        # Consume the closing `)`.
        # Return a Call node with the function name and argument list.
        # If no call pattern is present, return parse_primary().
        raise NotImplementedError("parse_call (M2)")

    # primary = NUMBER | 'true' | 'false' | IDENT | '(' expr ')'
    def parse_primary(self):
        # If the next token is NUMBER, consume it and return Number(token.value).
        # If the next token is `true`, consume it and return Bool(True).
        # If the next token is `false`, consume it and return Bool(False).
        # If the next token is IDENT, consume it and return Var(token.text).
        # If the next token is `(`, consume it, parse an expression, consume `)`, and return the expression.
        # Otherwise raise SyntaxError that names the unexpected token and line.
        raise NotImplementedError("parse_primary (M2)")


# ---------------------------------------------------------------------------
# Module entry point used by minilang.py
# ---------------------------------------------------------------------------

def parse(tokens):
    return Parser(tokens).parse()


# ---------------------------------------------------------------------------
# AST pretty-printer (DONE) -- used by the `ast` command. You don't need to
# touch this; once your parse() returns a Program, this just works.
# ---------------------------------------------------------------------------

def print_ast(node, indent=0):
    pad = "  " * indent

    if isinstance(node, Program):
        print(f"{pad}Program")
        for fn in node.functions:
            print_ast(fn, indent + 1)
        if node.main_body:
            print(f"{pad}  (main)")
            for s in node.main_body:
                print_ast(s, indent + 2)
        return

    if isinstance(node, FnDecl):
        params = ", ".join(f"{n}:{t}" for n, t in node.params)
        print(f"{pad}FnDecl {node.name}({params}) -> {node.return_type}")
        for s in node.body:
            print_ast(s, indent + 1)
        return

    if isinstance(node, Let):
        print(f"{pad}Let {node.name}: {node.type} ="); print_ast(node.expr, indent + 1); return
    if isinstance(node, Assign):
        print(f"{pad}Assign {node.name} ="); print_ast(node.expr, indent + 1); return
    if isinstance(node, Block):
        print(f"{pad}Block")
        for s in node.stmts: print_ast(s, indent + 1)
        return
    if isinstance(node, If):
        print(f"{pad}If")
        print(f"{pad}  cond:");  print_ast(node.cond, indent + 2)
        print(f"{pad}  then:");  print_ast(node.then_stmt, indent + 2)
        if node.else_stmt is not None:
            print(f"{pad}  else:"); print_ast(node.else_stmt, indent + 2)
        return
    if isinstance(node, While):
        print(f"{pad}While")
        print(f"{pad}  cond:"); print_ast(node.cond, indent + 2)
        print(f"{pad}  body:"); print_ast(node.body, indent + 2)
        return
    if isinstance(node, Return):
        print(f"{pad}Return")
        if node.expr is not None: print_ast(node.expr, indent + 1)
        return
    if isinstance(node, Print):
        print(f"{pad}Print"); print_ast(node.expr, indent + 1); return
    if isinstance(node, ExprStmt):
        print(f"{pad}ExprStmt"); print_ast(node.expr, indent + 1); return
    if isinstance(node, Binary):
        print(f"{pad}Binary {node.op}")
        print_ast(node.left, indent + 1); print_ast(node.right, indent + 1)
        return
    if isinstance(node, Unary):
        print(f"{pad}Unary {node.op}"); print_ast(node.operand, indent + 1); return
    if isinstance(node, Call):
        print(f"{pad}Call {node.name}")
        for a in node.args: print_ast(a, indent + 1)
        return
    if isinstance(node, Number):
        print(f"{pad}Number {node.value}"); return
    if isinstance(node, Bool):
        print(f"{pad}Bool {node.value}"); return
    if isinstance(node, Var):
        print(f"{pad}Var {node.name}"); return

    print(f"{pad}<unknown node {type(node).__name__}>")
