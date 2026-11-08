# Installation

FigExport supports Python 3.10+. Install it in a virtual environment:

```sh
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install figexport
```

For source installation and contributions, see [For Developers](developers/index.md).

## System tools

Install only the tools required by your sources and output format.

| Input | Required tools |
| --- | --- |
| SVG → SVG | None; the file is copied unchanged |
| SVG → PDF/PNG/JPG | Cairo |
| draw.io | draw.io Desktop |
| LaTeX → PDF | `pdflatex` and any packages used by the document |
| LaTeX → SVG | `pdflatex` and `dvisvgm` |
| LaTeX → PNG/JPG | `pdflatex`, `dvisvgm` and Cairo |
| PlantUML → SVG/PNG/JPG | `plantuml` on PATH, or Java and a PlantUML JAR |
| PlantUML → PDF | The above, plus Cairo |

Some PlantUML diagrams also require Graphviz (`dot`).

### Linux

For Debian/Ubuntu, install the relevant packages:

```sh
sudo apt-get update
sudo apt-get install libcairo2 default-jre-headless graphviz
# Only for LaTeX; latex-extra/pictures include standalone and TikZ:
sudo apt-get install texlive-latex-extra texlive-pictures dvisvgm
```

Install draw.io Desktop separately from its [official releases](https://github.com/jgraph/drawio-desktop/releases).
Headless draw.io needs an X display; use `xvfb-run -a figexport ...` on a server.
Other distributions use different package names.

### macOS

```sh
brew install cairo libffi
brew install --cask drawio
```

Install a TeX distribution such as [MacTeX](https://tug.org/mactex/) for LaTeX.
If Cairo is not found, set `DYLD_FALLBACK_LIBRARY_PATH` to `$(brew --prefix)/lib`
in the shell used to run FigExport.

### Windows

Install the 64-bit [MSYS2](https://www.msys2.org/) distribution. In its MINGW64 shell:

```sh
pacman -S --needed mingw-w64-x86_64-cairo
```

For a normal 64-bit Windows Python installation, expose these DLLs in PowerShell:

```powershell
$cairoDir = "C:\msys64\mingw64\bin"
$env:PATH = "$env:PATH;$cairoDir"
$env:CAIROCFFI_DLL_DIRECTORIES = $cairoDir
```

Adjust the path if MSYS2 is installed elsewhere. CairoCFFI needs PATH for DLL
discovery as well as its DLL directory setting. Append the MSYS2 directory so
your Windows Python or active virtual environment stays ahead of MSYS2's Python.

Install draw.io Desktop normally; FigExport checks PATH and common installation
directories. Use TeX Live or MiKTeX for LaTeX, and add `pdflatex` and `dvisvgm` to
PATH.

See [CairoSVG's installation notes](https://cairosvg.org/documentation/) for native
library requirements. FigExport reports missing dependencies only when needed.

## PlantUML

Install the `plantuml` command, or download a JAR from the
[official releases](https://github.com/plantuml/plantuml/releases) and set
`tools.plantuml.jar_name` in your [configuration](configuration.md).
Automatic downloading happens only if you explicitly configure `download_url`.

Run `figexport --check-tools` to inspect discovery. It does not download anything,
launch external programs or verify every tool's runtime dependencies.
