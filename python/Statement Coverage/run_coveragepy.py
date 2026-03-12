#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "coveragepy"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "github-actions-cicd-example")


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def resolve_python() -> str:
    tool_python = venv_python(TOOL_DIR)
    if tool_python.is_file():
        return str(tool_python)
    return sys.executable


def create_venv() -> str:
    tool_python = venv_python(TOOL_DIR)
    if tool_python.is_file():
        return str(tool_python)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(tool_python)


def install_coverage() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    python = create_venv()
    return subprocess.run([python, "-m", "pip", "install", "-r", str(requirements)], cwd=str(ROOT)).returncode


def run_coverage(repo: Path, args: list[str]) -> int:
    python = resolve_python()
    return subprocess.run([python, "-m", "coverage", *args], cwd=str(repo)).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    runp = sub.add_parser("run")
    runp.add_argument("--repo")
    runp.add_argument("tool_args", nargs=argparse.REMAINDER)
    return parser


def normalize(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "install":
        return install_coverage()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    return run_coverage(repo, normalize(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
