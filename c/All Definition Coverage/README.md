# All Definition Coverage

This folder follows the same model as the Python workspace.

Tools included:
- `cppcheck --dump`
- `lcov`

Shared target repo:
- `..\cJSON`

Typical flow:
1. `py -3.12 .\run_all_definition.py install`
2. `py -3.12 .\run_all_definition.py run --repo "..\cJSON"`
