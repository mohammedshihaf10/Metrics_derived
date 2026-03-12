#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "clang_tidy_report" / "cognitive_complexity.txt"
CLANG_TIDY = Path(r"C:\msys64\mingw64\bin\clang-tidy.exe")


def install_tool() -> int:
    return 0 if CLANG_TIDY.is_file() else 1


def run_tool(repo: Path, output_path: Path, tool_args: list[str]) -> int:
    if not CLANG_TIDY.is_file():
        raise SystemExit(f"Missing clang-tidy executable: {CLANG_TIDY}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    args = tool_args or [
        str(repo / "cJSON.c"),
        "--checks=-*,readability-function-cognitive-complexity",
        "--",
        "-I",
        str(repo),
    ]
    result = subprocess.run([str(CLANG_TIDY), *args], cwd=str(repo), capture_output=True, text=True)
    text = result.stdout + result.stderr
    output_path.write_text(text, encoding="utf-8")
    if text:
        print(text, end="")
    return result.returncode


def normalize_tool_args(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def resolve_repo_path(value: str | None) -> Path:
    if value is None:
        return DEFAULT_REPO_PATH.resolve()
    path = Path(value)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("--output")
    run.add_argument("tool_args", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_tool()
    repo = resolve_repo_path(args.repo)
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_tool(repo, output_path, normalize_tool_args(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
