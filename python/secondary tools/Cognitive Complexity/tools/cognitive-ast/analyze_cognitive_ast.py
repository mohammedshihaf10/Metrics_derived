from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


def score_block(body: list[ast.stmt], depth: int = 0) -> int:
    total = 0
    for stmt in body:
        if isinstance(stmt, ast.If):
            total += 1 + depth + score_block(stmt.body, depth + 1) + score_block(stmt.orelse, depth + 1)
        elif isinstance(stmt, (ast.For, ast.While)):
            total += 1 + depth + score_block(stmt.body, depth + 1) + score_block(stmt.orelse, depth + 1)
        elif isinstance(stmt, ast.Try):
            total += len(stmt.handlers) * (1 + depth)
            total += score_block(stmt.body, depth + 1) + score_block(stmt.orelse, depth + 1) + score_block(stmt.finalbody, depth + 1)
    return total


repo = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
report = {"files": []}

for path in sorted(item for item in repo.rglob("*.py") if ".venv" not in item.parts and "__pycache__" not in item.parts):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = [{"name": node.name, "lineno": node.lineno, "cognitive_complexity": score_block(node.body)} for node in tree.body if isinstance(node, ast.FunctionDef)]
    if functions:
        report["files"].append({"file": str(path.relative_to(repo)), "functions": functions})

output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
