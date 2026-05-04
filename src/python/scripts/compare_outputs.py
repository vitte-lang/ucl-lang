# =========================================================
# Comparator Engine PRO — MAX ∞
# text / json / binary / ast / tolerant / parallel / report
# =========================================================

import json
import hashlib
import difflib
import sys
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Tuple

# ===================== Config =====================

TOLERANCE_FLOAT = 1e-6
IGNORE_WHITESPACE = True
IGNORE_ORDER = True
IGNORE_KEYS = ["timestamp", "id"]
PARALLELISM = 8
FAIL_FAST = False

REPORT_HTML = "compare_report.html"

# ===================== Utils =====================

def log(msg: str):
    print(f"[compare] {msg}")


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def read_bytes(p: Path) -> bytes:
    return p.read_bytes()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ===================== Normalization =====================

def normalize_text(s: str) -> str:
    if IGNORE_WHITESPACE:
        return "\n".join(line.strip() for line in s.splitlines())
    return s


def normalize_json(obj: Any) -> Any:
    if isinstance(obj, dict):
        items = obj.items()
        if IGNORE_ORDER:
            items = sorted(items)
        return {
            k: normalize_json(v)
            for k, v in items
            if k not in IGNORE_KEYS
        }
    elif isinstance(obj, list):
        return [normalize_json(x) for x in obj]
    elif isinstance(obj, float):
        return round(obj, 6)
    return obj


# ===================== Diff =====================

def diff_text(a: str, b: str) -> str:
    return "\n".join(difflib.unified_diff(
        a.splitlines(),
        b.splitlines(),
        fromfile="expected",
        tofile="actual",
        lineterm=""
    ))


# ===================== Compare =====================

def compare_text(a: str, b: str) -> Tuple[bool, str]:
    a_n = normalize_text(a)
    b_n = normalize_text(b)

    if a_n == b_n:
        return True, ""

    return False, diff_text(a_n, b_n)


def compare_json(a: Any, b: Any) -> Tuple[bool, str]:
    na = normalize_json(a)
    nb = normalize_json(b)

    if na == nb:
        return True, ""

    return False, json.dumps({
        "expected": na,
        "actual": nb
    }, indent=2)


def compare_binary(a: bytes, b: bytes) -> Tuple[bool, str]:
    if a == b:
        return True, ""

    return False, f"hash mismatch: {sha256(a)} != {sha256(b)}"


# ===================== Smart Dispatch =====================

def smart_compare(pa: Path, pb: Path) -> Tuple[bool, str]:
    if not pa.exists() or not pb.exists():
        return False, "missing file"

    ext = pa.suffix.lower()

    try:
        if ext == ".json":
            return compare_json(
                json.loads(read_text(pa)),
                json.loads(read_text(pb))
            )

        elif ext in [".txt", ".md", ".ucl", ".dots"]:
            return compare_text(read_text(pa), read_text(pb))

        else:
            return compare_binary(read_bytes(pa), read_bytes(pb))

    except Exception as e:
        return False, f"error: {e}"


# ===================== Directory Compare =====================

def list_files(root: Path) -> List[Path]:
    return sorted(p.relative_to(root) for p in root.rglob("*") if p.is_file())


def compare_file_pair(args) -> Dict[str, Any]:
    root_a, root_b, rel = args
    pa = root_a / rel
    pb = root_b / rel

    ok, diff = smart_compare(pa, pb)

    return {
        "file": str(rel),
        "ok": ok,
        "diff": diff
    }


def compare_dirs(dir_a: Path, dir_b: Path) -> List[Dict[str, Any]]:
    files_a = list_files(dir_a)
    files_b = list_files(dir_b)

    if files_a != files_b:
        return [{
            "file": "__filelist__",
            "ok": False,
            "diff": "file list mismatch"
        }]

    tasks = [(dir_a, dir_b, f) for f in files_a]

    results = []
    with ThreadPoolExecutor(max_workers=PARALLELISM) as pool:
        for r in pool.map(compare_file_pair, tasks):
            results.append(r)
            if not r["ok"] and FAIL_FAST:
                break

    return results


# ===================== Metrics =====================

def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    failed = sum(1 for r in results if not r["ok"])

    return {
        "total": total,
        "failed": failed,
        "passed": total - failed
    }


# ===================== HTML Report =====================

def generate_html(results: List[Dict[str, Any]]):
    rows = []
    for r in results:
        color = "#ccffcc" if r["ok"] else "#ffcccc"
        diff = r["diff"].replace("<", "&lt;").replace(">", "&gt;")
        rows.append(f"""
        <tr style="background:{color}">
          <td>{r['file']}</td>
          <td>{r['ok']}</td>
          <td><pre>{diff}</pre></td>
        </tr>
        """)

    html = f"""
    <html>
    <body>
    <h1>Comparison Report</h1>
    <table border="1">
    <tr><th>File</th><th>Status</th><th>Diff</th></tr>
    {''.join(rows)}
    </table>
    </body>
    </html>
    """

    Path(REPORT_HTML).write_text(html)


# ===================== CI =====================

def ci_check(results: List[Dict[str, Any]]):
    summary = summarize(results)

    log(f"total={summary['total']} failed={summary['failed']}")

    if summary["failed"] > 0:
        sys.exit(1)


# ===================== Entry =====================

def main():
    if len(sys.argv) < 3:
        print("usage: compare_outputs.py <dir_a> <dir_b>")
        sys.exit(1)

    dir_a = Path(sys.argv[1])
    dir_b = Path(sys.argv[2])

    results = compare_dirs(dir_a, dir_b)

    for r in results:
        if not r["ok"]:
            log(f"FAIL {r['file']}")

    generate_html(results)
    ci_check(results)


if __name__ == "__main__":
    main()
