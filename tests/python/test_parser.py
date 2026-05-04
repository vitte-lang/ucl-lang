from ucl_py.lexer import lex
from ucl_py.parser import Parser

def test_parse():
    Parser(lex('a=1;')).parse()
