from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


repo = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
compare_ref = sys.argv[3] if len(sys.argv) > 3 else "HEAD~1"
coverage_json = repo / "coverage_delta_secondary.json"

subprocess.run([sys.executable, "-m", "coverage", "erase"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "run", "-m", "pytest"], cwd=str(repo), check=True)
subprocess.run([sys.executable, "-m", "coverage", "json", "-o", coverage_json.name], cwd=str(repo), check=True)

coverage_data = json.loads(coverage_json.read_text(encoding="utf-8"))
diff_result = subprocess.run(["git", "diff", "--unified=0", compare_ref, "--", "*.py"], cwd=str(repo), capture_output=True, text=True, check=True)

changed_lines: dict[str, set[int]] = {}
current_file = ""
for line in diff_result.stdout.splitlines():
    if line.startswith("+++ b/"):
        current_file = line[6:].replace("/", "\\")
        changed_lines.setdefault(current_file, set())
        continue
    if line.startswith("@@"):
        plus_chunk = next(part for part in line.split() if part.startswith("+"))
        raw = plus_chunk[1:].split(",")
        start = int(raw[0])
        length = int(raw[1]) if len(raw) > 1 else 1
        if current_file and length > 0:
            changed_lines[current_file].update(range(start, start + length))

covered_changed: list[dict[str, object]] = []
uncovered_changed: list[dict[str, object]] = []
for file_key, lines in changed_lines.items():
    coverage_key = next((key for key in coverage_data["files"] if key.endswith(file_key) or key.replace("/", "\\").endswith(file_key)), None)
    if not coverage_key:
        for line_no in sorted(lines):
            uncovered_changed.append({"file": file_key, "line": line_no})
        continue
    executed = set(coverage_data["files"][coverage_key]["executed_lines"])
    for line_no in sorted(lines):
        item = {"file": file_key, "line": line_no}
        if line_no in executed:
            covered_changed.append(item)
        else:
            uncovered_changed.append(item)

total = len(covered_changed) + len(uncovered_changed)
report = {
    "compare_ref": compare_ref,
    "changed_lines": total,
    "covered_changed_lines": len(covered_changed),
    "uncovered_changed_lines": len(uncovered_changed),
    "coverage_percent": round((len(covered_changed) / total) * 100, 2) if total else 100.0,
    "covered": covered_changed,
    "uncovered": uncovered_changed,
}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
