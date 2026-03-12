#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "coverage_delta_report" / "coverage_delta.json"
STATEMENT_RUNNER = ROOT.parent / "Statement Coverage" / "run_gcovr.py"
STATEMENT_INFO = ROOT.parent / "Statement Coverage" / "gcovr_report" / "statement_coverage.info"


def safe_git_env(repo: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "safe.directory"
    env["GIT_CONFIG_VALUE_0"] = str(repo)
    return env


def install_tool() -> int:
    return 0


def resolve_repo_path(value: str | None) -> Path:
    if value is None:
        return DEFAULT_REPO_PATH.resolve()
    path = Path(value)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def ensure_statement_report(repo: Path) -> None:
    if STATEMENT_INFO.is_file():
        return
    subprocess.run(
        ["py", "-3.12", str(STATEMENT_RUNNER), "run", "--repo", str(repo)],
        check=True,
        cwd=str(ROOT),
    )


def normalize_file_name(path_text: str) -> str:
    text = path_text.replace("\\", "/")
    name = Path(text).name
    if name:
        return name
    return text


def parse_lcov_hits(info_path: Path) -> dict[str, set[int]]:
    hits: dict[str, set[int]] = {}
    current = None
    for raw_line in info_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw_line.startswith("SF:"):
            current = normalize_file_name(raw_line[3:])
            hits.setdefault(current, set())
        elif raw_line.startswith("DA:") and current is not None:
            line_no, count = raw_line[3:].split(",", 1)
            if int(count) > 0:
                hits[current].add(int(line_no))
    return hits


def parse_diff_changed_lines(repo: Path, base_ref: str, head_ref: str) -> dict[str, set[int]]:
    result = subprocess.run(
        ["git", "-C", str(repo), "diff", "--unified=0", base_ref, head_ref],
        check=True,
        capture_output=True,
        text=True,
        env=safe_git_env(repo),
    )
    changed: dict[str, set[int]] = {}
    current = None
    hunk_re = re.compile(r"^\@\@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? \@\@")
    for line in result.stdout.splitlines():
        if line.startswith("+++ b/"):
            current = normalize_file_name(line[6:])
            changed.setdefault(current, set())
            continue
        match = hunk_re.match(line)
        if current is None or match is None:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        if count == 0:
            continue
        for line_no in range(start, start + count):
            changed[current].add(line_no)
    return changed


def run_tool(repo: Path, output_path: Path, base_ref: str, head_ref: str) -> int:
    ensure_statement_report(repo)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    coverage_hits = parse_lcov_hits(STATEMENT_INFO)
    changed = parse_diff_changed_lines(repo, base_ref, head_ref)
    files = []
    total_changed = 0
    total_covered = 0
    for path_name in sorted(changed):
        changed_lines = changed[path_name]
        covered_lines = coverage_hits.get(path_name, set()) & changed_lines
        files.append(
            {
                "path": path_name,
                "changed_lines": sorted(changed_lines),
                "changed_line_count": len(changed_lines),
                "covered_changed_lines": sorted(covered_lines),
                "covered_changed_line_count": len(covered_lines),
            }
        )
        total_changed += len(changed_lines)
        total_covered += len(covered_lines)
    percent = 0.0 if total_changed == 0 else round((total_covered / total_changed) * 100.0, 2)
    payload = {
        "base_ref": base_ref,
        "head_ref": head_ref,
        "changed_files": len(files),
        "changed_lines": total_changed,
        "covered_changed_lines": total_covered,
        "diff_coverage_percent": percent,
        "files": files,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("--output")
    run.add_argument("--base-ref", default="HEAD~1")
    run.add_argument("--head-ref", default="HEAD")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_tool()
    repo = resolve_repo_path(args.repo)
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_tool(repo, output_path, args.base_ref, args.head_ref)


if __name__ == "__main__":
    raise SystemExit(main())
