# Examples

Following is a real-world example that depends on:

* CI via GitHub Actions
* Primary branch named `main`
* Configured environment named `Release`
* `Release` environment variable `GH_TOKEN` defined with personal access token
* Preceding `test` and `lint` jobs that must complete successfully
* Existence of a `RELEASE.md` file in project root

```yaml
# .github/workflows/release.yml

[…]

jobs:

  test:
  […]

  lint:
  […]

  release:
    name: Release
    environment: Release
    needs: [test, lint]
    runs-on: ubuntu-latest
    if: ${{ github.ref=='refs/heads/main' && github.event_name!='pull_request' }}

    steps:
      - uses: actions/checkout@v3
        with:
          token: ${{ secrets.GH_TOKEN }}

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Check release
        id: check_release
        run: |
          python -m pip install autopub[github]
          autopub check

      - name: Publish
        if: ${{ steps.check_release.outputs.autopub_release=='true' }}
        env:
          GITHUB_TOKEN: ${{ secrets.GH_TOKEN }}
        run: |
          autopub prepare
          autopub commit
          autopub build
          autopub githubrelease
          autopub publish
```
