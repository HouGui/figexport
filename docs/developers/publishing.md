# Publishing

The package is published on **PyPI**. The documentation website is hosted on
**GitHub Pages**. Pushing to `main` does not publish a package.

## Make the repository public

In [repository settings](https://github.com/HouGui/figexport/settings), choose
**General → Danger Zone → Change visibility → Public**. Enable GitHub Actions
if it is disabled, and wait for CI and Documentation checks to pass.

## Publish the documentation website

1. In **Settings → Pages**, set the source to **GitHub Actions**.
2. In **Settings → Secrets and variables → Actions → Variables**, add
   `ENABLE_PAGES` with the value `true`.
3. Run **Actions → Documentation → Run workflow** on `main`.

The website will be [hougui.github.io/figexport](https://hougui.github.io/figexport/).
Later documentation changes on `main` deploy automatically. Deployment requires
public visibility and `ENABLE_PAGES=true`. No `gh-pages` branch is needed.
See [GitHub's Pages setup](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Connect PyPI once

1. In **GitHub Settings → Environments**, create `pypi` and restrict deployment
   to tags matching `v*`.
2. Sign in as an owner of the existing [figexport project](https://pypi.org/manage/project/figexport/).
   Under **Publishing**, add a GitHub Trusted Publisher:

| Field | Value |
| --- | --- |
| Owner | `HouGui` |
| Repository | `figexport` |
| Workflow filename | `release.yml` |
| Environment | `pypi` |

[Trusted Publishing](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
uses short-lived credentials. No API token or repository secret is needed.

## Publish a release

1. Set the version in `pyproject.toml` and run the
   [development checks](index.md#validate-a-change).
2. Push to `main` and wait for CI and Documentation checks to pass.
3. Tag that commit. For version 0.2.6:

        git switch main
        git pull --ff-only
        git tag -a v0.2.6 -m "Release 0.2.6"
        git push origin v0.2.6

4. Open [GitHub Releases](https://github.com/HouGui/figexport/releases/new), select
   `v0.2.6`, title it `FigExport 0.2.6`, write the release notes and publish it.
   Leave **pre-release** unchecked.
5. Wait for **Publish to PyPI** to finish. It builds, tests and uploads the same
   wheel and source archive. Approve the `pypi` deployment if you added reviewers.
6. Verify in a fresh virtual environment:

        pip install figexport
        figexport --version

For existing installations, run `pip install --upgrade figexport`.

The tag must equal `v` plus the package version. Only stable versions are published,
and only from a public repository. PyPI versions cannot be reused: if an upload
fails, check PyPI and the workflow logs before retrying. Changed artifacts need
a new version.
