# src/lexer.py
# MILESTONE M1 -- the lexer.
#
# Your job: take a string of MiniLang source code and produce a list of
# Token objects. The parser (M2) will read those tokens, not the raw text.
#
# Everything you NEED is already in this file -- Token class, token-kind
# constants, the KEYWORDS table, and the Lexer skeleton with low-level
# helpers (peek, advance, at_end, lex). The only piece you have to write
# yourself is `Lexer.next_token`. That method picks the next token out
# of `self.src` starting at `self.pos`.
#
# Suggested order of attack:
#   1. Skip whitespace.
#   2. Skip `//` line comments and `/* ... */` block comments.
#   3. Recognize NUMBER (a run of digits).
#   4. Recognize IDENT / keywords (letter or underscore, then alphanumerics).
#   5. Recognize two-character operators (== != <= >= && ||).
#   6. Recognize one-character operators and punctuation.
#   7. On anything unrecognized: raise SyntaxError with the line number.
#
# When you're done, this should work:
#   python3 minilang.py tokens examples/ladder/01-literal.ml
# and produce a token list ending in EOF.

# ---------------------------------------------------------------------------
# Token kinds (string constants -- compare with `tok.kind == NUMBER`).
# ---------------------------------------------------------------------------

NUMBER  = "NUMBER"
IDENT   = "IDENT"

LET     = "LET"
IF      = "IF"
ELSE    = "ELSE"
WHILE   = "WHILE"
FUN     = "FUN"
RETURN  = "RETURN"
TRUE    = "TRUE"
FALSE   = "FALSE"
PRINT   = "PRINT"

PLUS, MINUS, STAR, SLASH = "PLUS", "MINUS", "STAR", "SLASH"
LT, GT, EQ, BANG         = "LT", "GT", "EQ", "BANG"
LPAREN, RPAREN           = "LPAREN", "RPAREN"
LBRACE, RBRACE           = "LBRACE", "RBRACE"
COLON, SEMI, COMMA       = "COLON", "SEMI", "COMMA"

EQEQ, BANGEQ = "EQEQ", "BANGEQ"
LE, GE       = "LE", "GE"
AND, OR      = "AND", "OR"

EOF = "EOF"

KEYWORDS = {
    "let":    LET,
    "if":     IF,
    "else":   ELSE,
    "while":  WHILE,
    "fun":    FUN,
    "return": RETURN,
    "true":   TRUE,
    "false":  FALSE,
    "print":  PRINT,
}


# ---------------------------------------------------------------------------
# Token: a small record describing one token.
# ---------------------------------------------------------------------------

class Token:
    def __init__(self, kind, text, value, line):
        self.kind = kind     # e.g. NUMBER, IDENT, LET, ...
        self.text = text     # exact source substring, e.g. "10"
        self.value = value   # for NUMBER: the int. Else None.
        self.line = line

    def __repr__(self):
        if self.value is not None:
            return f"{self.kind:7} {self.text!r:10} (value={self.value})  line {self.line}"
        return f"{self.kind:7} {self.text!r:10}                line {self.line}"


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    def __init__(self, src):
        self.src = src
        self.pos = 0
        self.line = 1

    # ----- low-level helpers (already done) -----

    def at_end(self):
        return self.pos >= len(self.src)

    def peek(self, offset=0):
        """Return the character `offset` ahead, or '' if past end."""
        i = self.pos + offset
        return self.src[i] if i < len(self.src) else ""

    def advance(self):
        """Consume and return the current character."""
        c = self.src[self.pos]
        self.pos += 1
        if c == "\n":
            self.line += 1
        return c

    # ----- main loop (already done) -----

    def lex(self):
        tokens = []
        while not self.at_end():
            tok = self.next_token()
            if tok is not None:           # whitespace/comments return None
                tokens.append(tok)
        tokens.append(Token(EOF, "", None, self.line))
        return tokens

    # ----- TODO M1: the one method you have to write -----

    def next_token(self):
        """Read the next token from the source, starting at self.pos.

        Returns a Token, or None for whitespace/comments.
        Raises SyntaxError on an unrecognized character.

        Hints:
          - `self.peek()` looks at the current char without consuming.
          - `self.peek(1)` looks one ahead (for two-char operators like '==').
          - `self.advance()` consumes one char and returns it.
          - For NUMBER, walk while `self.peek().isdigit()`.
          - For IDENT/keywords, walk while alnum or '_', then look up in KEYWORDS.
          - Return `Token(KIND, text, value_or_None, self.line)` -- but use
            the line at the START of the token, not after advancing.
        """
        raise NotImplementedError("Lexer.next_token -- implement me (Milestone M1)")


# ---------------------------------------------------------------------------
# Convenience entry point used by minilang.py
# ---------------------------------------------------------------------------

def lex(src):
    return Lexer(src).lex()
