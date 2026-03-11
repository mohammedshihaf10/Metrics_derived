#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "pyflowchart"
DEFAULT_REPO_PATH = str(ROOT)
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
    subprocess.run(
        [python, "-m", "venv", str(venv_path)],
        check=True,
        cwd=str(ROOT),
    )
    return str(venv_python(TOOL_DIR))


def install_pyflowchart() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    if not requirements.is_file():
        raise SystemExit(f"Missing requirements file: {requirements}")

    python = create_venv()
    command = [python, "-m", "pip", "install", "-r", str(requirements)]
    return subprocess.run(command, cwd=str(ROOT)).returncode


def run_pyflowchart(repo: Path, tool_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    python = resolve_python()
    command = [python, "-m", "pyflowchart", *tool_args]
    return subprocess.run(command, cwd=str(repo)).returncode


def get_repo_path(repo_arg: str | None) -> Path:
    repo_value = repo_arg or DEFAULT_REPO_PATH
    return Path(repo_value).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install or run pyflowchart against a provided repo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install", help="Install pyflowchart")

    run_parser = subparsers.add_parser("run", help="Run pyflowchart")
    run_parser.add_argument(
        "--repo",
        help="Working directory for the command.",
    )
    run_parser.add_argument(
        "tool_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed directly to pyflowchart",
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
        return install_pyflowchart()

    if args.command == "run":
        repo = get_repo_path(args.repo)
        tool_args = normalize_tool_args(args.tool_args)
        return run_pyflowchart(repo, tool_args)

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
