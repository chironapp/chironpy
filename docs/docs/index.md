# chironpy

Endurance sports analysis library for Python

A fork of [sweatpy](https://github.com/GoldenCheetah/sweatpy)

[![Downloads](https://pepy.tech/badge/chiron)](https://pepy.tech/project/chiron)

> :warning: **This is a fork of the original sweatpy project, which no longer seems to be maintained.**

Documentation for the original project can be found [here](https://github.com/GoldenCheetah/sweatpy/blob/master/docs/docs/index.md).

## Introduction

chironpy is a Python library that is designed to make workout analysis a breeze. The current state of the project is "very beta": features might be added, removed or changed in backwards incompatible ways. When the time is right a stable version will be released. Get in touch with the contributors or create an issue if you have problems/questions/feature requests/special use cases.

## Installation

This library can be installed from [PyPI](https://pypi.org/project/chironpy/):

```bash
pip install chironpy
```

## Usage

chironpy supports loading .fit, .tcx and .gpx files. To load a .fit file:

```python
import chironpy


data = chironpy.read_fit("path/to/file.fit")
```

More information about loading files can be found [here](features/data_loading.md).

The data frames that are returned by chironpy when loading files is similar for different file types.
Read more about this standardization [here](features/nomenclature.md).

## Contributing

See [contributing](contributing.md).

## Contributors

- [Clive Gross](https://github.com/clivegross)
- [Maksym Sladkov](https://github.com/sladkovm) - Original Author
- [Aart Goossens](https://github.com/AartGoossens) - Original Author

## License

See [LICENSE](LICENSE) file.
