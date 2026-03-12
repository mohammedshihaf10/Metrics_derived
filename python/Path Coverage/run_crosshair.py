#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "crosshair"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "tool_examples")

def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"

def resolve_python() -> str:
    p = venv_python(TOOL_DIR)
    return str(p) if p.is_file() else sys.executable

def create_venv() -> str:
    p = venv_python(TOOL_DIR)
    if p.is_file():
        return str(p)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(p)

def install_tool() -> int:
    return subprocess.run([create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")], cwd=str(ROOT)).returncode

def run_tool(repo: Path, tool_args: list[str]) -> int:
    return subprocess.run([resolve_python(), "-m", "crosshair", *tool_args], cwd=str(repo)).returncode

def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="command", required=True)
    sp.add_parser("install")
    rp = sp.add_parser("run")
    rp.add_argument("--repo")
    rp.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if args.command == "install":
        return install_tool()
    tool_args = args.tool_args[1:] if args.tool_args and args.tool_args[0] == "--" else args.tool_args
    return run_tool(Path(args.repo or DEFAULT_REPO_PATH).resolve(), tool_args)

if __name__ == "__main__":
    raise SystemExit(main())
