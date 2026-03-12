#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOL_DIR = ROOT / "tools" / "defuse-combo"
DEFAULT_REPO_PATH = str(ROOT.parent / "Cyclomatic Complexity" / "github-actions-cicd-example")


def venv_python(path: Path) -> Path:
    if sys.platform.startswith("win"):
        return path / ".venv" / "Scripts" / "python.exe"
    return path / ".venv" / "bin" / "python"


def create_venv() -> str:
    p = venv_python(TOOL_DIR)
    if p.is_file():
        return str(p)
    subprocess.run([sys.executable, "-m", "venv", str(TOOL_DIR / ".venv")], check=True, cwd=str(ROOT))
    return str(p)


def install_tool() -> int:
    return subprocess.run(
        [create_venv(), "-m", "pip", "install", "-r", str(TOOL_DIR / "requirements.txt")],
        cwd=str(ROOT),
    ).returncode


def function_ranges(tree: ast.AST) -> list[tuple[str, int, int]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end_lineno = max(getattr(n, "lineno", node.lineno) for n in ast.walk(node))
            out.append((node.name, node.lineno, end_lineno))
    return sorted(out, key=lambda x: x[1])


def enclosing_function(lineno: int, ranges: list[tuple[str, int, int]]) -> str:
    for name, start, end in ranges:
        if start <= lineno <= end:
            return name
    return "<module>"


class DefUseCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.defs: list[dict[str, object]] = []
        self.uses: list[dict[str, object]] = []
        self._predicate_lines: set[int] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args:
            self.defs.append({"name": arg.arg, "lineno": arg.lineno})
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._record_target(target)
        self.generic_visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record_target(node.target)
        if node.value:
            self.generic_visit(node.value)

    def visit_For(self, node: ast.For) -> None:
        self._record_target(node.target)
        self._predicate_lines.add(node.lineno)
        self.generic_visit(node.iter)
        for child in node.body:
            self.visit(child)
        for child in node.orelse:
            self.visit(child)

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                self._record_target(item.optional_vars)
            self.visit(item.context_expr)
        for child in node.body:
            self.visit(child)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            kind = "p-use" if node.lineno in self._predicate_lines else "c-use"
            self.uses.append({"name": node.id, "lineno": node.lineno, "use_kind": kind})

    def visit_If(self, node: ast.If) -> None:
        self._predicate_lines.add(node.lineno)
        self.visit(node.test)
        for child in node.body:
            self.visit(child)
        for child in node.orelse:
            self.visit(child)

    def _record_target(self, target: ast.AST) -> None:
        if isinstance(target, ast.Name):
            self.defs.append({"name": target.id, "lineno": target.lineno})
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._record_target(elt)


def analyze(repo: Path) -> dict[str, object]:
    target = repo / "actionscicd" / "somecode.py"
    coverage_json = repo / "defuse_coverage.json"

    python = create_venv()
    subprocess.run([python, "-m", "coverage", "erase"], cwd=str(repo), check=True)
    subprocess.run([python, "-m", "coverage", "run", "-m", "pytest"], cwd=str(repo), check=True)
    subprocess.run([python, "-m", "coverage", "json", "-o", str(coverage_json.name)], cwd=str(repo), check=True)

    data = json.loads(coverage_json.read_text(encoding="utf-8"))
    covered_lines = set(data["files"]["actionscicd\\somecode.py"]["executed_lines"])
    missing_lines = set(data["files"]["actionscicd\\somecode.py"]["missing_lines"])

    tree = ast.parse(target.read_text(encoding="utf-8"))
    ranges = function_ranges(tree)
    collector = DefUseCollector()
    collector.visit(tree)

    defs = []
    for item in collector.defs:
        entry = dict(item)
        entry["scope"] = enclosing_function(int(entry["lineno"]), ranges)
        entry["covered"] = int(entry["lineno"]) in covered_lines
        defs.append(entry)

    uses = []
    for item in collector.uses:
        entry = dict(item)
        entry["scope"] = enclosing_function(int(entry["lineno"]), ranges)
        entry["covered"] = int(entry["lineno"]) in covered_lines
        uses.append(entry)

    defs_by_scope_name: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for d in defs:
        defs_by_scope_name[(str(d["scope"]), str(d["name"]))].append(d)
    for lst in defs_by_scope_name.values():
        lst.sort(key=lambda x: int(x["lineno"]))

    pairs = []
    for u in uses:
        key = (str(u["scope"]), str(u["name"]))
        candidates = [d for d in defs_by_scope_name.get(key, []) if int(d["lineno"]) <= int(u["lineno"])]
        if candidates:
            d = candidates[-1]
            pairs.append(
                {
                    "scope": u["scope"],
                    "name": u["name"],
                    "def_line": d["lineno"],
                    "use_line": u["lineno"],
                    "use_kind": u["use_kind"],
                    "covered_pair": bool(d["covered"]) and bool(u["covered"]),
                }
            )

    covered_pairs = [p for p in pairs if p["covered_pair"]]
    c_use_pairs = [p for p in covered_pairs if p["use_kind"] == "c-use"]
    p_use_pairs = [p for p in covered_pairs if p["use_kind"] == "p-use"]
    uncovered_uses = [p for p in pairs if not p["covered_pair"]]

    return {
        "file": str(target),
        "covered_lines": sorted(covered_lines),
        "missing_lines": sorted(missing_lines),
        "definitions_total": len(defs),
        "uses_total": len(uses),
        "definition_use_pairs_total": len(pairs),
        "covered_definition_use_pairs": len(covered_pairs),
        "c_use_pairs": len(c_use_pairs),
        "p_use_pairs": len(p_use_pairs),
        "definition_use_pairs": pairs,
        "uncovered_definition_use_pairs": uncovered_uses,
    }


def run_tool(repo: Path) -> int:
    result = analyze(repo)
    out = ROOT / "all_uses_report.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="command", required=True)
    sp.add_parser("install")
    rp = sp.add_parser("run")
    rp.add_argument("--repo")
    args = ap.parse_args()
    if args.command == "install":
        return install_tool()
    return run_tool(Path(args.repo or DEFAULT_REPO_PATH).resolve())


if __name__ == "__main__":
    raise SystemExit(main())
