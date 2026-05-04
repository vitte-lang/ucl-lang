from ucl_py.lexer import lex
import sys

text = open(sys.argv[1]).read()
for t in lex(text):
    print(t)
