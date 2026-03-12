# Coverage Delta

This folder follows the same model as the Python workspace.

Tools included:
- `git`
- `lcov`

Shared target repo:
- `..\cJSON`

Typical flow:
1. `py -3.12 .\run_coverage_delta.py install`
2. `py -3.12 .\run_coverage_delta.py run --repo "..\cJSON"`
