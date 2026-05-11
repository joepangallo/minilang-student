// runner.js
// A tiny Node.js runner for the MiniLang back end.
//
// Usage:
//     node tools/runner.js examples/ladder/10-recursion.ml.wat
//     node tools/runner.js out.wasm           // also works for raw .wasm bytes
//
// What it does:
//   1. Reads a .wat or .wasm file from disk.
//   2. If it's .wat, uses the wabt JS library (which is itself wasm!) to
//      assemble it to a .wasm binary in memory. So you don't need to install
//      the system `wat2wasm` tool just to demo your compiler.
//   3. Instantiates the module, supplying `env.print` as a host function that
//      just `console.log`s whatever the wasm passes in.
//   4. The MiniLang module's `(start $main)` runs automatically at
//      instantiation, so we don't have to invoke anything by hand.
//
// One-time setup:
//     cd tools && npm install wabt
//
// (If you'd rather use the official CLI: `brew install wabt`, then
//  `wat2wasm out.wat -o out.wasm` and run this script on the .wasm.)

const fs = require("fs");
const path = require("path");

async function main() {
    const file = process.argv[2];
    if (!file) {
        console.error("usage: node runner.js <file.wat | file.wasm>");
        process.exit(1);
    }

    // Load the file and produce a wasm Uint8Array regardless of input format.
    const ext = path.extname(file).toLowerCase();
    let wasmBytes;
    if (ext === ".wat") {
        const wabt = await require("wabt")();
        const source = fs.readFileSync(file, "utf8");
        const module = wabt.parseWat(file, source);
        wasmBytes = module.toBinary({}).buffer;
    } else if (ext === ".wasm") {
        wasmBytes = fs.readFileSync(file);
    } else {
        console.error(`unsupported extension: ${ext} (expected .wat or .wasm)`);
        process.exit(1);
    }

    // Provide the imported `env.print` that MiniLang emits a call to.
    // Every `print(x);` in MiniLang turns into `call $print` in WAT.
    const imports = {
        env: {
            print: (value) => console.log(value),
        },
    };

    // `(start $main)` in the wasm module runs at instantiation, so we just
    // wait for instantiate() to resolve and we're done.
    await WebAssembly.instantiate(wasmBytes, imports);
}

main().catch((err) => {
    console.error("error:", err.message || err);
    process.exit(1);
});
