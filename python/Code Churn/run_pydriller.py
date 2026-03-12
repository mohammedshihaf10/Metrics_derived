#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "pydriller"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "github-actions-cicd-example")
DEFAULT_OUTPUT_PATH = str(ROOT / "pydriller_report" / "code_churn.json")


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

    subprocess.run(
        [sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")],
        check=True,
        cwd=str(ROOT),
    )
    return str(tool_python)


def install_pydriller() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    if not requirements.is_file():
        raise SystemExit(f"Missing requirements file: {requirements}")

    python = create_venv()
    return subprocess.run(
        [python, "-m", "pip", "install", "-r", str(requirements)],
        cwd=str(ROOT),
    ).returncode


def run_pydriller(repo: Path, output_path: Path) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    python = resolve_python()
    script = ROOT / "tools" / "pydriller" / "analyze_churn.py"
    command = [python, str(script), str(repo), str(output_path)]
    return subprocess.run(command, cwd=str(ROOT)).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or run pydriller churn analysis against a provided repo.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("install", help="Install pydriller")

    run_parser = subparsers.add_parser("run", help="Run pydriller churn analysis")
    run_parser.add_argument("--repo", help="Target repository path")
    run_parser.add_argument("--output", help="Output JSON path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "install":
        return install_pydriller()

    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_pydriller(repo, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
