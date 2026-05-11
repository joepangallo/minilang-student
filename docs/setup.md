# Setup — get your dev machine ready in fifteen minutes

You need three things installed: Python 3.10 or newer, Node.js (any
recent LTS), and a one-time `npm install wabt`. That's it for the basic
workflow. If you want to use the official `wat2wasm` CLI tool too
(strictly optional — the Node runner has it built in), there's a
fourth install.

This document gives you copy-paste commands for macOS, Windows, and
Linux, plus verification commands at the bottom so you know everything
works.

---

## macOS

If you don't already have Homebrew, install it:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Then:

```bash
brew install python@3.12 node
```

Clone this repository and install the wasm assembler library:

```bash
git clone <your-instructor-will-give-you-the-url>.git
cd minilang
cd tools && npm install wabt && cd ..
```

(Optional but recommended.) If you want the official `wat2wasm` CLI
for inspecting the WAT-to-wasm assembly directly:

```bash
brew install wabt
```

---

## Windows

Use the official Python installer from python.org (check "Add Python to
PATH" during install) and the official Node.js installer from nodejs.org.
Then in PowerShell:

```powershell
git clone <your-instructor-will-give-you-the-url>.git
cd minilang
cd tools
npm install wabt
cd ..
```

(Optional.) WABT for Windows: download a release zip from
https://github.com/WebAssembly/wabt/releases and add `bin/` to your PATH.

---

## Linux

```bash
sudo apt-get install -y python3 python3-pip nodejs npm git
```

(Ubuntu's `nodejs` may be old; if your `node --version` is below 18,
install a newer LTS via https://nodejs.org/ or `nvm`.)

```bash
git clone <your-instructor-will-give-you-the-url>.git
cd minilang
cd tools && npm install wabt && cd ..
```

(Optional.) `sudo apt-get install -y wabt` for the official CLI.

---

## Verify

Run these four commands from the repo root. Each should print the
expected output. If any one fails, fix it before moving on.

```bash
# 1. Python works.
python3 --version             # Python 3.10 or newer
```

```bash
# 2. Node works.
node --version                # v18 or newer
```

```bash
# 3. The CLI dispatcher loads.
python3 minilang.py tokens examples/ladder/01-literal.ml
# expected: NotImplementedError: Lexer.next_token — implement me (Milestone M1)
```

That error is what you *want* to see — it means Python found the
dispatcher, the dispatcher found `src/lexer.py`, and you're now staring
at the first method you need to write.

```bash
# 4. wabt is installed (no error, just exits silently).
node -e "require('wabt')().then(() => console.log('wabt OK'))"
# expected: wabt OK
```

If all four checks pass you're set. Open `README.md` and start on
Milestone M1.

## Troubleshooting

**"command not found: python3"** — install Python (see above). On Windows
the command may be `python` instead of `python3`.

**"Cannot find module 'wabt'"** when running `tools/run.sh` — you skipped
the `npm install wabt` step. Run it from inside `tools/`.

**`tools/run.sh: permission denied`** — `chmod +x tools/run.sh`.

**Anything else** — run `python3 tools/check.py minilang.py`. On a
fresh clone it should report every rung failing at M1, which confirms
the environment itself is fine and the work ahead is in your code.
