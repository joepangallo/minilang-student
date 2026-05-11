# src/codegen.py
# OPTIONAL milestone -- compile to a tiny stack-based bytecode and run it
# on a small Python VM. Pedagogically useful even though it's not graded:
# the WAT codegen (see wat_codegen.py) is the same shape with a different
# output instruction set.
#
# What you GET for free:
#   - The VM (Frame, VM.step, VM.run) is fully implemented. You can run
#     bytecode without touching it.
#   - Compiler scope-stack helpers (declare/resolve with name mangling)
#   - emit / patch_jump / here utilities
#
# What you HAVE TO WRITE (if you're doing this milestone):
#   - compile_stmt: lower each statement to bytecode
#   - compile_expr: lower each expression to bytecode
#
# Instruction set (tuples):
#   PUSH v / LOAD name / STORE name
#   ADD / SUB / MUL / DIV / NEG
#   LT / LE / GT / GE / EQ / NE
#   NOT
#   JMP target / JZ target           (jump targets are instruction indices)
#   CALL name / RET
#   PRINT / HALT
#
# Short-circuit && and || compile to JZ + JMP, not to AND/OR opcodes.

from src import parser as P


def _i32(x):
    x = x & 0xFFFFFFFF
    if x >= 0x80000000:
        x -= 0x100000000
    return x


class Compiler:
    def __init__(self):
        self.functions = {}
        self.code = None
        self.scopes = []
        self.next_id = 0

    # ----- emit helpers (DONE) -----

    def emit(self, *instr):
        self.code.append(instr); return len(self.code) - 1
    def patch_jump(self, idx, target):
        op = self.code[idx][0]
        self.code[idx] = (op, target)
    def here(self):
        return len(self.code)

    # ----- scope / name mangling (DONE) -----

    def push_scope(self): self.scopes.append({})
    def pop_scope(self):  self.scopes.pop()
    def declare(self, name):
        wat = f"{name}#{self.next_id}"; self.next_id += 1
        self.scopes[-1][name] = wat; return wat
    def resolve(self, name):
        for scope in reversed(self.scopes):
            if name in scope: return scope[name]
        return name

    # ----- driver (DONE) -----

    def compile(self, program):
        for fn in program.functions:
            self.compile_fn(fn)
        self.code = []
        self.functions["_main"] = self.code
        self.scopes = [{}]; self.next_id = 0
        for stmt in program.main_body:
            self.compile_stmt(stmt)
        self.emit("HALT")
        return self.functions

    def compile_fn(self, fn):
        self.code = []
        self.functions[fn.name] = self.code
        self.scopes = [{}]; self.next_id = 0
        mangled_params = [self.declare(name) for (name, _t) in fn.params]
        for mangled in reversed(mangled_params):
            self.emit("STORE", mangled)
        for stmt in fn.body:
            self.compile_stmt(stmt)
        self.emit("PUSH", 0); self.emit("RET")

    # ----- TODO: compilation -----

    def compile_stmt(self, stmt):
        # Let:    compile_expr; emit STORE (declare and get mangled name)
        # Assign: compile_expr; emit STORE self.resolve(name)
        # Block:  push_scope; compile each; pop_scope
        # If:     compile cond; JZ to else; compile then; JMP to end; patch JZ; (else); patch JMP
        # While:  remember loop_start; cond; JZ to end; body; JMP loop_start; patch JZ
        # Return: compile expr (or PUSH 0); RET
        # Print:  compile expr; PRINT
        # ExprStmt: compile expr (leave result on stack; VM tolerates)
        raise NotImplementedError("compile_stmt (codegen)")

    def compile_expr(self, expr):
        # Number / Bool: PUSH value
        # Var:           LOAD self.resolve(name)
        # Unary:         compile operand; NEG or NOT
        # Binary &&/||:  short-circuit using JZ + JMP + PUSH False/True
        # Binary other:  compile both sides; emit the right opcode (ADD/SUB/...)
        # Call:          compile each arg; CALL name
        raise NotImplementedError("compile_expr (codegen)")


# ---------------------------------------------------------------------------
# Bytecode VM -- fully implemented. You only fill in Compiler above.
# ---------------------------------------------------------------------------

class Frame:
    def __init__(self, code):
        self.code = code; self.ip = 0; self.env = {}


class VM:
    def __init__(self, functions):
        self.functions = functions
        self.stack = []
        self.frames = []

    def run(self):
        self.frames.append(Frame(self.functions["_main"]))
        while self.frames:
            self.step()

    def step(self):
        frame = self.frames[-1]
        instr = frame.code[frame.ip]; frame.ip += 1
        op = instr[0]

        if op == "PUSH":  self.stack.append(instr[1]); return
        if op == "LOAD":  self.stack.append(frame.env[instr[1]]); return
        if op == "STORE": frame.env[instr[1]] = self.stack.pop(); return

        if op == "ADD": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(_i32(a+b)); return
        if op == "SUB": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(_i32(a-b)); return
        if op == "MUL": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(_i32(a*b)); return
        if op == "DIV":
            b=self.stack.pop(); a=self.stack.pop()
            if b == 0: raise RuntimeError("division by zero")
            q = abs(a) // abs(b)
            if (a<0) ^ (b<0): q = -q
            self.stack.append(_i32(q)); return
        if op == "NEG": a=self.stack.pop(); self.stack.append(_i32(-a)); return

        if op == "LT": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a<b); return
        if op == "LE": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a<=b); return
        if op == "GT": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a>b); return
        if op == "GE": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a>=b); return
        if op == "EQ": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a==b); return
        if op == "NE": b=self.stack.pop(); a=self.stack.pop(); self.stack.append(a!=b); return
        if op == "NOT": a=self.stack.pop(); self.stack.append(not a); return

        if op == "JMP": frame.ip = instr[1]; return
        if op == "JZ":
            v = self.stack.pop()
            if not v: frame.ip = instr[1]
            return

        if op == "CALL": self.frames.append(Frame(self.functions[instr[1]])); return
        if op == "RET":  self.frames.pop(); return

        if op == "PRINT":
            v = self.stack.pop()
            if v is True:    print(1)
            elif v is False: print(0)
            else:            print(v)
            return
        if op == "HALT": self.frames = []; return

        raise RuntimeError(f"unknown opcode {op}")


def compile_(program):
    return Compiler().compile(program)


def print_bytecode(functions):
    names = [n for n in functions if n != "_main"] + ["_main"]
    for name in names:
        if name not in functions: continue
        print(f"function {name}:")
        for i, instr in enumerate(functions[name]):
            args = " ".join(repr(x) for x in instr[1:])
            print(f"  {i:3}  {instr[0]:6} {args}")
        print()


def execute(functions):
    VM(functions).run()
