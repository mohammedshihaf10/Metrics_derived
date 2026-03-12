# Coverage Delta

This folder follows the same model as the other technique folders.

Tool included:
- diff-cover

Shared target repo:
- `..\Cyclomatic Complexity\github-actions-cicd-example`

Typical flow:
1. `py -3.12 .\run_diff_cover.py install`
2. `py -3.12 .\run_diff_cover.py run --repo "..\Cyclomatic Complexity\github-actions-cicd-example" -- --compare-branch=HEAD~1`
