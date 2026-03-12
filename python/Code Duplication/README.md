# Code Duplication Tool Runner

This workspace mirrors the other technique folders, but for Python code duplication analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: tool-specific runtime notes
- `tools/<tool-name>/tool.json`: tool metadata and entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for the runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `github-actions-cicd-example/`: cloned Python repo used by the notebook
- `jscpd_report/`: generated duplication report output

## Included Tool

- `jscpd`

## Note

This folder is Python-only. It uses the open-source `jscpd` tool to detect duplicated blocks, duplicated lines, duplicated tokens, clone locations, and duplication percentages.

## Prerequisite

This workspace expects a working Node.js installation on the machine.
