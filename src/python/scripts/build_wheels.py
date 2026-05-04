# =========================================================
# Wheel Builder — MAX ∞
# multi-platform / isolation / cache / sign / verify / publish
# cibuildwheel-like + CI/CD + reproducible
# =========================================================

import os
import sys
import subprocess
import hashlib
import json
import shutil
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict

# ===================== Config =====================

PROJECT_DIR = Path(".").resolve()
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
CACHE_DIR = PROJECT_DIR / ".wheel_cache"

PYTHON_VERSIONS = ["cp39", "cp310", "cp311", "cp312"]
PLATFORMS = ["manylinux_x86_64", "macosx_arm64", "win_amd64"]

SIGN_KEY = os.environ.get("WHEEL_SIGN_KEY", None)
REGISTRY_URL = os.environ.get("WHEEL_REGISTRY", "https://upload.pypi.org/legacy/")

CI_MODE = os.environ.get("CI", "false") == "true"

# ===================== Models =====================

@dataclass
class BuildResult:
    python: str
    platform: str
    wheel: str
    hash: str
    signed: bool


# ===================== Utils =====================

def log(msg: str):
    print(f"[wheel] {msg}")


def run(cmd: List[str], cwd=None):
    log(" ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def ensure_dirs():
    DIST_DIR.mkdir(exist_ok=True)
    BUILD_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)


# ===================== Isolation =====================

def create_venv(python: str, path: Path):
    run([python, "-m", "venv", str(path)])


def install_build_tools(venv: Path):
    pip = venv / "bin" / "pip"
    run([str(pip), "install", "--upgrade", "pip", "build", "wheel", "twine"])


# ===================== Build =====================

def build_wheel(python: str, platform: str) -> Path:
    venv = BUILD_DIR / f"{python}-{platform}"
    if venv.exists():
        shutil.rmtree(venv)

    create_venv(python, venv)
    install_build_tools(venv)

    env = os.environ.copy()
    env["PLATFORM"] = platform

    run([str(venv / "bin" / "python"), "-m", "build", "--wheel"], cwd=PROJECT_DIR)

    wheels = list(DIST_DIR.glob("*.whl"))
    assert wheels, "No wheel produced"
    return wheels[-1]


# ===================== Cache =====================

def cache_key(python: str, platform: str) -> str:
    return hashlib.sha256(f"{python}-{platform}".encode()).hexdigest()


def cache_hit(key: str) -> bool:
    return (CACHE_DIR / key).exists()


def cache_store(key: str):
    (CACHE_DIR / key).write_text("ok")


# ===================== Signing =====================

def sign_wheel(path: Path) -> bool:
    if not SIGN_KEY:
        return False

    sig_path = path.with_suffix(".sig")

    run(["openssl", "dgst", "-sha256", "-sign", SIGN_KEY, "-out", str(sig_path), str(path)])
    return True


def verify_wheel(path: Path):
    sig_path = path.with_suffix(".sig")
    if not sig_path.exists():
        return

    run(["openssl", "dgst", "-sha256", "-verify", SIGN_KEY, "-signature", str(sig_path), str(path)])


# ===================== Publish =====================

def publish_wheel(path: Path):
    run(["twine", "upload", "--repository-url", REGISTRY_URL, str(path)])


# ===================== Pipeline =====================

def build_all() -> List[BuildResult]:
    ensure_dirs()

    results: List[BuildResult] = []

    for py in PYTHON_VERSIONS:
        for plat in PLATFORMS:
            key = cache_key(py, plat)

            if cache_hit(key):
                log(f"cache hit {py}-{plat}")
                continue

            try:
                wheel = build_wheel(py, plat)
                h = hash_file(wheel)

                signed = sign_wheel(wheel)
                verify_wheel(wheel)

                cache_store(key)

                results.append(BuildResult(
                    python=py,
                    platform=plat,
                    wheel=str(wheel),
                    hash=h,
                    signed=signed
                ))

            except Exception as e:
                log(f"FAIL {py}-{plat}: {e}")
                if CI_MODE:
                    sys.exit(1)

    return results


# ===================== Report =====================

def report(results: List[BuildResult]):
    log("=== BUILD REPORT ===")
    for r in results:
        log(f"{r.python} {r.platform} -> {r.wheel}")
        log(f"hash={r.hash} signed={r.signed}")


# ===================== Export =====================

def export(results: List[BuildResult]):
    with open("wheels.json", "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)


# ===================== CI =====================

def ci_publish(results: List[BuildResult]):
    if not CI_MODE:
        return

    for r in results:
        publish_wheel(Path(r.wheel))


# ===================== Entry =====================

def main():
    results = build_all()
    report(results)
    export(results)
    ci_publish(results)


if __name__ == "__main__":
    main()
