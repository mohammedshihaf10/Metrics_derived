#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "gcovr"
DEFAULT_REPO_PATH = str(ROOT.parent / "cJSON")
REPORT_DIR = ROOT / "gcovr_report"


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


def run_tool(repo: Path, gcovr_args: list[str]) -> int:
    bash = r"C:\msys64\usr\bin\bash.exe"
    build_dir = repo / "build-branch"
    repo_unix = f"/d/Projects/sample\\ repo/c/{repo.name}"
    repo_report = repo / "branch_coverage.info"
    build_cmd = (
        "export PATH=/mingw64/bin:$PATH; "
        f"cd {repo_unix} && rm -rf build-branch && "
        "cmake -S . -B build-branch -DENABLE_CJSON_TEST=On -DENABLE_CUSTOM_COMPILER_FLAGS=Off "
        "-DCMAKE_C_FLAGS=\"--coverage -O0\" "
        "-DCMAKE_EXE_LINKER_FLAGS=\"--coverage\" "
        "-DCMAKE_SHARED_LINKER_FLAGS=\"--coverage\" && "
        "cmake --build build-branch && "
        "ctest --test-dir build-branch --output-on-failure"
    )
    subprocess.run([bash, "-lc", build_cmd], check=True, cwd=str(ROOT))

    REPORT_DIR.mkdir(exist_ok=True)
    report_cmd = (
        "export PATH=/mingw64/bin:$PATH; "
        f"cd {repo_unix} && rm -f branch.info && "
        f"lcov --rc lcov_branch_coverage=1 --capture --directory {build_dir.name} --base-directory . --output-file {repo_report.name}"
    )
    summary_cmd = (
        "export PATH=/mingw64/bin:$PATH; "
        f"cd {repo_unix} && lcov --rc lcov_branch_coverage=1 --summary {repo_report.name}"
    )
    result = subprocess.run([bash, "-lc", report_cmd], cwd=str(ROOT)).returncode
    if result != 0:
        return result
    summary = subprocess.run([bash, "-lc", summary_cmd], cwd=str(ROOT))
    if repo_report.exists():
        target = REPORT_DIR / repo_report.name
        target.write_bytes(repo_report.read_bytes())
        repo_report.unlink()
    return summary.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("gcovr_args", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_tool()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    gcovr_args = args.gcovr_args[1:] if args.gcovr_args and args.gcovr_args[0] == "--" else args.gcovr_args
    return run_tool(repo, gcovr_args)


if __name__ == "__main__":
    raise SystemExit(main())
