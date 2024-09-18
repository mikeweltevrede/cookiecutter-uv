#!/usr/bin/env python
from __future__ import annotations

import shutil
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()


def remove_file(filepath: str) -> None:
    """Remove the file located at `filepath` from the PROJECT_DIRECTORY.

    :param filepath: Path to the file to remove.
    """
    (PROJECT_DIRECTORY / filepath).unlink()


def remove_dir(dirpath: str) -> None:
    """Remove the directory located at `filepath` from the PROJECT_DIRECTORY.

    :param dirpath: Path to the directory to remove.
    """
    shutil.rmtree(PROJECT_DIRECTORY / dirpath)


if __name__ == "__main__":
    if "{{cookiecutter.include_github_actions}}" != "y":
        remove_dir(".github")
    elif "{{cookiecutter.mkdocs}}" != "y" and "{{cookiecutter.publish_to_pypi}}" == "n":
        remove_file(".github/workflows/on-release-main.yml")

    if "{{cookiecutter.mkdocs}}" != "y":
        remove_dir("docs")
        remove_file("mkdocs.yml")

    if "{{cookiecutter.dockerfile}}" != "y":
        remove_file("Dockerfile")

    if "{{cookiecutter.codecov}}" != "y":
        remove_file("codecov.yaml")
        if "{{cookiecutter.include_github_actions}}" == "y":
            remove_file(".github/workflows/validate-codecov-config.yml")

    if "{{cookiecutter.devcontainer}}" != "y":
        remove_dir(".devcontainer")
