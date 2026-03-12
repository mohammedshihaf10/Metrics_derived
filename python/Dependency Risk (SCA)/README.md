# Dependency Risk (SCA) Tool Runner

This workspace mirrors the other technique folders, but for Python software composition analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for the runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../Cyclomatic Complexity/github-actions-cicd-example/`: shared existing Python repo used by the notebook

## Included Tool

- `pip-audit`

## Note

This folder is Python-only. It uses `pip-audit` as the single open-source dependency-vulnerability tool for SCA-style auditing.

## Prerequisite

This workspace expects a working Python installation on the machine.
