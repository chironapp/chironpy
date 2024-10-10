# chironpy

[![Downloads](https://pepy.tech/badge/chiron)](https://pepy.tech/project/chiron)

!!! warning
    **chironpy is currently undergoing major revisions which will result in deprecations and backwards incompatible changes. We recommend pinning your chironpy dependency in your requirements.txt file (e.g. `chiron==0.19.0`).**

!!! tip
    Noticed a missing feature, found a bug or just have a great idea for `chironpy`? Get in touch with us by creating an issue [here](https://github.com/chironapp/chironpy/issues/new)!


## Introduction
chironpy is a Python library that is designed to make workout analysis a breeze. The current state of the project is "very beta": features might be added, removed or changed in backwards incompatible ways. When the time is right a stable version will be released. Get in touch with the contributors or create an issue if you have problems/questions/feature requests/special use cases.

## Installation
This library can be installed from [PyPI](https://pypi.org/project/chiron/):
```bash
pip install chiron
```

## Usage
chironpy supports loading .fit, .tcx and .gpx files. To load a .fit file:
```python
import chiron


data = chiron.read_fit("path/to/file.fit")
```
More information about loading files can be found [here](/features/data_loading/).

The data frames that are returned by chironpy when loading files is similar for different file types.
Read more about this standardization [here](/features/nomenclature/).

## Contributing
See [contributing](contributing.md).

## Contributors
- [Aart Goossens](https://github.com/AartGoossens)
- [Maksym Sladkov](https://github.com/sladkovm)

## License
See [LICENSE](LICENSE) file.
