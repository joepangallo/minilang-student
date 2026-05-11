// err-cond-not-bool.ml
// SHOULD BE REJECTED by the type checker.
// Reason: an `if` condition must be of type `bool`. The expression (1 + 1)
// has type `int`, so this is a type error -- even though many languages
// (C, Python) accept it. MiniLang does not.

if (1 + 1) print(1);
