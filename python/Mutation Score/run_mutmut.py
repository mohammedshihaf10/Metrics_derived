#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "mutmut"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "github-actions-cicd-example")
DEFAULT_CONFIG_PATH = ROOT / "cosmic_ray.toml"
DEFAULT_SESSION_PATH = ROOT / "cosmic_ray.sqlite"

def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"

def resolve_python() -> str:
    p = venv_python(TOOL_DIR)
    return str(p) if p.is_file() else sys.executable

def create_venv() -> str:
    p = venv_python(TOOL_DIR)
    if p.is_file():
        return str(p)
    if sys.platform.startswith("win"):
        subprocess.run(["py", "-3.10", "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    else:
        subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(p)

def install_tool() -> int:
    return subprocess.run([create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")], cwd=str(ROOT)).returncode

def run_tool(repo: Path, tool_args: list[str]) -> int:
    if sys.platform.startswith("win"):
        cmd = TOOL_DIR / ".venv" / "Scripts" / "cosmic-ray.exe"
        venv_py = TOOL_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        cmd = TOOL_DIR / ".venv" / "bin" / "cosmic-ray"
        venv_py = TOOL_DIR / ".venv" / "bin" / "python"

    test_command = f'"{venv_py}" -m pytest -q'
    config_text = "\n".join(
        [
            "[cosmic-ray]",
            f'module-path = "{(repo / "actionscicd" / "somecode.py").as_posix()}"',
            "timeout = 20.0",
            "excluded-modules = []",
            f'test-command = {test_command!r}',
            "",
            "[cosmic-ray.distributor]",
            'name = "local"',
            "",
        ]
    )
    DEFAULT_CONFIG_PATH.write_text(config_text, encoding="utf-8")
    if DEFAULT_SESSION_PATH.exists():
        DEFAULT_SESSION_PATH.unlink()

    init_rc = subprocess.run([str(cmd), "init", str(DEFAULT_CONFIG_PATH), str(DEFAULT_SESSION_PATH)], cwd=str(repo)).returncode
    if init_rc != 0:
        return init_rc
    exec_rc = subprocess.run([str(cmd), "exec", str(DEFAULT_CONFIG_PATH), str(DEFAULT_SESSION_PATH)], cwd=str(repo)).returncode
    if exec_rc != 0:
        return exec_rc
    return subprocess.run([str(cmd), "dump", str(DEFAULT_SESSION_PATH)], cwd=str(repo)).returncode

def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="command", required=True)
    sp.add_parser("install")
    rp = sp.add_parser("run")
    rp.add_argument("--repo")
    rp.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if args.command == "install":
        return install_tool()
    tool_args = args.tool_args[1:] if args.tool_args and args.tool_args[0] == "--" else args.tool_args
    return run_tool(Path(args.repo or DEFAULT_REPO_PATH).resolve(), tool_args)

if __name__ == "__main__":
    raise SystemExit(main())
