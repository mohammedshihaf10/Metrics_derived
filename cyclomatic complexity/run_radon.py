#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "radon"
DEFAULT_REPO_PATH = ""


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
        [sys.executable, "-m", "venv", "--clear", "--without-pip", str(venv_path)],
        check=True,
        cwd=str(ROOT),
        env=build_tool_env(),
    )
    return str(venv_python(TOOL_DIR))


def install_radon() -> int:
    requirements = TOOL_DIR / "requirements.txt"
    if not requirements.is_file():
        raise SystemExit(f"Missing requirements file: {requirements}")

    create_venv()
    packages_dir = TOOL_DIR / "packages"
    if not packages_dir.is_dir():
        raise SystemExit(
            f"Missing packages directory: {packages_dir}. Download the radon wheels first."
        )

    site_packages = venv_site_packages(TOOL_DIR)
    site_packages.mkdir(parents=True, exist_ok=True)
    clear_directory(site_packages)

    wheel_files = sorted(packages_dir.glob("*.whl"))
    if not wheel_files:
        raise SystemExit(f"No wheel files found in: {packages_dir}")

    for wheel_path in wheel_files:
        with zipfile.ZipFile(wheel_path) as wheel:
            wheel.extractall(site_packages)

    return 0


def run_radon(repo: Path, radon_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")

    python = resolve_python()
    command = [python, "-m", "radon", *radon_args]

    # Stream stdout/stderr directly so the tool output is not changed.
    return subprocess.run(command, cwd=str(repo)).returncode


def build_tool_env() -> dict[str, str]:
    temp_dir = TOOL_DIR / ".tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["TMP"] = str(temp_dir)
    env["TEMP"] = str(temp_dir)
    return env


def venv_site_packages(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Lib" / "site-packages"
    version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    return path / ".venv" / "lib" / version / "site-packages"


def clear_directory(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def get_repo_path(repo_arg: str | list[str] | None) -> Path:
    if isinstance(repo_arg, list):
        repo_value = " ".join(repo_arg)
    else:
        repo_value = repo_arg

    repo_value = repo_value or DEFAULT_REPO_PATH
    if not repo_value:
        raise SystemExit(
            "Set DEFAULT_REPO_PATH in run_radon.py or pass --repo with your repository path."
        )
    return Path(repo_value).resolve()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install or run radon against a provided repo."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("install", help="Install radon")

    run_parser = subparsers.add_parser("run", help="Run radon")
    run_parser.add_argument(
        "--repo",
        nargs="+",
        help="Target repository path, for example D:\\Projects\\my-repo",
    )
    run_parser.add_argument(
        "radon_args",
        nargs=argparse.REMAINDER,
        help="Arguments passed directly to radon",
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
        return install_radon()

    if args.command == "run":
        repo = get_repo_path(args.repo)
        radon_args = normalize_tool_args(args.radon_args)
        return run_radon(repo, radon_args)

    parser.error("Unsupported command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
