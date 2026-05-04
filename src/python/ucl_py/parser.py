from .tokens import TokenKind
from .ast import Program, Assignment, Section

class Parser:
    def __init__(self, tokens):
        self.toks = tokens
        self.i = 0

    def cur(self):
        return self.toks[self.i]

    def eat(self, kind):
        if self.cur().kind != kind:
            raise ValueError(f"Expected {kind}, got {self.cur().kind}")
        self.i += 1

    def parse(self):
        items = []
        while self.cur().kind != TokenKind.EOF:
            items.append(self.parse_stmt())
        return Program(items)

    def parse_stmt(self):
        # very minimal: ident = string;
        tok = self.cur()
        if tok.kind == TokenKind.IDENT:
            name = tok.value
            self.eat(TokenKind.IDENT)
            if self.cur().kind == TokenKind.LBRACE:
                self.eat(TokenKind.LBRACE)
                body = []
                while self.cur().kind != TokenKind.RBRACE:
                    body.append(self.parse_stmt())
                self.eat(TokenKind.RBRACE)
                return Section(name, body)
            self.eat(TokenKind.EQ)
            val = self.parse_value()
            if self.cur().kind == TokenKind.SEMI:
                self.eat(TokenKind.SEMI)
            return Assignment(name, val)
        raise ValueError("Invalid statement")

    def parse_value(self):
        tok = self.cur()
        if tok.kind in (TokenKind.STRING, TokenKind.NUMBER):
            self.i += 1
            return tok.value
        if tok.kind == TokenKind.TRUE:
            self.i += 1; return True
        if tok.kind == TokenKind.FALSE:
            self.i += 1; return False
        if tok.kind == TokenKind.NULL:
            self.i += 1; return None
        raise ValueError("Invalid value")
