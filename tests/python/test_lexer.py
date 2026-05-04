from ucl_py.lexer import lex

def test_lex():
    assert len(lex('a=1;')) > 0
