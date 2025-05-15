# Running Metrics

Get best efforts (fastest times) for a list of distances:

```python
import os
import chironpy

example = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
data = chironpy.read_file(example.path, resample=True, interpolate=True)

distances = [1000, 5000, 10000, 21100] # in metres
bests = chironpy.metrics.core.multiple_best_distance_intervals(
    data['distance'],
    windows=distances
)
print(f'best efforts over {distances}m for {example}')
for i, best in enumerate(bests):
    pace = best['value']/60 / distances[i] * 1000 # min/km
    print(str(distances[i]/1000) + 'km', pace, best)

```

Outputs:

```
best efforts over [1000, 5000, 10000, 21100] for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit
1.0km 3.1666666666666665 {'value': 190, 'start_index': 5845, 'stop_index': 6035}
5.0km 3.356666666666667 {'value': 1007, 'start_index': 574, 'stop_index': 1581}
10.0km 3.405 {'value': 2043, 'start_index': 483, 'stop_index': 2526}
21.1km 3.4368088467614535 {'value': 4351, 'start_index': 156, 'stop_index': 4507}
```

Or use the new `WorkoutData` class:

```python
import os
from chironpy import examples, WorkoutData

example = examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
data = WorkoutData.from_file(example.path)

distances = [1000, 5000, 10000, 21100] # in metres
bests = data.best_distance_intervals(
    windows=distances
)
print(f'best efforts over {best_distances}m for {example}')
for i, best in enumerate(bests):
    pace = best['value']/60 / distances[i] * 1000 # min/km
    print(str(distances[i]/1000) + 'km', pace, best)

```

Outputs the same as the previous example.
