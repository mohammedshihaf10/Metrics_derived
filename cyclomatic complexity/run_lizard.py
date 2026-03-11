#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "lizard"
DEFAULT_REPO_PATH = r"D:\Projects\sample repo\github-actions-cicd-example"


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
    python = resolve_python()
    if python != sys.executable:
        return python

    venv_path = TOOL_DIR / ".venv"
    subprocess.run(
        [sys.executable, "-m", "venv", str(venv_path)],
        check=True,
        cwd=str(ROOT),
    )
    return str(venv_python(TOOL_DIR))


def install_lizard() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    if not requirements.is_file():
        raise SystemExit(f"Missing requirements file: {requirements}")

    python = create_venv()
    command = [python, "-m", "pip", "install", "-r", str(requirements)]
    return subprocess.run(command, cwd=str(ROOT)).returncode


def run_lizard(repo: Path, lizard_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    python = resolve_python()
    command = [python, "-m", "lizard", *lizard_args]

    # Stream stdout/stderr directly so the tool output is not changed.
    return subprocess.run(command, cwd=str(repo)).returncode


def get_repo_path(repo_arg: str | None) -> Path:
    repo_value = repo_arg or DEFAULT_REPO_PATH
    if not repo_value:
        raise SystemExit(
            "Set DEFAULT_REPO_PATH in run_lizard.py or pass --repo with your repository path."
        )
    return Path(repo_value).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install or run lizard against a provided repo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install", help="Install lizard")

    run_parser = subparsers.add_parser("run", help="Run lizard")
    run_parser.add_argument(
        "--repo",
        help="Target repository path, for example D:\\Projects\\my-repo",
    )
    run_parser.add_argument(
        "lizard_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed directly to lizard",
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
        return install_lizard()

    if args.command == "run":
        repo = get_repo_path(args.repo)
        lizard_args = normalize_tool_args(args.lizard_args)
        return run_lizard(repo, lizard_args)

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
