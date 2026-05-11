// err-undefined.ml
// SHOULD BE REJECTED by the type checker.
// Reason: `whatever` was never declared. The symbol-table lookup fails.

print(whatever);
