# FigExport

[![CI](https://github.com/HouGui/figexport/actions/workflows/ci.yml/badge.svg)](https://github.com/HouGui/figexport/actions/workflows/ci.yml)
[![Docs build](https://github.com/HouGui/figexport/actions/workflows/docs.yml/badge.svg)](https://github.com/HouGui/figexport/actions/workflows/docs.yml)
[Docs](https://hougui.github.io/figexport/)

Export **SVG, draw.io, LaTeX and PlantUML** figures to **PDF, SVG, PNG or JPG**
with one command. Process a file or a directory tree, or use a JSON configuration
for repeatable exports.

## Quick start

Requires Python 3.10+ and the [system tools for your input formats](https://github.com/HouGui/figexport/blob/main/docs/installation.md).

```sh
pip install figexport
figexport figures/ --format pdf --output-dir exported/
```

Preview an export or check installed tools:

```sh
figexport figures/ --dry-run
figexport --check-tools
```

The default output is `_export/`; subdirectories are preserved. Individual
conversion failures return a nonzero exit status. Use `--help` for all options.

## Documentation

- [Documentation source](https://github.com/HouGui/figexport/tree/main/docs)
- [Contributing](https://github.com/HouGui/figexport/blob/main/CONTRIBUTING.md)
- [Releases](https://github.com/HouGui/figexport/releases)

## License

[MIT](https://github.com/HouGui/figexport/blob/main/LICENSE). External converters have their own licenses and are installed separately.
