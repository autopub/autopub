# AutoPub

[![Build Status](https://img.shields.io/circleci/build/github/autopub/autopub)](https://circleci.com/gh/autopub/autopub) [![PyPI Version](https://img.shields.io/pypi/v/autopub)](https://pypi.org/project/autopub/)

AutoPub enables project maintainers to release new package versions to PyPI by merging pull requests.

## Environment

AutoPub is intended for use with continuous integration (CI) systems such as [GitHub Actions][], [CircleCI][], or [Travis CI][]. Projects used with AutoPub are built via [build][] and published via [Twine][]. Contributions that add support for other CI and build systems are welcome.

## Configuration

AutoPub settings can be configured via the `[tool.autopub]` table in the target project’s `pyproject.toml` file. Required settings include Git username and email address:

```toml
[tool.autopub]
git-username = "Your Name"
git-email = "your_email@example.com"
```

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
