#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "complexipy"
DEFAULT_REPO_PATH = str(ROOT / "github-actions-cicd-example")
BOOTSTRAP_PYTHONS = [
    Path(r"C:\Users\moham\AppData\Local\Programs\Python\Python313\python.exe"),
    Path(r"C:\Users\moham\AppData\Local\Programs\Python\Python312\python.exe"),
]


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def find_bootstrap_python() -> str:
    for candidate in BOOTSTRAP_PYTHONS:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def resolve_python() -> str:
    tool_python = venv_python(TOOL_DIR)
    if tool_python.is_file():
        return str(tool_python)
    return find_bootstrap_python()


def create_venv() -> str:
    python = resolve_python()
    if python != find_bootstrap_python():
        return python
    venv_path = TOOL_DIR / ".venv"
    subprocess.run([python, "-m", "venv", str(venv_path)], check=True, cwd=str(ROOT))
    return str(venv_python(TOOL_DIR))


def install_complexipy() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    python = create_venv()
    return subprocess.run(
        [python, "-m", "pip", "install", "-r", str(requirements)],
        cwd=str(ROOT),
    ).returncode


def run_complexipy(repo: Path, tool_args: list[str]) -> int:
    if sys.platform.startswith("win"):
        command = [str(TOOL_DIR / ".venv" / "Scripts" / "complexipy.exe"), *tool_args]
    else:
        python = resolve_python()
        command = [python, "-m", "complexipy", *tool_args]
    return subprocess.run(command, cwd=str(repo)).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or run complexipy.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("install", help="Install complexipy")
    run_parser = subparsers.add_parser("run", help="Run complexipy")
    run_parser.add_argument("--repo", help="Working directory for the command.")
    run_parser.add_argument("tool_args", nargs=argparse.REMAINDER)
    return parser


def normalize_tool_args(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "install":
        return install_complexipy()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    return run_complexipy(repo, normalize_tool_args(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
