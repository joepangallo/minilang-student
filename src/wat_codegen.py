# src/wat_codegen.py
# MILESTONES M5-M7 -- the WebAssembly Text Format back end. THIS IS GRADED.
#
# Your job: emit a complete (module ...) string of WAT that, when piped
# through `wat2wasm` and run with `env.print` provided, produces the same
# output as your interpreter (M4).
#
# What you GET for free:
#   - WatCompiler scaffold with emit, indent, scope-stack, name-mangling
#   - The driver that puts together the module preamble, the user functions,
#     the synthesized $main, and the (start $main) directive
#   - The (import "env" "print" ...) line in the preamble
#
# What you HAVE TO WRITE:
#   - compile_stmt for every statement type
#   - compile_expr for every expression type
#
# WAT cheatsheet (memorize these):
#
#   MiniLang                 WAT
#   --------                 ---
#   42                       i32.const 42
#   true / false             i32.const 1 / i32.const 0
#   x  (local)               local.get $<mangled>
#   x = e  (local)           <e>  local.set $<mangled>
#   let x = e                <e>  local.set $<mangled>      (also (local $x i32) at top)
#   a + b                    <a> <b> i32.add               (also -, *, /=div_s)
#   a == b / a != b          <a> <b> i32.eq / i32.ne
#   a < b / <= / > / >=      <a> <b> i32.lt_s / le_s / gt_s / ge_s
#   !b                       <b> i32.eqz
#   -x                       i32.const 0  <x>  i32.sub
#   if (c) S1 else S2        <c>  if  <S1>  else  <S2>  end
#   while (c) S              block  loop  <c>  i32.eqz  br_if 1  <S>  br 0  end  end
#   return e                 <e>  return
#   print(e)                 <e>  call $print
#   expression statement     <expr>  drop     (discard leftover value)
#   f(a, b)                  <a>  <b>  call $f
#
# Short-circuit && and ||  -- WAT's `if (result i32) ... else ... end` makes
# `if` work as an expression. See the hint in compile_expr below.
#
# Locals: ALL `let`-introduced names in a function must be declared at the
# TOP of that function with `(local $name i32)` BEFORE any instructions.
# The scaffold below handles this: as you call self.declare_local(name) in
# compile_stmt, the local accumulates in self.locals and gets emitted up
# front by the driver.

from src import parser as P


