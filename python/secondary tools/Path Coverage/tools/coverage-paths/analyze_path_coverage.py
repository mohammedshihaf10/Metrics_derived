from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path


def estimate(stmt: ast.stmt) -> int:
    if isinstance(stmt, ast.If):
        return max(1, paths(stmt.body)) + max(1, paths(stmt.orelse))
    if isinstance(stmt, (ast.For, ast.While)):
        return 1 + paths(stmt.body) + paths(stmt.orelse)
    return 1


def paths(body: list[ast.stmt]) -> int:
    total = 1
    for stmt in body:
        total *= estimate(stmt)
    return total


repo = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
target = repo / "actionscicd" / "somecode.py"
coverage_json = repo / "secondary_path_coverage.json"

subprocess.run([sys.executable, "-m", "coverage", "erase"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "json", "-o", coverage_json.name], cwd=str(repo), check=True)

data = json.loads(coverage_json.read_text(encoding="utf-8"))
file_key = next(key for key in data["files"] if key.endswith("actionscicd\\somecode.py") or key.endswith("actionscicd/somecode.py"))
covered = set(data["files"][file_key]["executed_lines"])

tree = ast.parse(target.read_text(encoding="utf-8"))
functions = []
for node in tree.body:
    if isinstance(node, ast.FunctionDef):
        end = max(getattr(child, "lineno", node.lineno) for child in ast.walk(node))
        functions.append({"name": node.name, "lineno": node.lineno, "estimated_paths": paths(node.body), "covered": any(line in covered for line in range(node.lineno, end + 1))})

report = {"file": str(target), "covered_lines": sorted(covered), "functions": functions, "covered_functions": sum(1 for item in functions if item["covered"]), "estimated_total_paths": sum(int(item["estimated_paths"]) for item in functions)}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
