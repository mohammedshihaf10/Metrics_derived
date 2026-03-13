#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "symtable-uses"
DEFAULT_REPO_PATH = str((ROOT.parent / "github-actions-cicd-example").resolve())
DEFAULT_OUTPUT_PATH = str(ROOT / "all_uses_report.json")
def venv_python(path: Path) -> Path:
    return path / ".venv" / ("Scripts" if sys.platform.startswith("win") else "bin") / ("python.exe" if sys.platform.startswith("win") else "python")
def resolve_python() -> str:
    p = venv_python(TOOL_DIR)
    return str(p) if p.is_file() else sys.executable
def create_venv() -> str:
    p = venv_python(TOOL_DIR)
    if p.is_file():
        return str(p)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(p)
def install_tool() -> int:
    return subprocess.run([create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")], cwd=str(ROOT)).returncode
def normalize(args: list[str]) -> list[str]:
    return args[1:] if args and args[0] == "--" else args
def main() -> int:
    ap = argparse.ArgumentParser(description="Install or run coverage.py + symtable against a provided repo.")
    sp = ap.add_subparsers(dest="command", required=True)
    sp.add_parser("install")
    rp = sp.add_parser("run")
    rp.add_argument("--repo")
    rp.add_argument("--output")
    rp.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if args.command == "install":
        return install_tool()
    repo = Path(args.repo or DEFAULT_REPO_PATH).resolve()
    output = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return subprocess.run([resolve_python(), str(TOOL_DIR / "analyze_uses.py"), str(repo), str(output), *normalize(args.tool_args)], cwd=str(ROOT)).returncode
if __name__ == "__main__":
    raise SystemExit(main())
