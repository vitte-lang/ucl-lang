from ucl_py.lexer import lex
from ucl_py.parser import Parser
from ucl_py.evaluator import evaluate

def test_eval():
    p = Parser(lex('a=1;')).parse()
    assert evaluate(p)
