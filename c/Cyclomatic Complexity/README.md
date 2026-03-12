# Cyclomatic Complexity

This folder follows the same model as the Python workspace.

Tool included:
- `lizard`

Shared target repo:
- `..\cJSON`

Typical flow:
1. `py -3.12 .\run_lizard.py install`
2. `py -3.12 .\run_lizard.py run --repo "..\cJSON" -- .`
