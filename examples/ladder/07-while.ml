// 07-while.ml
// Teaches: while loops, loop condition, mutating a variable inside the body.
// Expected output: 1
//                  2
//                  3

let i: int = 1;
while (i <= 3) {
  print(i);
  i = i + 1;
}
