"""Validate the tag and both distributions before publishing a stable release."""

import email
import os
import tarfile
from pathlib import Path
from zipfile import ZipFile

import tomllib
from packaging.version import Version

config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
version = Version(config["project"]["version"])
expected_tag = f"v{version}"
if os.environ.get("RELEASE_TAG") != expected_tag:
    raise SystemExit(f"Release tag must be {expected_tag!r}; update pyproject.toml first.")
if version.is_prerelease or version.is_devrelease or version.local:
    raise SystemExit("Only stable versions can be published by this workflow.")
wheels = list(Path("dist").glob("*.whl"))
sdists = list(Path("dist").glob("*.tar.gz"))
if len(wheels) != 1 or len(sdists) != 1:
    raise SystemExit("Expected exactly one wheel and one source archive in dist/.")
with ZipFile(wheels[0]) as wheel:
    metadata_files = [name for name in wheel.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata_files) != 1:
        raise SystemExit("Expected exactly one wheel metadata file.")
    wheel_metadata = email.message_from_bytes(wheel.read(metadata_files[0]))
with tarfile.open(sdists[0], "r:gz") as sdist:
    metadata_files = [
        member
        for member in sdist.getmembers()
        if member.isfile() and member.name.count("/") == 1 and member.name.endswith("/PKG-INFO")
    ]
    if len(metadata_files) != 1:
        raise SystemExit("Expected exactly one source archive metadata file.")
    with sdist.extractfile(metadata_files[0]) as metadata_file:
        sdist_metadata = email.message_from_bytes(metadata_file.read())
for label, metadata in [("wheel", wheel_metadata), ("source archive", sdist_metadata)]:
    if metadata["Name"] != "figexport" or metadata["Version"] != str(version):
        raise SystemExit(f"Built {label} metadata does not match the release configuration.")
print(f"Validated figexport {version} ({expected_tag}).")
