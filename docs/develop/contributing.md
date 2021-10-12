# Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

## Development Environment

AutoPub is built with [Poetry][], so if you don’t already have it installed, the first step is to install it by following the [Poetry Installation Documentation][].

Once [Poetry][] is installed, follow the steps below to install AutoPub for development:

```shell
git clone https://github.com/autopub/autopub
cd autopub
poetry install
```

## Building the Documentation

AutoPub’s documentation is found in `docs/`. Build the documentation via:

```shell
poetry run invoke docbuild
```

To build and serve the documentation in one step, run the following command and then open http://localhost:8000 in your browser:

```shell
poetry run invoke docserve
```

When you make changes to the documentation, it should be automatically re-built after a few moments, and the browser window should automatically refresh and display your changes (as long as there were no build errors). If you don’t see the expected changes, switch back to your terminal console and see if there were any build errors.


[existing issues]: https://github.com/autopub/autopub/issues
[Poetry]: https://python-poetry.org/
[Poetry Installation Documentation]: https://python-poetry.org/docs/master/#installation
