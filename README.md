# AutoPub

[![Build Status](https://img.shields.io/circleci/build/github/autopub/autopub)](https://circleci.com/gh/autopub/autopub) [![PyPI Version](https://img.shields.io/pypi/v/autopub)](https://pypi.org/project/autopub/)

AutoPub enables project maintainers to release new package versions to PyPI by merging pull requests.

## Environment

AutoPub is intended for use with continuous integration (CI) systems such as [GitHub Actions][], [CircleCI][], or [Travis CI][]. Projects used with AutoPub are built via [build][] and published via [Twine][]. Contributions that add support for other CI and build systems are welcome.

## Configuration

AutoPub settings can be configured via the `[tool.autopub]` table in the target project's `pyproject.toml` file or via environment variables.

### Git Configuration

You can configure the git username and email used for release commits in three ways:

#### 1. Via pyproject.toml (recommended for project-specific settings)

```toml
[tool.autopub.plugin_config.git]
git-username = "Your Name"
git-email = "your_email@example.com"
```

#### 2. Via environment variables (recommended for CI/CD)

```bash
export GIT_USERNAME="release-bot[bot]"
export GIT_EMAIL="123456+release-bot[bot]@users.noreply.github.com"
```

Environment variables take precedence over pyproject.toml configuration.

#### 3. Default values

If neither environment variables nor pyproject.toml configuration is provided, autopub will use:
- Username: `autopub`
- Email: `autopub@autopub`

### Legacy Configuration

For backward compatibility, the old configuration format is still supported:

```toml
[tool.autopub]
git-username = "Your Name"
git-email = "your_email@example.com"
```

However, this format is deprecated and will be removed in a future release. Please migrate to the plugin_config format shown above.

## Release Files

Contributors should include a `RELEASE.md` file in their pull requests with two bits of information:

* Release type: major, minor, or patch
* Description of the changes, to be used as the changelog entry

Example:

    Release type: patch

    Add function to update version strings in multiple files.

## Usage

The following `autopub` sub-commands can be used as steps in your CI flows:

* `autopub check`: Check whether release file exists.
* `autopub prepare`: Update version strings and add entry to changelog.
* `autopub build`: Build the project.
* `autopub commit`: Add, commit, and push incremented version and changelog changes.
* `autopub githubrelease`: Create a new release on GitHub.
* `autopub publish`: Publish a new release.

For systems such as Travis CI in which only one deployment step is permitted, there is a single command that runs the above steps in sequence:

* `autopub deploy`: Run `prepare`, `build`, `commit`, `githubrelease`, and `publish` in one invocation.


[GitHub Actions]: https://github.com/features/actions
[CircleCI]: https://circleci.com
[Travis CI]: https://travis-ci.org
[build]: https://pypa-build.readthedocs.io
[Twine]: https://twine.readthedocs.io/
