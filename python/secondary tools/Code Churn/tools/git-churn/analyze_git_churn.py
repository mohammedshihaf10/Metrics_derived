from __future__ import annotations
import json, subprocess, sys
from collections import defaultdict
from pathlib import Path
repo, output = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
result = subprocess.run(['git', 'log', '--numstat', '--format=%H|%cI'], cwd=str(repo), capture_output=True, text=True, check=True)
stats = defaultdict(lambda: {'path':'','commit_count':0,'added_lines':0,'deleted_lines':0,'total_churn':0})
commit = ''
for line in result.stdout.splitlines():
    if not line.strip():
        continue
    if '|' in line and '\t' not in line:
        commit = line.split('|', 1)[0]
        continue
    parts = line.split('\t')
    if len(parts) != 3 or '-' in parts[:2]:
        continue
    added, deleted, path = int(parts[0]), int(parts[1]), parts[2]
    item = stats[path]
    item['path'] = path
    item['commit_count'] += 1
    item['added_lines'] += added
    item['deleted_lines'] += deleted
    item['total_churn'] += added + deleted
report = {'summary': {'total_files_touched': len(stats), 'total_commits': len({commit})}, 'top_files': sorted(stats.values(), key=lambda x: (x['total_churn'], x['commit_count']), reverse=True)[:10]}
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
