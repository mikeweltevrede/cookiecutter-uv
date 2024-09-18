.PHONY: bake
bake: ## bake without inputs and overwrite if exists.
	@cookiecutter --no-input . --overwrite-if-exists

.PHONY: bake-with-inputs
bake-with-inputs: ## bake with inputs and overwrite if exists.
	@cookiecutter . --overwrite-if-exists

.PHONY: bake-and-test-deploy
bake-and-test-deploy: ## For quick publishing to cookiecutter-uv-example to test GH Actions
	@rm -rf cookiecutter-uv-example || true
	@cookiecutter --no-input . --overwrite-if-exists \
		author="Mike Weltevrede" \
		email="mikeweltevrede@gmail.com" \
		github_author_handle=mikeweltevrede \
		project_name=cookiecutter-uv-plus-example \
		project_slug=cookiecutter_uv_plus_example
	@cd cookiecutter-uv-example; uv sync && \
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
clean-build: ## clean build artifacts
	@rm -rf dist

.PHONY: publish
publish: ## Publish a release to PyPI.
	@echo "🚀 Publishing: Dry run."
	@uvx --from build pyproject-build --installer uv
	@echo "🚀 Publishing."
	@uvx twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

.PHONY: build-and-publish
build-and-publish: build publish ## Build and publish.

.PHONY: update
update: ## Add upstream remote and merge upstream main branch (fail if not on main to avoid moving commits on a checkout)
	@echo "🚀 Updating main branch from upstream"
	@echo "🚀 Checking if on main branch, and updating"
	@[ "$(shell git rev-parse --abbrev-ref HEAD)" = "main" ] || (echo "❌ Error: You are not on the main branch." && exit 1)
	@git pull
	@echo "🚀 Checking out to branch feature/update-from-upstream/dev"
	@git checkout -b feature/update-from-upstream/dev
	@echo "🚀 Merging upstream/main"
	@git remote add upstream https://github.com/fpgmaas/cookiecutter-uv || true
	@git fetch upstream && git merge upstream/main
	@git push
ifeq ($(CLEANUP), true)
	@echo "🚀 Checking out to main branch and deleting feature/update-from-upstream/dev locally"
	@git checkout main && git branch -D feature/update-from-upstream/dev
else
	@echo "🚫 Skipping checkout to main branch and deleting feature branch locally (use 'make update CLEANUP=true' to enable)"
endif

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
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
