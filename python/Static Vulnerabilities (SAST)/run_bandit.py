#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "bandit"
DEFAULT_REPO_PATH = str(ROOT.parent / "Code Duplication" / "github-actions-cicd-example")
DEFAULT_OUTPUT_PATH = str(ROOT / "bandit_report" / "bandit.json")


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


def install_bandit() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    if not requirements.is_file():
        raise SystemExit(f"Missing requirements file: {requirements}")

    python = create_venv()
    return subprocess.run(
        [python, "-m", "pip", "install", "-r", str(requirements)],
        cwd=str(ROOT),
    ).returncode


def run_bandit(repo: Path, output_path: Path | None, bandit_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    python = resolve_python()
    command = [python, "-m", "bandit", *bandit_args]
    result = subprocess.run(
        command,
        cwd=str(repo),
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")

    if output_path is not None and result.stdout:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stdout = result.stdout
        json_start = stdout.find("{")
        if json_start != -1:
            stdout = stdout[json_start:]
        output_path.write_text(stdout, encoding="utf-8")

    return result.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or run bandit against a provided repo.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("install", help="Install bandit")

    run_parser = subparsers.add_parser("run", help="Run bandit")
    run_parser.add_argument("--repo", help="Target repository path")
    run_parser.add_argument("--output", help="Optional file path for captured stdout")
    run_parser.add_argument(
        "bandit_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed directly to bandit",
    )
    return parser


def normalize_tool_args(args: list[str]) -> list[str]:
    if args and args[0] == "--":
        return args[1:]
    return args


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "install":
        return install_bandit()

    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output_path = Path(args.output).resolve() if args.output else None
    bandit_args = normalize_tool_args(args.bandit_args)
    return run_bandit(repo, output_path, bandit_args)


if __name__ == "__main__":
    raise SystemExit(main())
