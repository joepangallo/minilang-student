// 11-short-circuit.ml
// Teaches: short-circuit evaluation of && and ||.
// If && does NOT short-circuit, the right side evaluates `10 / x` with
// x == 0 and crashes with a division-by-zero error. If it DOES short-circuit,
// the right side is skipped because the left side is already false.
// Expected output: 0

let x: int = 0;
if (x != 0 && 10 / x > 0) print(1); else print(0);
