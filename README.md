# chironpy

Endurance sports analysis library for Python

A fork of [sweatpy](https://github.com/GoldenCheetah/sweatpy)

[![Downloads](https://pepy.tech/badge/chiron)](https://pepy.tech/project/chiron)

> :warning: **This is a fork of the original sweatpy project, which no longer seems to be maintained.**

Documentation for the original project can be found [here](https://github.com/GoldenCheetah/sweatpy/blob/master/docs/docs/index.md).

## Documentation

Usage and examples can be found [here](https://chironapp.github.io/chironpy/).

## Publishing

Build and publish using `poetry`.

### TestPyPI

Test using TestPyPI. Create a project-scoped token in TestPyPI. Test publish manually:

```
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --repository testpypi --username __token__ --password pypi-YOURTOKEN
```

Or use the Github Actions as configured in `.github/workflows/publishtestpypi.yml`. Ensure:

- The GitHub repo is connected to the TestPyPI project in TestPyPI.
- The TestPyPI token has been added to the Github repo nvironment secrets: Settings > Environments > testpypi > Envionment secrets > TESTPYPI_TOKEN

```
[testpypi]
  repository = https://test.pypi.org/legacy/
  username = __token__
  password = # either a user-scoped token or a project-scoped token you want to set as the default
```

Install from TestPyPI:

```
pip install chironpy --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/
```

## Development

### Validating functionality

The `examples/` directory contains utility scripts to help validate the functionality of the `chironpy` library during development.

## Contributors

- [Clive Gross](https://github.com/clivegross)
- [Chiron - The endurance training platform](https://github.com/chironapp)

Original authors ([sweatpy](https://github.com/GoldenCheetah/sweatpy)):

- [Maksym Sladkov](https://github.com/sladkovm)
- [Aart Goossens](https://github.com/AartGoossens)

With thanks to:

- [Aaron Schroeder](https://github.com/aaron-schroeder) for work on running power and elevation metrics published in [heartandsole](https://github.com/aaron-schroeder/heartandsole) and [spatialfriend](https://github.com/aaron-schroeder/spatialfriend).

## License

See [LICENSE](LICENSE) file.

```

```
