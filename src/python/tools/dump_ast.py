from ucl_py.lexer import lex
from ucl_py.parser import Parser
import sys, pprint

text = open(sys.argv[1]).read()
prog = Parser(lex(text)).parse()
pprint.pp(prog)
