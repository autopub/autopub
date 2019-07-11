# AutoPub

AutoPub enables project maintainers to release new package versions to PyPI by merging pull requests.

## Environment

AutoPub is intended for use with continuous integration (CI) systems and currently supports CircleCI. Projects used with AutoPub are assumed to be managed via [Poetry][].Support for other CI and build systems is planned and contributions adding such support would be welcome.

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
* `autopub commit`: Add, commit, and push incremented version and changelog changes.
* `autopub githubrelease`: Create a new release on GitHub.


[Poetry]: https://poetry.eustace.io
