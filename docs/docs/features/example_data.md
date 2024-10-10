# Example data

*chironpy* comes included with a range of example data for testing purposes.

An index of the data is kept [here](https://github.com/chironapp/chironpy/blob/master/chiron/examples/index.yml).

```python
import json

import chiron

example_fit = chiron.examples(path='4078723797.fit')
```

You can use the example data for testing:

```python
import chiron

data = chiron.read_fit(example_fit.path)
```

If you are looking for a specific file type or sport you can also filter the example data, which returns a [filter](https://docs.python.org/3/library/functions.html#filter) iterable that you can iterator over:
```
import chiron

examples = chiron.examples(
    file_type=chiron.FileTypeEnum.fit,
    sport=chiron.SportEnum.cycling)

for example in examples:
    # Do fancy things with example data...
```
