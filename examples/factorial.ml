// factorial.ml -- recursion, if/else, comparison, function calls.

fun factorial(n: int): int {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}

let result: int = factorial(5);
print(result);    // 120
