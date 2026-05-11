#!/bin/bash
# tools/run.sh -- compile a MiniLang source file and run it on real wasm.
#
# Usage:
#     tools/run.sh examples/ladder/01-literal.ml
#
# Requires Node.js and a one-time `cd tools && npm install wabt`.

set -e
src="$1"
if [ -z "$src" ]; then
    echo "usage: tools/run.sh FILE.ml" >&2
    exit 1
fi
here="$(cd "$(dirname "$0")" && pwd)"
wat="$(mktemp -t minilang.XXXXXX).wat"
python3 "$here/../minilang.py" wat "$src" > "$wat"
node "$here/runner.js" "$wat"
rm "$wat"
