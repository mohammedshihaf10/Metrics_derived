# Lint / Rule Violation Tool Runner

This workspace mirrors the other technique folders, but for Python lint and rule-violation analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for the runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../Code Duplication/github-actions-cicd-example/`: shared existing Python repo used by the notebook

## Included Tool

- `pylint`

## Note

This folder is Python-only. It uses `pylint` as the single open-source tool for rule detection, violation reporting, naming checks, unused-variable checks, severity categories, and configuration handling.

## Prerequisite

This workspace expects a working Python installation on the machine.
