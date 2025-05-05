# chironpy

Endurance sports analysis library for Python

A fork of [sweatpy](https://github.com/GoldenCheetah/sweatpy)

[![Downloads](https://pepy.tech/badge/chiron)](https://pepy.tech/project/chiron)

> :warning: **This is a fork of the original chironpy project, which is currently undergoing major revisions. These revisions may result in deprecations and backwards incompatible changes. We recommend pinning your chironpy dependency in your requirements.txt file (e.g. `sweat==0.19.0`).**

Documentation for the original project can be found [here](https://github.com/GoldenCheetah/sweatpy/blob/master/docs/docs/index.md).

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

## Contributors

- [Clive Gross](https://github.com/clivegross)
- [Maksym Sladkov](https://github.com/sladkovm) - Original Author
- [Aart Goossens](https://github.com/AartGoossens) - Original Author

## License

See [LICENSE](LICENSE) file.
