from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

from pydriller import Repository


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: analyze_churn.py <repo> <output>")

    repo = Path(sys.argv[1]).resolve()
    output = Path(sys.argv[2]).resolve()

    file_stats: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "path": "",
            "commit_count": 0,
            "added_lines": 0,
            "deleted_lines": 0,
            "total_churn": 0,
            "last_commit": "",
        }
    )
    total_modifications = 0
    commit_count = 0

    for commit in Repository(str(repo)).traverse_commits():
        commit_count += 1
        for modified in commit.modified_files:
            path = modified.new_path or modified.old_path
            if not path:
                continue
            stats = file_stats[path]
            stats["path"] = path
            stats["commit_count"] = int(stats["commit_count"]) + 1
            added = modified.added_lines or 0
            deleted = modified.deleted_lines or 0
            stats["added_lines"] = int(stats["added_lines"]) + added
            stats["deleted_lines"] = int(stats["deleted_lines"]) + deleted
            stats["total_churn"] = int(stats["total_churn"]) + added + deleted
            stats["last_commit"] = commit.hash
            total_modifications += 1

    top_files = sorted(
        file_stats.values(),
        key=lambda item: (int(item["commit_count"]), int(item["total_churn"])),
        reverse=True,
    )[:10]

    report = {
        "summary": {
            "total_commits": commit_count,
            "total_files_touched": len(file_stats),
            "total_file_modifications": total_modifications,
        },
        "top_files": top_files,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
