# Maintainability Index Tool Runner

This workspace mirrors the other technique folders, but for Python maintainability-index-oriented analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for each runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../github-actions-cicd-example/`: shared root-level target repo used by the notebook

## Included Tool

- `radon`

## Note

This folder is Python-only. It uses `radon`, which directly reports Python Maintainability Index (`mi`) along with supporting complexity, raw, and Halstead metrics.

## Prerequisite

This workspace expects a working Python installation on the machine.
