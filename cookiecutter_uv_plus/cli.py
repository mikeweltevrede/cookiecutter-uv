from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    subprocess.run(["cookiecutter", str(Path(__file__).parents[1])], check=True)  # noqa: S603, S607
