// 12-mutual-recursion.ml
// Teaches: mutual recursion -- two functions that call each other.
// This is the program that REQUIRES two-pass type checking. You can't
// check isEven's body before isOdd's signature is known, and vice versa,
// so the type checker must collect all signatures in a first pass before
// checking any bodies.
// Expected output: 1   (true, since 10 is even)

fun isEven(n: int): bool {
  if (n == 0) return true;
  return isOdd(n - 1);
}
fun isOdd(n: int): bool {
  if (n == 0) return false;
  return isEven(n - 1);
}
print(isEven(10));
