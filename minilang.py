# minilang.py
# CLI dispatcher. Already wired up -- you don't need to edit this file.
#
# Usage:
#     python3 minilang.py tokens FILE.ml    # M1
#     python3 minilang.py ast    FILE.ml    # M2
#     python3 minilang.py run    FILE.ml    # M4
#     python3 minilang.py wat    FILE.ml    # M5-M7
#     python3 minilang.py build  FILE.ml    # optional bytecode VM

import sys

from src import lexer
from src import parser
from src import typecheck
from src import interpreter
from src import codegen
from src import wat_codegen


def main(argv):
    if len(argv) < 3:
        print("usage: python3 minilang.py <tokens|ast|run|build|wat> FILE.ml",
              file=sys.stderr)
        sys.exit(1)

    cmd, path = argv[1], argv[2]
    with open(path) as f:
        src = f.read()

    try:
        return run_command(cmd, src)
    except SyntaxError as e:
        print(f"syntax error: {e}", file=sys.stderr); sys.exit(1)
    except typecheck.TypeError_ as e:
        print(f"type error: {e}", file=sys.stderr); sys.exit(1)
    except RuntimeError as e:
        print(f"runtime error: {e}", file=sys.stderr); sys.exit(1)


def run_command(cmd, src):
    tokens = lexer.lex(src)

    if cmd == "tokens":
        print(f"{'KIND':7} {'TEXT':10}                LINE")
        print("-" * 50)
        for tok in tokens:
            print(tok)
        return

    program = parser.parse(tokens)

    if cmd == "ast":
        parser.print_ast(program)
        return

    typecheck.check(program)

    if cmd == "run":
        interpreter.run(program)
        return

    if cmd == "build":
        functions = codegen.compile_(program)
        print("=== bytecode ===")
        codegen.print_bytecode(functions)
        print("=== output ===")
        codegen.execute(functions)
        return

    if cmd == "wat":
        print(wat_codegen.compile_(program))
        return

    print(f"unknown command '{cmd}'. Use tokens | ast | run | build | wat.",
          file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
