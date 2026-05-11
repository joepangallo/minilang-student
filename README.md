# MiniLang — student starter kit

This repo is what you'll spend the next four weeks filling in. Every
source file under `src/` has a class skeleton, the data types you'll
need, BNF comments where relevant, and a `NotImplementedError` in each
method you have to write yourself. The CLI dispatcher (`minilang.py`)
is already wired up — you don't need to touch it.

## Your day-1 checklist

1. Make sure you've worked through `docs/setup.md`. You need
   Python 3.10+, Node.js, and `npm install wabt` once inside `tools/`.

2. From the repo root, try this:

   ```bash
   python3 minilang.py tokens examples/ladder/01-literal.ml
   ```

   You'll get:

   ```
   NotImplementedError: Lexer.next_token — implement me (Milestone M1)
   ```

   Good. That's where you start.

3. Open `src/lexer.py`, find `next_token`, and write it. When
   you're done, the command above should produce a clean token list.

4. Run the checkpoint script from the repo root:

   ```bash
   python3 tools/check.py minilang.py
   ```

   It runs every ladder program through every command and tells you
   which milestones you've completed.

## The milestone -> file map

| Milestone | File you'll be writing       | Unlocks                   |
|-----------|------------------------------|---------------------------|
| M1        | `src/lexer.py`               | `tokens` command          |
| M2        | `src/parser.py`              | `ast` command             |
| M3        | `src/typecheck.py`           | Catches type errors       |
| M4        | `src/interpreter.py`         | `run` command             |
| M5–M7     | `src/wat_codegen.py`         | `wat` command (graded)    |
| (optional)| `src/codegen.py`             | `build` (bytecode VM)     |

## Where the BNF lives

Each method in `parser.py` has its grammar production written in a
comment directly above it. Read the comment first, then write the code
to match. Recursive descent is at its best when the BNF and the code
look like the same thing.

## When you get stuck

Run the checkpoint script:

```bash
python3 tools/check.py minilang.py
```

It runs each ladder program through your compiler and tells you the
expected output, your actual output, and which rung failed. The diff
points straight at the stage that went wrong.

If you're still stuck, bring your output to office hours — your
instructor has the reference compiler and can show you the diff
against it.

## Order of attack

1. Get rung 1 (`01-literal.ml`) working through `tokens`. That's just
   `next_token`. Tiny scope.
2. Add identifier/keyword handling so `03-let.ml` lexes.
3. Add operators so `02-arithmetic.ml` lexes.
4. Once all twelve positive rungs tokenize, **move on to the parser**.
5. Same drill for the parser: get rung 1 parsing, then rung 2, then
   add features until the ladder climbs.

This is intentional: each ladder rung is a discrete, runnable success.
You should see something green at least once per class.
