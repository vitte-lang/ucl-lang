from ucl_py.lexer import lex
from ucl_py.parser import Parser
import json, sys

text = open(sys.argv[1]).read()
prog = Parser(lex(text)).parse()
open(sys.argv[2], "w").write(str(prog))
