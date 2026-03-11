# Minimal Tool Runner

This workspace is a simple harness for running a single configured tool against a repo you provide.

## Structure

- `tools/<tool-name>/requirements.txt`: dependencies for that tool only
- `tools/<tool-name>/tool.json`: tool metadata and command entrypoint
- `run_tool.py`: installs or runs one tool at a time
- `requirements-whitebox.txt`: optional aggregate dependency file

## Included Tool

- `coveragepy`

## Install a Tool

```powershell
python run_tool.py install coveragepy
```

This creates a virtual environment at `tools/coveragepy/.venv` and installs only that tool's dependencies.

## Run a Tool Against a Repo

```powershell
python run_tool.py run coveragepy --repo D:\path\to\repo -- run -m pytest
```

That command executes:

```powershell
python -m coverage run -m pytest
```

inside the provided repo directory.

Tool output is streamed directly. The runner does not reformat or post-process stdout/stderr.

## More Examples

Coverage report:

```powershell
python run_tool.py run coveragepy --repo D:\path\to\repo -- report
```

Coverage XML:

```powershell
python run_tool.py run coveragepy --repo D:\path\to\repo -- xml
```

## Prerequisite

This workspace expects a working `python` installation on the machine. The current environment where I built this scaffold does not have a usable Python executable, so I could not run the install step here.
