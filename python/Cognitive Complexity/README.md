# Cognitive Complexity Tool Runner

This workspace mirrors the cyclomatic-complexity harness, but for cognitive-complexity-oriented analysis.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_<tool>.py`: installs or runs one tool at a time
- `*_notebook.ipynb`: thin notebook wrapper for each runner
- `*_simple_mapping.txt`: maps notebook output to the requested classifications
- `../github-actions-cicd-example/`: shared root-level target repo used by the notebooks
- `tool_examples/`: small local examples for stable cognitive-complexity output

## Included Tools

- `complexipy`
- `flake8-cognitive-complexity`
- `pyrefact`

## Prerequisite

This workspace expects a working Python installation on the machine.
