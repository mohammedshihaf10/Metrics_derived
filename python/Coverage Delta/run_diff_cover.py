#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "diff-cover"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "github-actions-cicd-example")


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def create_venv() -> str:
    p = venv_python(TOOL_DIR)
    if p.is_file():
        return str(p)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(p)


def install_tool() -> int:
    return subprocess.run(
        [create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")],
        cwd=str(ROOT),
    ).returncode


def run_tool(repo: Path, tool_args: list[str]) -> int:
    python = create_venv()
    subprocess.run([python, "-m", "coverage", "erase"], cwd=str(repo), check=True)
    subprocess.run([python, "-m", "coverage", "run", "-m", "pytest"], cwd=str(repo), check=True)
    subprocess.run([python, "-m", "coverage", "xml", "-o", "coverage_delta.xml"], cwd=str(repo), check=True)

    if sys.platform.startswith("win"):
        diff_cover = TOOL_DIR / ".venv" / "Scripts" / "diff-cover.exe"
    else:
        diff_cover = TOOL_DIR / ".venv" / "bin" / "diff-cover"
    return subprocess.run([str(diff_cover), "coverage_delta.xml", *tool_args], cwd=str(repo)).returncode


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

    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    tool_args = args.tool_args[1:] if args.tool_args and args.tool_args[0] == "--" else args.tool_args
    return run_tool(repo, tool_args)


if __name__ == "__main__":
    raise SystemExit(main())
