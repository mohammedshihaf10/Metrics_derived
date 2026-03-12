# Code Churn Tool Runner

This workspace mirrors the other technique folders, but for Python code-churn analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for the runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../Cyclomatic Complexity/github-actions-cicd-example/`: shared existing Git-backed Python repo used by the notebook

## Included Tool

- `pydriller`

## Note

This folder is Python-only. It uses `pydriller` as the single open-source history-analysis tool for code churn.

## Prerequisite

This workspace expects a working Python installation on the machine.
