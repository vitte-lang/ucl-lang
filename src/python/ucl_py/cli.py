import sys
from .lexer import lex
from .parser import Parser
from .evaluator import evaluate
from .convert_json import to_json

def main(argv=None):
    argv = argv or sys.argv
    if len(argv) < 3:
        print("ucl <cmd> <file>")
        return 1
    cmd, path = argv[1], argv[2]
    text = open(path).read()
    prog = Parser(lex(text)).parse()
    if cmd == "eval":
        print(evaluate(prog))
    elif cmd == "json":
        print(to_json(evaluate(prog)))
    else:
        print("unknown")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
