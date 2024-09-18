from __future__ import annotations

import shlex
import subprocess

from tests.utils import file_contains_text, is_valid_yaml, run_within_dir


def test_bake_project(cookies):
    result = cookies.bake(extra_context={"project_name": "my-project"})

    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == "my-project"
    assert result.project_path.is_dir()


def test_using_pytest(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake()

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


def test_devcontainer(cookies, tmp_path):
    """Test that the devcontainer files are created when devcontainer=y"""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "y"})
        assert result.exit_code == 0
        assert (result.project_path / ".devcontainer" / "devcontainer.json").is_file()
        assert (result.project_path / ".devcontainer" / "postCreateCommand.sh").is_file()


def test_not_devcontainer(cookies, tmp_path):
    """Test that the devcontainer files are not created when devcontainer=n"""
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"devcontainer": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / ".devcontainer" / "devcontainer.json").is_file()
        assert not (result.project_path / ".devcontainer" / "postCreateCommand.sh").is_file()


def test_cicd_contains_pypi_secrets(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "y"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(result.project_path / ".github" / "workflows" / "on-release-main.yml", "PYPI_TOKEN")
        assert file_contains_text(result.project_path / "Makefile", "build-and-publish")


def test_dont_publish(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "make build-and-publish"
        )


def test_mkdocs(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "y"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "mkdocs gh-deploy"
        )
        assert file_contains_text(result.project_path / "Makefile", "docs:")
        assert (result.project_path / "docs").is_dir()


def test_not_mkdocs(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"mkdocs": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "on-release-main.yml")
        assert not file_contains_text(
            result.project_path / ".github" / "workflows" / "on-release-main.yml", "mkdocs gh-deploy"
        )
        assert not file_contains_text(result.project_path / "Makefile", "docs:")
        assert not (result.project_path / "docs").is_dir()


def test_tox(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake()
        assert result.exit_code == 0
        assert (result.project_path / "tox.ini").is_file()
        assert file_contains_text(result.project_path / "tox.ini", "[tox]")


def test_dockerfile(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "y"})
        assert result.exit_code == 0
        assert (result.project_path / "Dockerfile").is_file()


def test_not_dockerfile(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"dockerfile": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / "Dockerfile").is_file()


def test_codecov(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake()
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert (result.project_path / "codecov.yaml").is_file()
        assert (result.project_path / ".github" / "workflows" / "validate-codecov-config.yml").is_file()


def test_not_codecov(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"codecov": "n"})
        assert result.exit_code == 0
        assert is_valid_yaml(result.project_path / ".github" / "workflows" / "main.yml")
        assert not (result.project_path / "codecov.yaml").is_file()
        assert not (result.project_path / ".github" / "workflows" / "validate-codecov-config.yml").is_file()


def test_remove_release_workflow(cookies, tmp_path):
    with run_within_dir(tmp_path):
        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "y"})
        assert result.exit_code == 0
        assert (result.project_path / ".github" / "workflows" / "on-release-main.yml").is_file()

        result = cookies.bake(extra_context={"publish_to_pypi": "n", "mkdocs": "n"})
        assert result.exit_code == 0
        assert not (result.project_path / ".github" / "workflows" / "on-release-main.yml").is_file()
