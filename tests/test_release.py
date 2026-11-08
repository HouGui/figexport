"""Exercise the release guard with synthetic distributions, without publishing."""

import io
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile

import pytest

pytestmark = pytest.mark.skipif(
    sys.version_info < (3, 11), reason="Release tooling uses Python 3.13 in CI (tomllib required)."
)
SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_release.py"


def make_distributions(tmp_path, version="0.2.6", wheel_version=None, sdist_version=None):
    (tmp_path / "pyproject.toml").write_text(f'[project]\nversion = "{version}"\n')
    dist = tmp_path / "dist"
    dist.mkdir()
    with ZipFile(dist / "package.whl", "w") as wheel:
        wheel.writestr(
            "figexport.dist-info/METADATA",
            f"Name: figexport\nVersion: {wheel_version or version}\n",
        )

    metadata = f"Name: figexport\nVersion: {sdist_version or version}\n".encode()
    with tarfile.open(dist / "package.tar.gz", "w:gz") as sdist:
        member = tarfile.TarInfo("figexport/PKG-INFO")
        member.size = len(metadata)
        sdist.addfile(member, io.BytesIO(metadata))
    return dist


def check_release(tmp_path, tag="v0.2.6"):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=tmp_path,
        env={**os.environ, "RELEASE_TAG": tag},
        capture_output=True,
        text=True,
        timeout=20,
    )


@pytest.mark.parametrize(
    "version,tag,wheel_version,sdist_version,message",
    [
        ("0.2.6", "v0.2.6", None, None, "Validated"),
        ("0.2.6", "0.2.6", None, None, "Release tag must"),
        ("0.2.6", "v2.0.0", None, None, "Release tag must"),
        ("0.2.6.dev1", "v0.2.6.dev1", None, None, "Only stable versions"),
        ("0.2.6+local", "v0.2.6+local", None, None, "Only stable versions"),
        ("0.2.6rc1", "v0.2.6rc1", None, None, "Only stable versions"),
        ("0.2.6", "v0.2.6", "2.0.0", None, "wheel metadata does not match"),
        ("0.2.6", "v0.2.6", None, "2.0.0", "source archive metadata does not match"),
    ],
)
def test_release_guard(tmp_path, version, tag, wheel_version, sdist_version, message):
    make_distributions(tmp_path, version, wheel_version, sdist_version)
    result = check_release(tmp_path, tag)
    assert (result.returncode == 0) is (message == "Validated")
    assert message in result.stdout + result.stderr


@pytest.mark.parametrize("filename", ["package.whl", "package.tar.gz"])
@pytest.mark.parametrize("extra", [False, True], ids=["missing", "duplicate"])
def test_requires_one_of_each_distribution(tmp_path, filename, extra):
    dist = make_distributions(tmp_path)
    if extra:
        (dist / f"extra-{filename}").write_bytes((dist / filename).read_bytes())
    else:
        (dist / filename).unlink()

    result = check_release(tmp_path)
    assert result.returncode != 0
    assert "exactly one wheel and one source archive" in result.stderr


@pytest.mark.parametrize("archive", ["wheel", "source archive"])
def test_requires_distribution_metadata(tmp_path, archive):
    dist = make_distributions(tmp_path)
    if archive == "wheel":
        with ZipFile(dist / "package.whl", "w"):
            pass
    else:
        with tarfile.open(dist / "package.tar.gz", "w:gz"):
            pass

    result = check_release(tmp_path)
    assert result.returncode != 0
    assert f"Expected exactly one {archive} metadata file" in result.stderr
