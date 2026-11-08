# CLI reference

```text
figexport [path] [options]
```

`python -m figexport` is equivalent. With no path, FigExport uses configured
mappings, or the current directory if no mappings are provided. The default
configuration file is `figexport_config.json` in the current directory, if present.

| Option | Purpose |
| --- | --- |
| `-c, --config FILE` | Read a JSON configuration; an explicitly selected missing file is an error |
| `-f, --format FORMAT` | Override the format: `pdf`, `svg`, `png`, `jpg`; `jpeg` is an alias |
| `-o, --output-dir DIR` | Override the export directory |
| `--exclude PATH` | Exclude a file or a whole directory; repeat for multiple paths |
| `--dry-run` | Plan and validate filenames without writing or downloading |
| `--no-overwrite` | Skip a source if any of its outputs exists |
| `--keep-going` | Continue after per-file errors; still return failure if any occurred |
| `--timeout SECONDS` | Positive timeout per external command or download connect/read; default `120` |
| `--json` | Write the result report to stdout as JSON |
| `--check-tools` | Report installed tools, without exporting |
| `--init-config [FILE]` | Create a minimal config; default `figexport_config.json`; never overwrite |
| `-q, --quiet` | Suppress progress and summaries; explicit JSON reports still print |
| `-v, --verbose` | Include tracebacks in error diagnostics |
| `--version` / `-h, --help` | Show the version or usage |

CLI paths resolve against the current working directory. Config-file paths follow
[configuration path rules](configuration.md#paths).

## Examples

```sh
figexport logo.svg -f png -o images
figexport figures --exclude figures/drafts --dry-run
figexport -c exports.json --keep-going --json > report.json
figexport --init-config
```

Reports count **source files**, not output pages. Each result contains `source`,
`outputs`, `status` (`exported`, `planned`, `skipped`, `failed`) and `message`.
Progress and errors go to stderr so stdout remains valid JSON. Configuration or
setup errors produce an `error` and `exit_code` object. Argument-parser errors
(such as unknown flags) use standard argparse text even with `--json`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Completed; also used for dry runs, empty input and informational commands |
| `1` | Conversion, dependency or filesystem failure |
| `2` | Invalid arguments, configuration, input selection or output collision |
| `130` | Interrupted with Ctrl+C |

## Output behavior

Files are discovered in a stable order. Folder scans skip symlinks, configured
output directories, common VCS/environment/cache directories, `build`, `dist`
and `site`. You can explicitly select a symlink to a file or directory.
Exclusions match paths and their descendants, not glob patterns.

Sources with conflicting output names are rejected before conversion, including
case-only collisions that would fail on Windows/macOS. Input files are never
replaced by their own exports. Existing outputs are replaced by default, after
conversion succeeds; `--no-overwrite` preserves them. A draw.io source is skipped
as a whole if even one page output already exists.

Each source is converted into a temporary directory. All expected outputs must
exist before they replace final files. Replacement is atomic per output file;
a disk error during a multi-page replacement can still leave a partially updated
set. Concurrent exports to the same destination are not supported.
