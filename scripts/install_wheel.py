"""Install exactly the wheel built by CI, never a similarly named PyPI release."""

import subprocess
import sys
from pathlib import Path

wheels = list(Path("dist").glob("*.whl"))
if len(wheels) != 1:
    raise SystemExit(f"Expected exactly one wheel in dist/, found {len(wheels)}.")
result = subprocess.run(
    [sys.executable, "-m", "pip", "install", f"{wheels[0]}[test]"],
    capture_output=True,
    text=True,
    timeout=300,
)
print(result.stdout, end="")
print(result.stderr, end="", file=sys.stderr)
raise SystemExit(result.returncode)
