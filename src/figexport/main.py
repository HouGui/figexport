"""Command-line entry point. Library imports never configure global logging."""

import argparse
import json
import logging
import sys
from pathlib import Path

from figexport import __version__
from figexport.config import DEFAULT_CONFIG, ExportConfig
from figexport.errors import ConfigError, FigexportError
from figexport.export.enums import ExportFormat
from figexport.export_manager import ExportManager
from figexport.tools import tool_status


def get_config_dict(config_file: Path, args: argparse.Namespace) -> dict:
    """Read UTF-8 JSON and apply CLI overrides, including when no default file exists."""
    config_dict = {}
    if config_file.exists():
        try:
            config_dict = json.loads(config_file.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise ConfigError(
                f"Invalid JSON in '{config_file}' at line {exc.lineno}, "
                f"column {exc.colno}: {exc.msg}"
            ) from exc
        except UnicodeError as exc:
            raise ConfigError(f"Configuration '{config_file}' must be UTF-8: {exc}") from exc
        if not isinstance(config_dict, dict):
            raise ConfigError(f"Configuration '{config_file}' must be a JSON object.")
    elif args.config is not None:
        raise ConfigError(f"Configuration file '{config_file}' does not exist.")

    if args.format:
        config_dict["export_format"] = args.format
    if args.output_dir is not None:
        config_dict["export_dir"] = str(args.output_dir.expanduser().resolve())
    if args.timeout is not None:
        config_dict["timeout"] = args.timeout
    if args.exclude:
        exclusions = config_dict.get("excluded_paths", [])
        if not isinstance(exclusions, list):
            raise ConfigError("excluded_paths must be a list of paths.")
        config_dict["excluded_paths"] = exclusions + [
            str(p.expanduser().resolve()) for p in args.exclude
        ]
    return config_dict


def _format(value: str) -> str:
    try:
        return ExportFormat.from_str(value).value
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="figexport",
        description="Export SVG, draw.io, LaTeX and PlantUML figures to PDF/SVG/PNG/JPG.",
        epilog="Config paths are relative to the config file; CLI paths are relative to your "
        "working directory. Without a config or path, export the current directory.",
    )
    _add_input_options(parser)
    _add_export_options(parser)
    _add_action_options(parser)

    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "-v", "--verbose", action="store_true", help="Include debugging tracebacks."
    )
    verbosity.add_argument("-q", "--quiet", action="store_true", help="Only print errors.")
    parser.add_argument("--version", action="version", version=f"figexport {__version__}")
    return parser.parse_args(argv)


def _add_input_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", type=Path, help="Input file or directory (recursive).")
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        help="JSON configuration (default: figexport_config.json if present).",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=_format,
        metavar="{pdf,svg,png,jpg}",
        help="Output format; overrides configuration (default: pdf).",
    )
    parser.add_argument(
        "-o", "--output-dir", type=Path, help="Output directory (default: _export)."
    )
    parser.add_argument(
        "--exclude",
        action="append",
        type=Path,
        default=[],
        metavar="PATH",
        help="Exclude a file or directory and its descendants; repeatable.",
    )


def _add_export_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--no-overwrite",
        action="store_true",
        help="Skip a source if any of its output files already exists.",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Continue after conversion errors; still exit nonzero on failure.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        metavar="SECONDS",
        help="Timeout per external command or download connect/read (default: 120).",
    )
    parser.add_argument(
        "--json", action="store_true", help="Write a machine-readable report to stdout."
    )


def _add_action_options(parser: argparse.ArgumentParser) -> None:
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--dry-run", action="store_true", help="Show planned outputs without writing."
    )
    actions.add_argument(
        "--check-tools",
        action="store_true",
        help="Report converter availability without exporting or downloading.",
    )
    actions.add_argument(
        "--init-config",
        nargs="?",
        const=Path("figexport_config.json"),
        type=Path,
        metavar="FILE",
        help="Create an example config, without overwriting.",
    )


def _init_config(args: argparse.Namespace) -> None:
    with args.init_config.expanduser().open("x", encoding="utf-8") as stream:
        json.dump(DEFAULT_CONFIG, stream, indent=2)
        stream.write("\n")

    if args.json:
        print(json.dumps({"config": str(args.init_config.resolve())}))
    elif not args.quiet:
        print(f"Created {args.init_config}.")


def _show_tools(config: ExportConfig, args: argparse.Namespace) -> None:
    status = tool_status(config)
    if args.json:
        print(json.dumps(status, indent=2))
    elif not args.quiet:
        for name, location in status.items():
            print(f"{name}: {location or 'not found (optional unless needed by your inputs)'}")


def _execute(args: argparse.Namespace) -> int:
    if args.init_config is not None:
        _init_config(args)
        return 0

    config_file = (args.config or Path("figexport_config.json")).expanduser().resolve()
    data = get_config_dict(config_file, args)
    config = ExportConfig(
        data, config_file.parent, args.path.expanduser().resolve() if args.path else None
    )
    if args.check_tools:
        _show_tools(config, args)
        return 0

    report = ExportManager(config).run(
        dry_run=args.dry_run, keep_going=args.keep_going, overwrite=not args.no_overwrite
    )
    summary = report.to_dict()
    if args.json:
        print(json.dumps(summary, indent=2))
    elif not args.quiet:
        print(
            f"{summary['exported']} exported, {summary['planned']} planned, "
            f"{summary['skipped']} skipped, {summary['failed']} failed."
        )
        if not report.results:
            print("No supported input files found.")
    return 1 if report.failed else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    logger = logging.getLogger("figexport")
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    previous_level, previous_propagate = logger.level, logger.propagate
    logger.addHandler(handler)
    logger.propagate = False
    logger.setLevel(
        logging.DEBUG if args.verbose else logging.ERROR if args.quiet else logging.INFO
    )

    try:
        return _execute(args)
    except (FigexportError, OSError, UnicodeError) as exc:
        logger.error("figexport: %s", exc, exc_info=args.verbose)
        code = 2 if isinstance(exc, (ConfigError, UnicodeError)) else 1
        if args.json:
            print(json.dumps({"error": str(exc), "exit_code": code}))
        return code
    except KeyboardInterrupt:
        logger.error("figexport: interrupted.")
        return 130
    finally:
        logger.removeHandler(handler)
        handler.close()
        logger.setLevel(previous_level)
        logger.propagate = previous_propagate


if __name__ == "__main__":
    sys.exit(main())
