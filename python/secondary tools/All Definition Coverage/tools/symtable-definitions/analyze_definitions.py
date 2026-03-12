from __future__ import annotations

import ast
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


def ranges(tree: ast.AST) -> list[tuple[str, int, int]]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end = max(getattr(child, "lineno", node.lineno) for child in ast.walk(node))
            out.append((node.name, node.lineno, end))
    return sorted(out, key=lambda item: item[1])


def scope(line: int, items: list[tuple[str, int, int]]) -> str:
    for name, start, end in items:
        if start <= line <= end:
            return name
    return "<module>"


class Collector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.defs: list[dict[str, object]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.defs.append({"name": node.name, "lineno": node.lineno, "kind": "function"})
        for arg in node.args.args:
            self.defs.append({"name": arg.arg, "lineno": arg.lineno, "kind": "parameter"})
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defs.append({"name": target.id, "lineno": target.lineno, "kind": "assignment"})
        self.generic_visit(node.value)


repo = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
target = repo / "actionscicd" / "somecode.py"
coverage_json = repo / "secondary_definitions_coverage.json"

subprocess.run([sys.executable, "-m", "coverage", "erase"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "json", "-o", coverage_json.name], cwd=str(repo), check=True)

data = json.loads(coverage_json.read_text(encoding="utf-8"))
file_key = next(key for key in data["files"] if key.endswith("actionscicd\\somecode.py") or key.endswith("actionscicd/somecode.py"))
covered = set(data["files"][file_key]["executed_lines"])

tree = ast.parse(target.read_text(encoding="utf-8"))
item_ranges = ranges(tree)
collector = Collector()
collector.visit(tree)

defs: list[dict[str, object]] = []
defs_by_name: dict[tuple[str, str], list[int]] = defaultdict(list)
for item in collector.defs:
    entry = dict(item)
    entry["scope"] = scope(int(entry["lineno"]), item_ranges)
    entry["covered"] = int(entry["lineno"]) in covered
    defs.append(entry)
    defs_by_name[(str(entry["scope"]), str(entry["name"]))].append(int(entry["lineno"]))

uses = []
for node in ast.walk(tree):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        node_scope = scope(node.lineno, item_ranges)
        candidates = [line for line in defs_by_name.get((node_scope, node.id), []) if line <= node.lineno]
        if candidates:
            uses.append({"name": node.id, "lineno": node.lineno, "scope": node_scope, "covered": node.lineno in covered, "def_line": candidates[-1]})

covered_defs = {(item["scope"], item["name"], item["def_line"]) for item in uses if item["covered"]}
report = {
    "file": str(target),
    "covered_lines": sorted(covered),
    "definitions_total": len(defs),
    "definitions_covered": sum(1 for item in defs if item["covered"]),
    "definitions_with_covered_use": len(covered_defs),
    "definitions": defs,
    "uses": uses,
    "uncovered_definitions": [item for item in defs if (item["scope"], item["name"], item["lineno"]) not in covered_defs],
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
