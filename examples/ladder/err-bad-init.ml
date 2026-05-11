// err-bad-init.ml
// SHOULD BE REJECTED by the type checker.
// Reason: cannot initialize an `int` variable with a `bool` value.
// A good error message names both types and the variable.

let x: int = true;
