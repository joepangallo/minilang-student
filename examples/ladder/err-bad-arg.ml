// err-bad-arg.ml
// SHOULD BE REJECTED by the type checker.
// Reason: `double` expects an `int` argument but is called with a `bool`.
// Tests that argument types are checked against the function's signature.

fun double(n: int): int {
  return n * 2;
}
print(double(true));
