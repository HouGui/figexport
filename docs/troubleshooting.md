# Troubleshooting

Start with `figexport --check-tools`. For a failed export, run the same command
with `--verbose` and inspect stderr. Reports identify the source file and include
converter diagnostics; `--keep-going` can collect several failures in one run.

| Symptom | Resolution |
| --- | --- |
| Cairo cannot load | Install the native library and expose its DLL/library directory; see [installation](installation.md) |
| draw.io not found | Install Desktop, add it to PATH or set `tools.drawio.exe_path` |
| draw.io cannot open a display | On headless Linux use `xvfb-run -a figexport ...` |
| PlantUML JAR missing | Set `tools.plantuml.jar_name`, install `plantuml`, or explicitly configure a download URL |
| Java/Graphviz missing | Install the required runtime and add it to PATH |
| LaTeX reports a missing `.sty`/`.cls` | Install that document's TeX packages; `standalone` and TikZ are not Python dependencies |
| A command times out | Inspect the tool error; raise `--timeout` for a legitimately slow conversion |
| Output collision | Rename sources with the same stem or give mappings distinct target directories |
| No files exported | Check the input path, exclusions and output directory; preview with `--dry-run` |

## Format limits

- SVG → SVG copies bytes; it does not validate or normalize the SVG. Rendering
  uses CairoSVG and its [supported SVG features](https://cairosvg.org/svg_support/).
- JPEG has no transparency; transparent pixels are composited over white.
- draw.io exports one file per page: `source_Page_name.ext`. Unsafe filename
  characters are replaced, and duplicate names receive numbered suffixes.
  FigExport detects the page-numbering change introduced by draw.io 27.0.2.
- Use one figure per LaTeX document. PDF retains the compiled document;
  SVG/PNG/JPG export its first page. Relative `\input` paths resolve next to the
  source. Compilation disables shell escape and stops on errors.
- Use one diagram per PlantUML source. Relative includes resolve next to the
  source, and output names follow the source filename even with named diagrams.
  Multiple `@start...` blocks in one file are rejected.

Only export sources you trust. External converters and SVG resource references
can read files or access the network; FigExport is not a sandbox.
