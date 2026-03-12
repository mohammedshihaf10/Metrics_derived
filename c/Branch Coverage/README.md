# Branch Coverage

This folder follows the same model as the Python workspace.

Tool included:
- `gcovr`

Shared target repo:
- `..\cJSON`

Typical flow:
1. `py -3.12 .\run_gcovr.py install`
2. `py -3.12 .\run_gcovr.py run --repo "..\cJSON"`
