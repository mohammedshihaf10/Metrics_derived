# Static Vulnerabilities (SAST) Tool Runner

This workspace mirrors the other technique folders, but for Python static security analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for the runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../Code Duplication/github-actions-cicd-example/`: shared existing Python repo used by the notebook

## Included Tool

- `bandit`

## Note

This folder is Python-only. It uses `bandit` as the single open-source SAST tool for security-rule detection and structured reporting.

## Prerequisite

This workspace expects a working Python installation on the machine.
