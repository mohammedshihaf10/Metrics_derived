#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "jscpd"
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "jscpd_report"


def jscpd_cmd() -> Path:
    if sys.platform.startswith("win"):
        return TOOL_DIR / "node_modules" / ".bin" / "jscpd.cmd"
    return TOOL_DIR / "node_modules" / ".bin" / "jscpd"


def require_node() -> None:
    subprocess.run(["node", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def install_jscpd() -> int:
    require_node()
    return subprocess.run(["npm.cmd", "install"], cwd=str(TOOL_DIR)).returncode


def prepare_output_dir(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def run_jscpd(repo: Path, output_dir: Path, tool_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")
    require_node()
    cmd = jscpd_cmd()
    if not cmd.is_file():
        raise FileNotFoundError(f"Missing jscpd executable: {cmd}")
    prepare_output_dir(output_dir)
    args = tool_args or [
        "--min-lines",
        "5",
        "--pattern",
        "**/*.{c,h}",
        ".",
    ]
    return subprocess.run([str(cmd), "--output", str(output_dir), *args], cwd=str(repo)).returncode


def normalize_tool_args(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("--output")
    run.add_argument("tool_args", nargs=argparse.REMAINDER)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_jscpd()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output_dir = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_jscpd(repo, output_dir, normalize_tool_args(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
