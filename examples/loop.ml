// loop.ml -- demonstrates `while`, assignment, and a boolean variable.

let i: int = 0;
let sum: int = 0;

while (i < 10) {
    sum = sum + i;
    i = i + 1;
}

print(sum);     // 0 + 1 + 2 + ... + 9 = 45

let big: bool = sum > 40;
print(big);     // true
