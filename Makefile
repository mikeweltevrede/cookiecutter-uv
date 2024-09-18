.PHONY: bake
bake: ## bake without inputs and overwrite if exists.
	@uv run cookiecutter --no-input . --overwrite-if-exists

.PHONY: bake-with-inputs
bake-with-inputs: ## bake with inputs and overwrite if exists.
	@uv run cookiecutter . --overwrite-if-exists

.PHONY: bake-and-test-deploy
bake-and-test-deploy: ## For quick publishing to cookiecutter-uv-plus-example to test GH Actions
	@rm -rf cookiecutter-uv-plus-example || true
	@uv run cookiecutter --no-input . --overwrite-if-exists \
		author="Mike Weltevrede" \
		email="mikeweltevrede@gmail.com" \
		github_author_handle=mikeweltevrede \
		project_name=cookiecutter-uv-plus-example \
		project_slug=cookiecutter_uv_plus_example
	@cd cookiecutter-uv-plus-example; uv sync && \
		git init -b main && \
		git add . && \
		uv run pre-commit install && \
		uv run pre-commit run -a || true && \
		git add . && \
		uv run pre-commit run -a || true && \
		git add . && \
		git commit -m "init commit" && \
		git remote add origin git@github.com:mikeweltevrede/cookiecutter-uv-plus-example.git && \
		git push -f origin main

.PHONY: install
install: ## Install the virtual environment
	@echo "🚀 Creating virtual environment"
	@uv sync

.PHONY: check
check: ## Run code quality tools.
	@echo "🚀 Checking lock file consistency with 'pyproject.toml'"
	@uv sync --locked
	@echo "🚀 Linting code: Running pre-commit"
	@uv run pre-commit run -a
	@echo "🚀 Static type checking: Running mypy"
	@uv run mypy
	@echo "🚀 Checking for obsolete dependencies: Running deptry"
	@uv run deptry .

.PHONY: test
test: ## Test the code with pytest.
	@echo "🚀 Testing code: Running pytest"
	@uv run python -m pytest --cov --cov-config=pyproject.toml --cov-report=xml tests

.PHONY: build
build: clean-build ## Build wheel file
	@echo "🚀 Creating wheel file"
	@uvx --from build pyproject-build --installer uv

.PHONY: clean-build
clean-build: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	@uv run python -c "import shutil; import os; shutil.rmtree('dist') if os.path.exists('dist') else None"

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing: Dry run."
	@uvx --from build pyproject-build --installer uv
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: update
update: ## Add upstream remote and merge upstream/main branch (fail if not on main-plus to avoid moving commits on a checkout)
	@echo "🚀 Updating branch with upstream/main"

ifeq ($(REQUIRE_MAIN_PLUS), true)
	@echo "🚀 Checking if on main-plus branch, and updating"
	@[ "$(shell git rev-parse --abbrev-ref HEAD)" = "main-plus" ] || (echo "❌ Error: You are not on the main-plus branch." && exit 1)
endif

	@echo "🚀 Updating this branch from origin"
	@git fetch origin
	@git pull

ifeq ($(NEW_BRANCH), true)
	@echo "🚀 Setting up branch feature/update-from-upstream/dev"
	@git checkout -b feature/update-from-upstream/dev
endif

	@echo "🚀 Merging upstream/main"
	@git remote add upstream https://github.com/fpgmaas/cookiecutter-uv || true
	@git fetch upstream && git merge upstream/main

.PHONY: update-with-main
update-with-main:
	@echo "🚀 Updating branch with origin/main"
	@git fetch origin && git merge origin/main

.PHONY: update-with-main-plus
update-with-main-plus:
	@echo "🚀 Updating branch with origin/main-plus"
	@git fetch origin && git merge origin/main-plus

.PHONY: docs-test
docs-test: ## Test if documentation can be built without warnings or errors
	@uv run mkdocs build -s

.PHONY: docs
docs: ## Build and serve the documentation
	@uv run mkdocs serve

.PHONY: help
help:
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
