from dataclasses import dataclass
from enum import Enum, auto

class TokenKind(Enum):
    IDENT = auto()
    NUMBER = auto()
    STRING = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACK = auto()
    RBRACK = auto()
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()
    COMMA = auto()
    COLON = auto()
    SEMI = auto()
    EQ = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    EOF = auto()

@dataclass
class Token:
    kind: TokenKind
    value: str
    pos: int
