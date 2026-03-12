#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_REPO_PATH = ROOT.parent / "cJSON"
DEFAULT_OUTPUT_PATH = ROOT / "dataflow_report" / "all_definition_report.json"
STATEMENT_INFO = ROOT.parent / "Statement Coverage" / "gcovr_report" / "statement_coverage.info"
STATEMENT_RUNNER = ROOT.parent / "Statement Coverage" / "run_gcovr.py"
CPPCHECK = Path(r"C:\msys64\mingw64\bin\cppcheck.exe")


def install_tool() -> int:
    return 0 if CPPCHECK.is_file() else 1


def resolve_repo_path(value: str | None) -> Path:
    if value is None:
        return DEFAULT_REPO_PATH.resolve()
    path = Path(value)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    return path


def ensure_statement_report(repo: Path) -> None:
    if STATEMENT_INFO.is_file():
        return
    subprocess.run(["py", "-3.12", str(STATEMENT_RUNNER), "run", "--repo", str(repo)], check=True, cwd=str(ROOT))


def normalize_file_name(path_text: str) -> str:
    text = path_text.replace("\\", "/")
    name = Path(text).name
    if name:
        return name
    return text


def parse_lcov_hits(info_path: Path) -> set[int]:
    hits: set[int] = set()
    current = None
    for raw_line in info_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if raw_line.startswith("SF:"):
            current = normalize_file_name(raw_line[3:])
        elif raw_line.startswith("DA:") and current == "cJSON.c":
            line_no, count = raw_line[3:].split(",", 1)
            if int(count) > 0:
                hits.add(int(line_no))
    return hits


def build_analysis(repo: Path) -> dict[str, object]:
    ensure_statement_report(repo)
    dump_base = repo / "cJSON.c"
    subprocess.run([str(CPPCHECK), "--dump", str(dump_base)], cwd=str(repo), check=True, capture_output=True, text=True)
    dump_path = repo / "cJSON.c.dump"
    root = ET.parse(dump_path).getroot()
    tokens = {}
    for token in root.iter("token"):
        token_id = token.attrib.get("id")
        if token_id:
            tokens[token_id] = {
                "line": int(token.attrib.get("linenr", "0")),
                "str": token.attrib.get("str", ""),
                "varId": token.attrib.get("varId", ""),
                "variable": token.attrib.get("variable", ""),
            }
    covered_lines = parse_lcov_hits(STATEMENT_INFO)
    definitions = []
    definition_use_pairs = []
    for var in root.iter("var"):
        if var.attrib.get("access") != "Local":
            continue
        name_token = tokens.get(var.attrib.get("nameToken", ""))
        if not name_token:
            continue
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name_token["str"]):
            continue
        def_line = int(name_token["line"])
        var_id = name_token.get("variable") or var.attrib.get("id", "")
        use_lines = sorted(
            {
                int(token["line"])
                for token in tokens.values()
                if token.get("variable") == var_id and int(token["line"]) >= def_line and int(token["line"]) in covered_lines
            }
        )
        if def_line in use_lines and len(use_lines) == 1:
            use_lines = []
        definitions.append(
            {
                "name": name_token["str"],
                "def_line": def_line,
                "covered_definition": def_line in covered_lines,
                "covered_use_lines": use_lines,
            }
        )
        for use_line in use_lines:
            if use_line == def_line:
                continue
            definition_use_pairs.append({"name": name_token["str"], "def_line": def_line, "use_line": use_line})
    uncovered = [item for item in definitions if not item["covered_use_lines"]]
    return {
        "definitions_total": len(definitions),
        "definitions_covered": sum(1 for item in definitions if item["covered_definition"]),
        "definitions_with_covered_use": sum(1 for item in definitions if item["covered_use_lines"]),
        "definition_use_pairs_total": len(definition_use_pairs),
        "definition_use_pairs": definition_use_pairs[:20],
        "uncovered_definitions": [{"name": item["name"], "def_line": item["def_line"]} for item in uncovered[:20]],
        "definitions": definitions[:20],
        "covered_lines_sample": sorted(covered_lines)[:40],
    }


def run_tool(repo: Path, output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_analysis(repo)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("install")
    run = sub.add_parser("run")
    run.add_argument("--repo")
    run.add_argument("--output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "install":
        return install_tool()
    repo = resolve_repo_path(args.repo)
    output_path = Path(args.output or DEFAULT_OUTPUT_PATH).resolve()
    return run_tool(repo, output_path)


if __name__ == "__main__":
    raise SystemExit(main())
