# FigExport

FigExport gives SVG, draw.io, LaTeX and PlantUML figures a shared export command.
All four input types can produce PDF, SVG, PNG and JPG. Requires Python 3.10+.

## Start exporting

[Install the system tools](installation.md) needed for your input format, then:

```sh
pip install figexport
figexport figures/ -f pdf -o exported/
```

Run `figexport figures/ --dry-run` to preview filenames or `figexport --check-tools`
to inspect installed converters.

Folder exports preserve their directory structure. Unrelated file types are
ignored; explicitly selecting an unsupported file is an error.

## Find what you need

- [CLI reference](cli.md): options, examples, reports and exit codes.
- [Configuration](configuration.md): repeatable exports and tool settings.
- [Python API](api.md): call FigExport from your application.
- [Troubleshooting](troubleshooting.md): missing tools and format limits.
- [For Developers](developers/index.md): contribute, extend or publish FigExport.
