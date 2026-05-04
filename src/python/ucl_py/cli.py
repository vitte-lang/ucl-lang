# =========================================================
# UCL CLI — MAX ∞
# parse / eval / validate / lint / format / run / repl
# plugins / CI / extensible
# =========================================================

import argparse
import sys
import json
from pathlib import Path

# hypothetical internal modules
from ucl_py import parser, evaluator, formatter, linter, ast as ucl_ast

# ===================== Utils =====================

def log(msg: str):
    print(f"[ucl] {msg}")


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ===================== Core Commands =====================

def cmd_parse(args):
    code = read_file(Path(args.file))
    tree = parser.parse(code)
    print(json.dumps(ucl_ast.to_dict(tree), indent=2))


def cmd_eval(args):
    code = read_file(Path(args.file))
    tree = parser.parse(code)
    result = evaluator.eval(tree)
    print(json.dumps(result, indent=2))


def cmd_validate(args):
    code = read_file(Path(args.file))
    tree = parser.parse(code)

    v = ucl_ast.Validator()
    tree.accept(v)

    if v.errors:
        print(json.dumps(v.errors, indent=2))
        sys.exit(1)
    else:
        log("valid")


def cmd_format(args):
    code = read_file(Path(args.file))
    out = formatter.format(code)
    print(out)


def cmd_lint(args):
    issues = linter.run(Path(args.file))

    for i in issues:
        print(f"{i['file']}:{i['line']} {i['msg']}")

    if any(i["severity"] == "error" for i in issues):
        sys.exit(1)


def cmd_run(args):
    code = read_file(Path(args.file))
    tree = parser.parse(code)
    result = evaluator.eval(tree)
    print(result)


# ===================== REPL =====================

def repl():
    log("UCL REPL (type 'exit')")
    while True:
        try:
            line = input("ucl> ")
            if line.strip() in ["exit", "quit"]:
                break

            tree = parser.parse(line)
            result = evaluator.eval(tree)
            print(result)

        except Exception as e:
            print("error:", e)


# ===================== CI =====================

def cmd_ci(args):
    files = list(Path(".").glob("**/*.ucl"))
    failed = False

    for f in files:
        try:
            code = read_file(f)
            tree = parser.parse(code)

            v = ucl_ast.Validator()
            tree.accept(v)

            if v.errors:
                log(f"invalid {f}")
                failed = True

        except Exception:
            log(f"parse error {f}")
            failed = True

    if failed:
        sys.exit(1)

    log("CI OK")


# ===================== Plugins =====================

PLUGINS = {}

def register_plugin(name, fn):
    PLUGINS[name] = fn


def cmd_plugin(args):
    if args.name not in PLUGINS:
        log("plugin not found")
        return

    PLUGINS[args.name](args)


# ===================== CLI =====================

def build_cli():
    p = argparse.ArgumentParser(prog="ucl", description="UCL CLI")

    sub = p.add_subparsers(dest="cmd")

    # parse
    sp = sub.add_parser("parse")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_parse)

    # eval
    sp = sub.add_parser("eval")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_eval)

    # validate
    sp = sub.add_parser("validate")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_validate)

    # format
    sp = sub.add_parser("format")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_format)

    # lint
    sp = sub.add_parser("lint")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_lint)

    # run
    sp = sub.add_parser("run")
    sp.add_argument("file")
    sp.set_defaults(func=cmd_run)

    # repl
    sp = sub.add_parser("repl")
    sp.set_defaults(func=lambda args: repl())

    # ci
    sp = sub.add_parser("ci")
    sp.set_defaults(func=cmd_ci)

    # plugin
    sp = sub.add_parser("plugin")
    sp.add_argument("name")
    sp.set_defaults(func=cmd_plugin)

    return p


# ===================== Entry =====================

def main():
    parser_cli = build_cli()
    args = parser_cli.parse_args()

    if not args.cmd:
        parser_cli.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
