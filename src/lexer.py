# lexer.py
# Stage 1 of the compiler: turn source text into a list of "tokens".
#
# A token is the smallest meaningful chunk of code: a keyword like `let`,
# a name like `x`, a number like `10`, or a symbol like `+` or `;`.
# The parser (stage 2) reads tokens, not raw text.

# ---------------------------------------------------------------------------
# Token kinds.
#
# We just use short uppercase strings. They're easy to print and easy to
# compare. (A more "Pythonic" version would use an Enum, but strings keep
# things simple for an intro class.)
# ---------------------------------------------------------------------------

# literals and names
NUMBER  = "NUMBER"
IDENT   = "IDENT"

# keywords
LET     = "LET"
IF      = "IF"
ELSE    = "ELSE"
WHILE   = "WHILE"
FUN     = "FUN"
RETURN  = "RETURN"
TRUE    = "TRUE"
FALSE   = "FALSE"
PRINT   = "PRINT"

# one-character symbols
PLUS    = "PLUS"     # +
MINUS   = "MINUS"    # -
STAR    = "STAR"     # *
SLASH   = "SLASH"    # /
LT      = "LT"       # <
GT      = "GT"       # >
EQ      = "EQ"       # =
BANG    = "BANG"     # !
LPAREN  = "LPAREN"   # (
RPAREN  = "RPAREN"   # )
LBRACE  = "LBRACE"   # {
RBRACE  = "RBRACE"   # }
COLON   = "COLON"    # :
SEMI    = "SEMI"     # ;
COMMA   = "COMMA"    # ,

# two-character symbols
EQEQ    = "EQEQ"     # ==
BANGEQ  = "BANGEQ"   # !=
LE      = "LE"       # <=
GE      = "GE"       # >=
AND     = "AND"      # &&
OR      = "OR"       # ||

# end-of-file marker (always the last token)
EOF     = "EOF"


# Map a keyword's spelling to its token kind. If a word isn't here,
# it's an identifier (a variable or function name).
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
    """One token: a kind tag, the source text it came from, an optional value, and a line number."""
    def __init__(self, kind, text, value, line):
        self.kind = kind     # one of the constants above, e.g. NUMBER
        self.text = text     # the exact substring of the source, e.g. "10"
        self.value = value   # for NUMBER: the int 10. Otherwise None.
        self.line = line     # line number, for error messages

    def __repr__(self):
        # Pretty-print tokens for the `tokens` command.
        if self.value is not None:
            return f"{self.kind:7} {self.text!r:10} (value={self.value})  line {self.line}"
        return f"{self.kind:7} {self.text!r:10}                line {self.line}"


# ---------------------------------------------------------------------------
# Lexer: walks the source string one character at a time and produces tokens.
# ---------------------------------------------------------------------------

class Lexer:
    """Walks the source string and produces a stream of tokens."""
    def __init__(self, src):
        self.src = src
        self.pos = 0      # index of the next character to read
        self.line = 1     # current line number (for error messages)

    # --- low-level helpers ---------------------------------------------------

    def at_end(self):
        return self.pos >= len(self.src)

    def peek(self, offset=0):
        """Look at a character without consuming it."""
        i = self.pos + offset
        if i < len(self.src):
            return self.src[i]
        return ""   # empty string means "past the end"

    def advance(self):
        """Consume the current character and return it."""
        c = self.src[self.pos]
        self.pos += 1
        # bump the line counter so error messages stay accurate
        if c == "\n":
            self.line += 1
        return c

    # --- main entry point ---------------------------------------------------

    def lex(self):
        """Run the lexer and return a list of tokens (ending in EOF)."""
        tokens = []
        while not self.at_end():
            tok = self.next_token()
            if tok is not None:        # whitespace/comments return None
                tokens.append(tok)
        tokens.append(Token(EOF, "", None, self.line))
        return tokens

    # --- pick the next token ------------------------------------------------

    def next_token(self):
        """Read one token from the current position, or return None for whitespace/comments."""
        c = self.peek()

        # skip whitespace
        if c in " \t\r\n":
            self.advance()
            return None

        # skip "// line comments"
        if c == "/" and self.peek(1) == "/":
            while not self.at_end() and self.peek() != "\n":
                self.advance()
            return None

        # skip "/* block comments */"
        if c == "/" and self.peek(1) == "*":
            self.advance(); self.advance()
            while not self.at_end() and not (self.peek() == "*" and self.peek(1) == "/"):
                self.advance()
            if not self.at_end():
                self.advance(); self.advance()    # consume the closing "*/"
            return None

        # numbers: a run of digits
        if c.isdigit():
            return self.number()

        # identifiers or keywords: start with letter or _, then letters/digits/_
        if c.isalpha() or c == "_":
            return self.identifier()

        # two-character symbols: check these before single-character ones,
        # otherwise "==" would lex as two separate "=" tokens

        two = self.src[self.pos:self.pos + 2]
        two_char = {
            "==": EQEQ, "!=": BANGEQ,
            "<=": LE,   ">=": GE,
            "&&": AND,  "||": OR,
        }
        if two in two_char:
            self.advance(); self.advance()
            return Token(two_char[two], two, None, self.line)

        # single-character symbols
        one_char = {
            "+": PLUS, "-": MINUS, "*": STAR, "/": SLASH,
            "<": LT,   ">": GT,    "=": EQ,   "!": BANG,
            "(": LPAREN, ")": RPAREN, "{": LBRACE, "}": RBRACE,
            ":": COLON,  ";": SEMI,    ",": COMMA,
        }
        if c in one_char:
            self.advance()
            return Token(one_char[c], c, None, self.line)

        # anything else is an error
        raise SyntaxError(f"line {self.line}: unexpected character {c!r}")

    # --- multi-character token helpers --------------------------------------

    def number(self):
        """Consume a run of digits and return a NUMBER token."""
        start = self.pos
        while not self.at_end() and self.peek().isdigit():
            self.advance()
        text = self.src[start:self.pos]
        return Token(NUMBER, text, int(text), self.line)

    def identifier(self):
        """Consume a name and return a keyword token if it matches, otherwise IDENT."""
        start = self.pos
        while not self.at_end() and (self.peek().isalnum() or self.peek() == "_"):
            self.advance()
        text = self.src[start:self.pos]
        # if it's a keyword, use that kind; otherwise it's a plain identifier
        kind = KEYWORDS.get(text, IDENT)
        return Token(kind, text, None, self.line)


# Convenience function so callers can write `lex(src)` instead of building
# a Lexer object themselves.
def lex(src):
    """Tokenize a source string and return the list of tokens."""
    return Lexer(src).lex()
