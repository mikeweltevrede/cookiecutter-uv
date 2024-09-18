from __future__ import annotations

import os
import shlex
import subprocess

from tests.utils import file_contains_text, is_valid_yaml, run_within_dir


def test_bake_project(cookies, repo_root):
    result = cookies.bake(extra_context={"project_name": "my-project"}, template=repo_root)

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "my-project"
    assert result.project_path.is_dir()


def test_using_pytest(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(template=repo_root)

        # Assert that project was created.
        assert result.exit_code == 0
        assert result.exception is None
        assert result.project_path.name == "example-project"
        assert result.project_path.is_dir()
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")

        # Install the uv environment and run the tests.
        with run_within_dir(str(result.project_path)):
            assert subprocess.check_call(shlex.split("uv sync")) == 0
            assert subprocess.check_call(shlex.split("uv run make test")) == 0


def test_devcontainer(cookies, tmp_path, repo_root):
    """Test that the devcontainer files are created when devcontainer=y"""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "y"}, template=repo_root)
        assert result.exit_code == 0
        assert os.path.isfile(f"{result.project_path}/.devcontainer/devcontainer.json")
        assert os.path.isfile(f"{result.project_path}/.devcontainer/postCreateCommand.sh")


def test_not_devcontainer(cookies, tmp_path, repo_root):
    """Test that the devcontainer files are not created when devcontainer=n"""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "n"}, template=repo_root)
        assert result.exit_code == 0
        assert not os.path.isfile(f"{result.project_path}/.devcontainer/devcontainer.json")
        assert not os.path.isfile(f"{result.project_path}/.devcontainer/postCreateCommand.sh")


def test_cicd_contains_pypi_secrets(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "y"}, template=repo_root)
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(f"{result.project_path}/.github/workflows/on-release-main.yml", "PYPI_TOKEN")
        assert file_contains_text(f"{result.project_path}/Makefile", "build-and-publish")


def test_dont_publish(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n"}, template=repo_root)
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            f"{result.project_path}/.github/workflows/on-release-main.yml", "make build-and-publish"
        )


def test_mkdocs(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "y"}, template=repo_root)
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(f"{result.project_path}/.github/workflows/on-release-main.yml", "mkdocs gh-deploy")
        assert file_contains_text(f"{result.project_path}/Makefile", "docs:")
        assert os.path.isdir(f"{result.project_path}/docs")


def test_not_mkdocs(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "n"}, template=repo_root)

        print("Files in repo_root / .github:")
        for root, _, files in os.walk(os.path.join(repo_root, ".github")):
            for file in files:
                print(os.path.join(root, file))

        print("Generated files in .github:")
        for root, _, files in os.walk(result.project_path / ".github"):
            for file in files:
                print(os.path.join(root, file))

        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            f"{result.project_path}/.github/workflows/on-release-main.yml", "mkdocs gh-deploy"
        )
        assert not file_contains_text(f"{result.project_path}/Makefile", "docs:")
        assert not os.path.isdir(f"{result.project_path}/docs")


def test_tox(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(template=repo_root)
        assert result.exit_code == 0
        assert os.path.isfile(f"{result.project_path}/tox.ini")
        assert file_contains_text(f"{result.project_path}/tox.ini", "[tox]")


def test_dockerfile(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "y"}, template=repo_root)
        assert result.exit_code == 0
        assert os.path.isfile(f"{result.project_path}/Dockerfile")


def test_not_dockerfile(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "n"}, template=repo_root)
        assert result.exit_code == 0
        assert not os.path.isfile(f"{result.project_path}/Dockerfile")


def test_codecov(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(template=repo_root)
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert os.path.isfile(f"{result.project_path}/codecov.yaml")
        assert os.path.isfile(f"{result.project_path}/.github/workflows/validate-codecov-config.yml")


def test_not_codecov(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"codecov": "n"}, template=repo_root)
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert not os.path.isfile(f"{result.project_path}/codecov.yaml")
        assert not os.path.isfile(f"{result.project_path}/.github/workflows/validate-codecov-config.yml")


def test_remove_release_workflow(cookies, tmp_path, repo_root):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "y"}, template=repo_root)
        assert result.exit_code == 0
        assert os.path.isfile(f"{result.project_path}/.github/workflows/on-release-main.yml")

        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "n"}, template=repo_root)
        assert result.exit_code == 0
        assert not os.path.isfile(f"{result.project_path}/.github/workflows/on-release-main.yml")
