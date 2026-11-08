# Working on FigExport

Start with [docs/developers/index.md](docs/developers/index.md) for setup, checks and the code map.
Keep user instructions in `docs/` and the README brief.

- Keep configuration, discovery, backends and CLI presentation separate; preserve public APIs.
- Keep functions focused and short; separate distinct steps with blank lines.
- Imports and constructors must not write files, download tools or configure root logging.
- Plan outputs before writing; reject collisions and source overwrites. Convert into staging files.
- Run subprocesses with argument lists, timeouts and captured diagnostics; never use a shell.
- Test behavior changes offline in `tmp_path`, including Windows paths. Mark native tests `integration`.
- Set the version in `pyproject.toml`; follow [docs/developers/publishing.md](docs/developers/publishing.md) for publishing.
- Keep Pages gated by public visibility and `ENABLE_PAGES`; maintenance must not enable publication.
