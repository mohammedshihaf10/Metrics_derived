#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "pydriller"
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "pydriller_report" / "code_churn.json"


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def create_venv() -> str:
    python = venv_python(TOOL_DIR)
    if python.is_file():
        return str(python)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(python)


def install_tool() -> int:
    python = create_venv()
    return subprocess.run([python, "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")], cwd=str(ROOT)).returncode


def run_tool(repo: Path, output_path: Path) -> int:
    python = create_venv()
    script = TOOL_DIR / "analyze_churn.py"
    env = dict(os.environ)
    env["GIT_CONFIG_COUNT"] = "1"
    env["GIT_CONFIG_KEY_0"] = "safe.directory"
    env["GIT_CONFIG_VALUE_0"] = str(repo)
    return subprocess.run([python, str(script), str(repo), str(output_path)], cwd=str(ROOT), env=env).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_tool()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_tool(repo, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
