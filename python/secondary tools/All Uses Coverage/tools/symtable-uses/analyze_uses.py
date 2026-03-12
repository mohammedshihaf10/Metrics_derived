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
        self.uses: list[dict[str, object]] = []
        self.predicate_lines: set[int] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for arg in node.args.args:
            self.defs.append({"name": arg.arg, "lineno": arg.lineno})
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defs.append({"name": target.id, "lineno": target.lineno})
        self.generic_visit(node.value)

    def visit_If(self, node: ast.If) -> None:
        self.predicate_lines.add(node.lineno)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.predicate_lines.add(node.lineno)
        if isinstance(node.target, ast.Name):
            self.defs.append({"name": node.target.id, "lineno": node.target.lineno})
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            use_kind = "p-use" if node.lineno in self.predicate_lines else "c-use"
            self.uses.append({"name": node.id, "lineno": node.lineno, "use_kind": use_kind})


repo = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
target = repo / "actionscicd" / "somecode.py"
coverage_json = repo / "secondary_uses_coverage.json"

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

defs: dict[tuple[str, str], list[int]] = defaultdict(list)
for item in collector.defs:
    defs[(scope(int(item["lineno"]), item_ranges), str(item["name"]))].append(int(item["lineno"]))

pairs = []
for item in collector.uses:
    item_scope = scope(int(item["lineno"]), item_ranges)
    candidates = [line for line in defs.get((item_scope, str(item["name"])), []) if line <= int(item["lineno"])]
    if candidates:
        def_line = candidates[-1]
        pairs.append({"scope": item_scope, "name": item["name"], "def_line": def_line, "use_line": item["lineno"], "use_kind": item["use_kind"], "covered_pair": def_line in covered and int(item["lineno"]) in covered})

covered_pairs = [item for item in pairs if item["covered_pair"]]
report = {
    "file": str(target),
    "covered_lines": sorted(covered),
    "definition_use_pairs_total": len(pairs),
    "covered_definition_use_pairs": len(covered_pairs),
    "c_use_pairs": sum(1 for item in covered_pairs if item["use_kind"] == "c-use"),
    "p_use_pairs": sum(1 for item in covered_pairs if item["use_kind"] == "p-use"),
    "definition_use_pairs": pairs,
    "uncovered_definition_use_pairs": [item for item in pairs if not item["covered_pair"]],
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
