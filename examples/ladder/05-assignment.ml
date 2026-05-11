// 05-assignment.ml
// Teaches: assignment is different from declaration.
// `let x: int = 1;` introduces x and gives it a type.
// `x = x + 1;`     mutates x; no new variable is created.
// Expected output: 2

let x: int = 1;
x = x + 1;
print(x);
