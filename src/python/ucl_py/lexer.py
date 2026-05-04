from .tokens import Token, TokenKind

def lex(text: str):
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1; continue
        if c.isalpha() or c == '_':
            j = i
            while j < n and (text[j].isalnum() or text[j] in '_-'):
                j += 1
            val = text[i:j]
            kind = {
                "true": TokenKind.TRUE,
                "false": TokenKind.FALSE,
                "null": TokenKind.NULL,
            }.get(val, TokenKind.IDENT)
            tokens.append(Token(kind, val, i))
            i = j; continue
        if c.isdigit():
            j = i
            while j < n and (text[j].isdigit() or text[j] == '.'):
                j += 1
            tokens.append(Token(TokenKind.NUMBER, text[i:j], i))
            i = j; continue
        if c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 1
            tokens.append(Token(TokenKind.STRING, text[i+1:j], i))
            i = j + 1; continue
        single = {
            '{': TokenKind.LBRACE, '}': TokenKind.RBRACE,
            '[': TokenKind.LBRACK, ']': TokenKind.RBRACK,
            '(': TokenKind.LPAREN, ')': TokenKind.RPAREN,
            '.': TokenKind.DOT, ',': TokenKind.COMMA,
            ':': TokenKind.COLON, ';': TokenKind.SEMI,
            '=': TokenKind.EQ, '+': TokenKind.PLUS,
            '-': TokenKind.MINUS, '*': TokenKind.STAR,
            '/': TokenKind.SLASH,
        }
        if c in single:
            tokens.append(Token(single[c], c, i))
            i += 1; continue
        raise ValueError(f"Unexpected char {c} at {i}")
    tokens.append(Token(TokenKind.EOF, "", n))
    return tokens
