# Settings

Configuration settings are read from the `[tool.autopub]` section of the project’s [`pyproject.toml`][] file, which you should add before customizing your configuration via the settings below.

## Required Configuration Settings

**The following configuration settings are required:**

`git-username`
:  Name of the user who will be credited in automated Git commits.

`git-email`
:  Email address for above user, to be used for automated Git commits.

## Optional Configuration Settings

**The following configuration settings are optional, with default values shown in parentheses:**

`project-name`
:  The name of the project. (`tool.poetry.name`)

`append-github-contributor`
:  Append GitHub PR contributor’s name to the changelog entry. (`False`)

`release-file`
:  Name of the release file AutoPub will use as its trigger. (`"RELEASE.md"`)

`changelog-file`
:  Changelog file name, to which AutoPub will append entries. (`"CHANGELOG.md"`)

`changelog-header`
:  Characters used to denote the changelog file’s top-level header. (`"========="`)

`version-header`
:  Character that AutoPub will use as secondary-level version headers. (`"-"`)

`version-strings`
:  File paths (relative to project root) of other files that contain version strings that should be incremented in addition to the [`pyproject.toml`][] file. (`[]`)

`tag-prefix`
:  String to prepend to version numbers — e.g., `"v"` for `v2.0`-style tags. (`""`)

`pypi-url`
:  Publish packages to this PyPI URL, used for Setuptools builds only (`""`)

`build-system`
:  Specify whether `poetry` or `setuptools` will be used for project builds (`build-system.requires`)


[`pyproject.toml`]: https://www.python.org/dev/peps/pep-0518/#specification
