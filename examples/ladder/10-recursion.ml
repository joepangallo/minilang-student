// 10-recursion.ml
// Teaches: recursion -- a function calls itself.
// Once this works, your interpreter (and later your wasm output) is
// correctly managing the call stack.
// Expected output: 120

fun fact(n: int): int {
  if (n <= 1) return 1;
  return n * fact(n - 1);
}
print(fact(5));
