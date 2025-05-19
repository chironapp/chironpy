# Example data

_chironpy_ comes included with a range of example data for testing purposes.

An index of the data is kept [here](https://github.com/chironapp/chironpy/blob/master/chiron/examples/index.yml).

```python
import json

import chironpy

example_fit = chironpy.examples(path='4078723797.fit')
```

You can use the example data for testing:

```python
import chironpy

data = chironpy.read_fit(example_fit.path)
```

If you are looking for a specific file type or sport you can also filter the example data, which returns a [filter](https://docs.python.org/3/library/functions.html#filter) iterable that you can iterator over:

```
import chironpy

examples = chironpy.examples(
    file_type=chironpy.FileTypeEnum.fit,
    sport=chironpy.SportEnum.cycling)

for example in examples:
    # Do fancy things with example data...
```
