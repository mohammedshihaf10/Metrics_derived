#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "cve-bin-tool"
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "cvebin_report" / "cvebin.json"
SITE_PACKAGES = TOOL_DIR / "site-packages"
CACHE_DIR = ROOT / "cvebin_cache"


def install_tool() -> int:
    SITE_PACKAGES.mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--target",
            str(SITE_PACKAGES),
            "-r",
            str(TOOL_DIR / "requirements.txt"),
        ],
        cwd=str(ROOT),
    ).returncode


def run_tool(repo: Path, output_path: Path, tool_args: list[str]) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    args = tool_args or ["-u", "never", "-f", "json", "-o", str(output_path), str(repo)]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SITE_PACKAGES) + os.pathsep + env.get("PYTHONPATH", "")
    env["HOME"] = str(ROOT)
    env["XDG_CACHE_HOME"] = str(CACHE_DIR)
    env["LOCALAPPDATA"] = str(CACHE_DIR)
    env["USERPROFILE"] = str(ROOT)
    env["APPDATA"] = str(CACHE_DIR)
    return subprocess.run([sys.executable, "-m", "cve_bin_tool.cli", *args], cwd=str(ROOT), env=env).returncode


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
        return install_tool()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_tool(repo, output_path, normalize_tool_args(args.tool_args))


if __name__ == "__main__":
    raise SystemExit(main())
