As mentioned in [README.md](../README.md), this was forked from [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv) with the intention of expanding on the template with more specific configurations that I like to apply to my own projects. This does not make sense to merge to the original repository because it would make the template too restrictive. The changes can be found in the `main-plus` branch.

In this document, I will outline the changes made in comparison to the upstream repository.

# Ruff rules

Compared to the upstream, I am much stricter in the code quality checks selected through `ruff`. I select more rules and specify settings to be stricter, e.g. for `flake8-type-checking` I set `strict` to `true`.
