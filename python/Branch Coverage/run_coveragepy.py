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
    python = create_venv()
    return subprocess.run([python, "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")], cwd=str(ROOT)).returncode


def run_coverage(repo: Path, args: list[str]) -> int:
    return subprocess.run([resolve_python(), "-m", "coverage", *args], cwd=str(repo)).returncode


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="command", required=True)
    s.add_parser("install")
    r = s.add_parser("run")
    r.add_argument("--repo")
    r.add_argument("tool_args", nargs=argparse.REMAINDER)
    return p


def normalize(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def main() -> int:
    args = parser().parse_args()
    if args.command == "install":
        return install_coverage()
    return run_coverage(Path(args.repo or DEFAULT_REPO_PATH).resolve(), normalize(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
