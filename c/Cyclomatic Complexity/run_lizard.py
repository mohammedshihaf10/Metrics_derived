#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "lizard"
DEFAULT_REPO_PATH = str(ROOT.parent / "cJSON")


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def create_venv() -> str:
    tool_python = venv_python(TOOL_DIR)
    if tool_python.is_file():
        return str(tool_python)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(tool_python)


def install_tool() -> int:
    return subprocess.run(
        [create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")],
        cwd=str(ROOT),
    ).returncode


def run_tool(repo: Path, tool_args: list[str]) -> int:
    python = create_venv()
    return subprocess.run([python, "-m", "lizard", *tool_args], cwd=str(repo)).returncode


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.command == "install":
        return install_tool()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    tool_args = args.tool_args[1:] if args.tool_args and args.tool_args[0] == "--" else args.tool_args
    return run_tool(repo, tool_args)


if __name__ == "__main__":
    raise SystemExit(main())
