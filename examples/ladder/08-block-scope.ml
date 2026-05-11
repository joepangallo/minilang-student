// 08-block-scope.ml
// Teaches: block scope and shadowing.
// The inner `x` is a separate variable from the outer `x`. At `}` the inner
// one disappears and the outer one is visible again. This is the program
// that justifies a stack-of-scopes in your symbol table.
// Expected output: 99
//                  1

let x: int = 1;
{
  let x: int = 99;
  print(x);
}
print(x);
