#!/usr/bin/env python
"""Coverage measured on the CHANGED surface, which is what the gate actually requires.

`.evals/config.json` declares `scope: "changed-files"`, and SH-LOOP-1's exit criterion is
"coverage on new/changed code >= unitTestCoverageMin". A whole-module figure is the wrong
measurement on a brownfield repo that started at 0% coverage: it charges this work unit for every
pre-existing untested line it never touched.

This script intersects the added/modified executable lines from `git diff` with coverage.py's own
per-line data, and reports both figures so the pre-existing shortfall stays visible rather than
being hidden.

Usage: changed-line-coverage.py <base-sha> <coverage-json> [path-prefix ...]
Exit 0 if changed-line coverage >= unitTestCoverageMin, else 1.
"""

import json
import io
import re
import subprocess
import sys


def added_lines(base_sha: str, prefixes: tuple[str, ...]) -> dict[str, set[int]]:
    """Line numbers added or modified in the working tree relative to base_sha."""
    out = subprocess.check_output(
        ["git", "diff", "-U0", base_sha, "--"] + list(prefixes),
        text=True,
        errors="replace",
    )
    result: dict[str, set[int]] = {}
    current: str | None = None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:].strip()
            result.setdefault(current, set())
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start = int(m.group(1))
                count = 1 if m.group(2) is None else int(m.group(2))
                result[current].update(range(start, start + count))
    return result


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    base_sha, cov_path = sys.argv[1], sys.argv[2]
    prefixes = tuple(sys.argv[3:]) or ("src/backend",)

    threshold = json.load(io.open(".evals/config.json", encoding="utf-8"))["thresholds"][
        "unitTestCoverageMin"
    ]
    cov = json.load(io.open(cov_path, encoding="utf-8"))

    diff = added_lines(base_sha, prefixes)

    total_changed = 0
    covered_changed = 0
    uncovered: list[str] = []

    for cov_file, data in cov.get("files", {}).items():
        norm = cov_file.replace("\\", "/")
        match = next((d for d in diff if norm.endswith(d) or d.endswith(norm)), None)
        if match is None:
            continue

        executed = set(data.get("executed_lines", []))
        missing = set(data.get("missing_lines", []))
        executable = executed | missing
        changed_executable = executable & diff[match]

        total_changed += len(changed_executable)
        covered_changed += len(changed_executable & executed)
        for ln in sorted(changed_executable & missing):
            uncovered.append(f"{norm}:{ln}")

    whole = cov.get("totals", {}).get("percent_covered", 0.0)
    pct = 100.0 if total_changed == 0 else round(covered_changed / total_changed * 100, 2)

    print("Coverage on the CHANGED surface")
    print("  scope                : changed-files (per .evals/config.json)")
    print(f"  base                 : {base_sha[:12]}")
    print(f"  changed executable   : {total_changed} line(s)")
    print(f"  covered              : {covered_changed} line(s)")
    print(f"  changed-line coverage: {pct}%")
    print(f"  threshold            : {threshold}% (unitTestCoverageMin)")
    print()
    print(f"  whole-module coverage: {round(whole, 2)}%  <- includes pre-existing untested code")
    if uncovered:
        print()
        print("  UNCOVERED changed lines:")
        for u in uncovered:
            print(f"    - {u}")

    ok = pct >= threshold
    print()
    print(f"  VERDICT: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
