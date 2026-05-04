# =========================================================
# UCL Version Engine 
# semver / parse / compare / ranges / bump / constraints
# =========================================================

import re
from dataclasses import dataclass
from typing import Optional, List


# ===================== Version =====================

SEMVER_RE = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)"
    r"(?:-([0-9A-Za-z.-]+))?"
    r"(?:\+([0-9A-Za-z.-]+))?$"
)


@dataclass(order=True, frozen=True)
class Version:
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    build: Optional[str] = None

    @staticmethod
    def parse(s: str) -> "Version":
        m = SEMVER_RE.match(s)
        if not m:
            raise ValueError(f"invalid version: {s}")

        return Version(
            major=int(m.group(1)),
            minor=int(m.group(2)),
            patch=int(m.group(3)),
            prerelease=m.group(4),
            build=m.group(5),
        )

    def __str__(self):
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += f"-{self.prerelease}"
        if self.build:
            s += f"+{self.build}"
        return s

    # ---------- bump ----------

    def bump_major(self):
        return Version(self.major + 1, 0, 0)

    def bump_minor(self):
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self):
        return Version(self.major, self.minor, self.patch + 1)

    # ---------- helpers ----------

    def is_prerelease(self):
        return self.prerelease is not None


# ===================== Range =====================

class Range:
    def __init__(self, raw: str):
        self.raw = raw
        self.constraints = self.parse(raw)

    def parse(self, raw: str):
        parts = raw.split()
        constraints = []

        for p in parts:
            if p.startswith(">="):
                constraints.append((">=", Version.parse(p[2:])))
            elif p.startswith("<="):
                constraints.append(("<=", Version.parse(p[2:])))
            elif p.startswith(">"):
                constraints.append((">", Version.parse(p[1:])))
            elif p.startswith("<"):
                constraints.append(("<", Version.parse(p[1:])))
            elif p.startswith("^"):
                v = Version.parse(p[1:])
                constraints.append((">=", v))
                constraints.append(("<", Version(v.major + 1, 0, 0)))
            elif p.startswith("~"):
                v = Version.parse(p[1:])
                constraints.append((">=", v))
                constraints.append(("<", Version(v.major, v.minor + 1, 0)))
            else:
                constraints.append(("==", Version.parse(p)))

        return constraints

    def matches(self, v: Version) -> bool:
        for op, target in self.constraints:
            if op == "==" and v != target:
                return False
            if op == ">=" and v < target:
                return False
            if op == "<=" and v > target:
                return False
            if op == ">" and v <= target:
                return False
            if op == "<" and v >= target:
                return False
        return True


# ===================== Resolver =====================

def max_satisfying(versions: List[str], range_str: str) -> Optional[str]:
    rng = Range(range_str)
    parsed = [Version.parse(v) for v in versions]

    matches = [v for v in parsed if rng.matches(v)]
    if not matches:
        return None

    return str(max(matches))


# ===================== Compare =====================

def compare(v1: str, v2: str) -> int:
    a = Version.parse(v1)
    b = Version.parse(v2)

    if a < b:
        return -1
    if a > b:
        return 1
    return 0


# ===================== Compatibility =====================

def is_compatible(a: str, b: str) -> bool:
    va = Version.parse(a)
    vb = Version.parse(b)

    return va.major == vb.major


# ===================== Sorting =====================

def sort_versions(versions: List[str]) -> List[str]:
    return sorted(versions, key=Version.parse)


# ===================== Example =====================

if __name__ == "__main__":
    v = Version.parse("1.2.3-alpha+001")

    print(v)
    print(v.bump_minor())

    versions = ["1.0.0", "1.2.0", "2.0.0"]
    print(max_satisfying(versions, "^1.0.0"))

    print(compare("1.0.0", "1.2.0"))
    print(is_compatible("1.2.0", "1.3.0"))
