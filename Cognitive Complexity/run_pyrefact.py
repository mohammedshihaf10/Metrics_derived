#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "pyrefact"
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
    subprocess.run([python, "-m", "venv", str(venv_path)], check=True, cwd=str(ROOT))
    return str(venv_python(TOOL_DIR))


def install_pyrefact() -> int:
    python = create_venv()
    return subprocess.run(
        [python, "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")],
        cwd=str(ROOT),
    ).returncode


def run_pyrefact(repo: Path, tool_args: list[str], stdin_file: str | None) -> int:
    python = resolve_python()
    command = [python, "-m", "pyrefact", *tool_args]
    stdin_text = None
    if stdin_file:
        stdin_path = Path(stdin_file)
        if not stdin_path.is_absolute():
            stdin_path = (repo / stdin_path).resolve()
        stdin_text = stdin_path.read_text(encoding="utf-8")
    return subprocess.run(command, cwd=str(repo), input=stdin_text, text=True).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Install or run pyrefact.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("install", help="Install pyrefact")
    run_parser = subparsers.add_parser("run", help="Run pyrefact")
    run_parser.add_argument("--repo", help="Working directory for the command.")
    run_parser.add_argument(
        "--stdin-file",
        help="Optional file to send to pyrefact via stdin when using --from-stdin.",
    )
    run_parser.add_argument("tool_args", nargs=argparse.REMAINDER)
    return parser


def normalize_tool_args(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "install":
        return install_pyrefact()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    return run_pyrefact(repo, normalize_tool_args(args.tool_args), args.stdin_file)


if __name__ == "__main__":
    raise SystemExit(main())
