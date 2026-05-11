# tools/check.py
# Grade a MiniLang compiler against the ladder.
#
# Usage:
#     python3 tools/check.py minilang.py
#
# What it does:
#   - For each of the 12 positive ladder programs, runs the student's compiler
#     in `tokens`, `ast`, `run`, and `wat` modes.
#   - For each of the 4 negative ladder programs, runs `run` and confirms it
#     errors out with a clean message (no Python stack trace).
#   - For `wat`, if Node.js and `tools/runner.js` are available, also instantiates
#     and runs the emitted WebAssembly and compares its output to the expected
#     value (so M5-M7 isn't graded on the textual WAT alone).
#   - Prints a per-rung pass/fail table and a milestone summary.
#
# Exit code: 0 iff every ladder rung passes every applicable stage.

import os
import sys
import subprocess
from pathlib import Path

# --------------------------------------------------------------------------- data

LADDER_POSITIVE = [
    ("01-literal",          ["42"]),
    ("02-arithmetic",       ["7"]),
    ("03-let",              ["10"]),
    ("04-bool",             ["1"]),
    ("05-assignment",       ["2"]),
    ("06-if",               ["1"]),
    ("07-while",            ["1", "2", "3"]),
    ("08-block-scope",      ["99", "1"]),
    ("09-function",         ["42"]),
    ("10-recursion",        ["120"]),
    ("11-short-circuit",    ["0"]),
    ("12-mutual-recursion", ["1"]),
]

LADDER_NEGATIVE = [
    "err-bad-init",
    "err-undefined",
    "err-cond-not-bool",
    "err-bad-arg",
]

# --------------------------------------------------------------------------- shell

def run(compiler, command, ml_path):
    """Run <python> <compiler> <command> <ml_path>. Return (stdout, stderr, returncode)."""
    proc = subprocess.run(
        [sys.executable, str(compiler), command, str(ml_path)],
        capture_output=True, text=True, timeout=15,
    )
    return proc.stdout.rstrip("\n"), proc.stderr.rstrip("\n"), proc.returncode

# --------------------------------------------------------------------------- WAT execution

def have_node_runner(runner_path):
    if not runner_path.exists():
        return False
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def run_wat(runner_path, wat_text):
    """Hand `wat_text` to tools/runner.js. Return (stdout, returncode)."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".wat", delete=False) as f:
        f.write(wat_text); tmp = f.name
    try:
        proc = subprocess.run(
            ["node", str(runner_path), tmp],
            capture_output=True, text=True, timeout=15,
        )
        return proc.stdout.rstrip("\n"), proc.returncode
    finally:
        os.unlink(tmp)

# --------------------------------------------------------------------------- main

def main():
    if len(sys.argv) < 2:
        print("usage: python3 tools/check.py <path/to/minilang.py>", file=sys.stderr)
        sys.exit(2)

    compiler = Path(sys.argv[1]).resolve()
    if not compiler.exists():
        print(f"compiler not found: {compiler}", file=sys.stderr); sys.exit(2)

    repo_root = Path(__file__).resolve().parent.parent
    examples = repo_root / "examples" / "ladder"
    runner = repo_root / "tools" / "runner.js"
    wat_runtime_available = have_node_runner(runner)

    results = []         # (rung, stage, ok, detail)

    # --- positives ---
    for name, expected_lines in LADDER_POSITIVE:
        ml = examples / f"{name}.ml"

        # M1: tokens
        out, err, rc = run(compiler, "tokens", ml)
        ok = (rc == 0 and "EOF" in out)
        results.append((name, "M1 tokens", ok,
                        f"(crashed: {err.splitlines()[0] if err else ''})" if not ok else ""))

        # M2: ast
        out, err, rc = run(compiler, "ast", ml)
        ok = (rc == 0 and "Program" in out)
        results.append((name, "M2 ast", ok,
                        f"(crashed: {err.splitlines()[0] if err else ''})" if not ok else ""))

        # M4: run
        out, err, rc = run(compiler, "run", ml)
        got_lines = out.splitlines()
        ok = (rc == 0 and got_lines == expected_lines)
        if rc != 0:
            detail = f"(error: {err.splitlines()[0] if err else 'no message'})"
        elif got_lines != expected_lines:
            detail = f"(expected {expected_lines}, got {got_lines})"
        else:
            detail = ""
        results.append((name, "M4 run", ok, detail))

        # M5-M7: wat
        out, err, rc = run(compiler, "wat", ml)
        if rc != 0 or not out.strip().startswith("(module"):
            results.append((name, "M5-M7 wat", False,
                            f"(error: {err.splitlines()[0] if err else 'no module'})"))
        elif wat_runtime_available:
            wat_out, wat_rc = run_wat(runner, out)
            wat_lines = wat_out.splitlines()
            ok = (wat_rc == 0 and wat_lines == expected_lines)
            detail = "" if ok else f"(wasm produced {wat_lines})"
            results.append((name, "M5-M7 wat", ok, detail))
        else:
            results.append((name, "M5-M7 wat", True,
                            "(emitted; wasm not executed -- install Node + `npm install wabt` in tools/)"))

    # --- negatives ---
    for name in LADDER_NEGATIVE:
        ml = examples / f"{name}.ml"
        out, err, rc = run(compiler, "run", ml)
        ok = (rc != 0 and ("type error" in err or "syntax error" in err))
        detail = "" if ok else f"(should be rejected; got rc={rc} err={err.splitlines()[0] if err else ''})"
        results.append((name, "M3 reject", ok, detail))

    # ----- per-rung table -----
    print(f"\nChecking compiler: {compiler}\n")
    print(f"{'rung':24} {'stage':14}  result")
    print("-" * 70)
    for rung, stage, ok, detail in results:
        mark = " PASS" if ok else " FAIL"
        print(f"{rung:24} {stage:14}  {mark}  {detail}")

    # ----- milestone summary -----
    by_stage = {}
    for rung, stage, ok, _ in results:
        by_stage.setdefault(stage, []).append(ok)

    print("\nMilestones:")
    for stage in ["M1 tokens", "M2 ast", "M3 reject", "M4 run", "M5-M7 wat"]:
        passed = sum(1 for ok in by_stage.get(stage, []) if ok)
        total = len(by_stage.get(stage, []))
        complete = "DONE" if passed == total and total > 0 else "  ..."
        print(f"  [{complete}]  {stage:14}  {passed}/{total} passed")

    overall_passed = all(ok for _, _, ok, _ in results)
    print(f"\n{'ALL PASSED' if overall_passed else 'Some checks failed.'}\n")
    sys.exit(0 if overall_passed else 1)


if __name__ == "__main__":
    main()
