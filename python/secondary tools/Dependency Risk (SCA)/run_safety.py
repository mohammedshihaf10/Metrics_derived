#!/usr/bin/env python3
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "safety"
DEFAULT_REPO_PATH = r"D:\Projects\Metrics_derived\python\Cyclomatic Complexity\github-actions-cicd-example"
DEFAULT_OUTPUT_PATH = str(ROOT / "safety_report.json")
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
def run_tool(repo: Path, output_path: Path | None, tool_args: list[str]) -> int:
    if not repo.is_dir():
        raise SystemExit(f"Repo path does not exist or is not a directory: {repo}")
    result = subprocess.run([resolve_python(), "-m", "safety", *tool_args], cwd=str(repo), capture_output=True, text=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    if output_path is not None and result.stdout:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.stdout, encoding="utf-8")
    return result.returncode
def main() -> int:
    ap = argparse.ArgumentParser(description="Install or run safety against a provided repo.")
    sp = ap.add_subparsers(dest="command", required=True)
    sp.add_parser("install")
    rp = sp.add_parser("run")
    rp.add_argument("--repo")
    rp.add_argument("--output")
    rp.add_argument("tool_args", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    if args.command == "install":
        return install_tool()
    return run_tool(Path(args.repo or DEFAULT_REPO_PATH).resolve(), Path(args.output or DEFAULT_OUTPUT_PATH).resolve(), normalize(args.tool_args))
if __name__ == "__main__":
    raise SystemExit(main())
