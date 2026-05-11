// 06-if.ml
// Teaches: if/else, comparison operators producing a bool.
// Type-checker exercise: change `x > 0` to `x + 0` -- the type checker
// should reject the program because an `if` condition must be bool.
// Expected output: 1

let x: int = 5;
if (x > 0) print(1); else print(0);