class WatCompiler:
    def __init__(self):
        self.body = []     # current function's instruction lines (indented)
        self.locals = []   # current function's local names (excluding params)
        self.scopes = []
        self.next_id = 0
        self.indent = 0

    # ----- helpers (DONE) -----

    def emit(self, line):
        self.body.append("  " * self.indent + line)

    def fresh(self, name):
        wat = f"${name}_{self.next_id}"; self.next_id += 1; return wat

    def declare_local(self, name):
        wat = self.fresh(name); self.scopes[-1][name] = wat
        self.locals.append(wat); return wat

    def resolve(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        raise RuntimeError(f"wat_codegen: unresolved '{name}'")

    def push_scope(self): self.scopes.append({})
    def pop_scope(self):  self.scopes.pop()

    # ----- driver (DONE) -----

    def compile(self, program):
        out = ["(module"]
        out.append('  (import "env" "print" (func $print (param i32)))')
        for fn in program.functions:
            out.extend(self.compile_fn(fn))
        out.extend(self.compile_main(program.main_body))
        out.append("  (start $main)")
        out.append(")")
        return "\n".join(out)

    def compile_fn(self, fn):
        self.body, self.locals, self.scopes = [], [], [{}]
        self.next_id = 0; self.indent = 2
        param_decls = []
        for (name, _t) in fn.params:
            wat = self.fresh(name)
            self.scopes[0][name] = wat
            param_decls.append(f"(param {wat} i32)")
        for stmt in fn.body:
            self.compile_stmt(stmt)
        # safety net
        self.emit("i32.const 0"); self.emit("return")
        header = f"  (func ${fn.name}"
        if param_decls: header += " " + " ".join(param_decls)
        header += " (result i32)"
        out = [header]
        for lcl in self.locals: out.append(f"    (local {lcl} i32)")
        out.extend(self.body)
        out.append("  )")
        return out

    def compile_main(self, stmts):
        self.body, self.locals, self.scopes = [], [], [{}]
        self.next_id = 0; self.indent = 2
        for stmt in stmts:
            self.compile_stmt(stmt)
        out = ['  (func $main (export "main")']
        for lcl in self.locals: out.append(f"    (local {lcl} i32)")
        out.extend(self.body)
        out.append("  )")
        return out

    # ----- TODO M5-M7 -----

    def compile_stmt(self, stmt):
        # Let:     compile_expr(stmt.expr); wat = self.declare_local(stmt.name);
        #          self.emit(f"local.set {wat}")
        # Assign:  compile_expr; self.emit(f"local.set {self.resolve(name)}")
        # Block:   push_scope; compile each; pop_scope
        # If:      compile cond; emit "if"; compile_stmt(then); (else: emit "else"; compile_stmt(else)); emit "end"
        # While:   emit "block"; emit "loop"; cond; emit "i32.eqz"; emit "br_if 1";
        #          compile body; emit "br 0"; emit "end"; emit "end"
        # Return:  compile expr (or i32.const 0); emit "return"
        # Print:   compile expr; emit "call $print"
        # ExprStmt: compile expr; emit "drop"
        # For Let, compile the initializer so the value is on the wasm stack.
        # Declare the local to reserve its mangled `(local ...)` entry.
        # Emit `local.set` for that local.
        # For Assign, compile the right-hand side and emit `local.set` for resolve(name).
        # For Block, push a new scope, compile nested statements, and pop in finally.
        # For If, compile the condition, emit `if`, compile the then branch, optional `else`, and `end`.
        # For While, emit `block` and `loop` before compiling the condition.
        # In While, emit `i32.eqz` and `br_if 1` to leave the loop when the condition is false.
        # Compile the body, emit `br 0` to repeat, then close both structures with `end`.
        # For Return, compile the expression or `i32.const 0` for bare return, then emit `return`.
        # For Print, compile the expression and emit `call $print`.
        # For ExprStmt, compile the expression and emit `drop`.
        # If no isinstance case matches, raise RuntimeError for the unknown statement node.
        raise NotImplementedError("wat compile_stmt (M5-M7)")

    def compile_expr(self, expr):
        # Number: emit f"i32.const {value}"
        # Bool:   emit f"i32.const {1 if value else 0}"
        # Var:    emit f"local.get {self.resolve(name)}"
        # Unary - : emit "i32.const 0"; compile operand; emit "i32.sub"
        # Unary ! : compile operand; emit "i32.eqz"
        # Binary && (short-circuit):
        #     compile left;
        #     emit "if (result i32)"
        #     compile right
        #     emit "else"; emit "  i32.const 0"; emit "end"
        # Binary || (short-circuit):
        #     compile left;
        #     emit "if (result i32)"; emit "  i32.const 1"
        #     emit "else"; compile right; emit "end"
        # Other binary: compile both sides; emit the right opcode from the
        #     cheatsheet (i32.add / i32.sub / i32.mul / i32.div_s / i32.lt_s / etc.)
        # Call:   compile each arg; emit f"call ${name}"
        # For Number, emit `i32.const` with the integer value.
        # For Bool, emit `i32.const 1` for true or `i32.const 0` for false.
        # For Var, emit `local.get` for resolve(name).
        # For Unary `-`, emit zero, compile the operand, then emit `i32.sub`.
        # For Unary `!`, compile the operand, then emit `i32.eqz`.
        # For Binary `&&`, compile left and use `if (result i32)` to short-circuit false.
        # For Binary `||`, compile left and use `if (result i32)` to short-circuit true.
        # For other Binary operators, compile left then right and emit the matching WAT opcode.
        # For Call, compile arguments left-to-right, then emit `call $name`.
        # If no isinstance case matches, raise RuntimeError for the unknown expression node.
        raise NotImplementedError("wat compile_expr (M5-M7)")


def compile_(program):
    return WatCompiler().compile(program)
