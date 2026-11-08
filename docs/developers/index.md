# For Developers

Use this guide to work on the code. For package releases and the documentation
website, see [Publishing](publishing.md).

## Local setup

Use Python 3.10+ for the package, or Python 3.13+ to also run release tooling.
Clone your fork, create a branch, then run these commands from the repository root:

```sh
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Install [Cairo](../installation.md) to run the portable rendering tests. Java,
draw.io and TeX are only needed for the opt-in native integration tests.

## Validate a change

```sh
ruff check .
ruff format --check .
python -m pytest -m "not integration" --cov
mkdocs build --strict
python -m build
python -m twine check --strict dist/*
```

Use `ruff format .` to format code and `mkdocs serve` to preview docs locally.
Tests use temporary directories and block network requests by default. The
coverage floor is 85%; add a focused regression test for each bug fix.

For the complete native suite, install all converters, provide a PlantUML JAR,
and set these environment variables before running pytest:

```text
FIGEXPORT_INTEGRATION=1
FIGEXPORT_PLANTUML_JAR=/absolute/path/to/plantuml.jar
FIGEXPORT_DRAWIO=/optional/path/to/drawio
```

Then run `python -m pytest -m integration`. On headless Linux, prefix the command
with `xvfb-run -a`. Tests fail if enabled converters are missing; skips never
silently hide an incomplete integration environment.

CI tests the **built wheel** on Windows, Linux and macOS with Python 3.10–3.14,
including real SVG conversions. A separate Linux job tests all external converters
and formats. Native draw.io/TeX/PlantUML execution on Windows/macOS is not yet covered.

## Code map

| Module | Responsibility |
| --- | --- |
| `config.py` | Settings validation and path resolution |
| `export_manager.py` | Discovery, output collisions, execution and reports |
| `export/fig_exporter.py` | Backend interface and staged output publication |
| `export/registry.py` | Source extension → backend factory |
| `export/*_exporter.py` | Tool-specific conversions |
| `tools.py` | Executable discovery and subprocess diagnostics |
| `main.py` | Argument parsing, presentation and exit codes |

## Adding a converter

1. Subclass `FigExporter` and implement `_convert(source, outputs)`. Write only
   the supplied staging paths; raise `ExportError` with useful details on failure.
2. If one source produces several files, override `output_paths(source, output_dir)`.
   Keep it deterministic and free of writes/downloads. Its order must match conversion.
3. Add its extension and factory to `EXPORTERS` in `export/registry.py`.
4. Add optional settings to `ExportConfig` only when the tool needs them. Reuse
   `run_command()` for timeouts, captured diagnostics and safe argument handling.
5. Add offline tests, a native integration test when appropriate, and document
   dependencies and format limits. Update the CLI help's format description.

For an application-specific backend, pass
`ExportManager(config, exporters={**EXPORTERS, ".custom": factory})` instead of
changing the global registry. Factory keys are lowercase extensions with a leading
`.`; the callable receives the validated configuration and returns a `FigExporter`.

The base class creates and cleans temporary directories, checks expected outputs
and replaces final files. Backends need no duplicate staging or error-reporting
framework. Keep additions focused on the converter's behavior.
