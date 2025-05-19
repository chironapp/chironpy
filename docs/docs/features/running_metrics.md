# Running Metrics

Get best efforts (fastest times), best heart rate, elevation etc for a list of distances or durations within an activity file.

## Use the `WorkoutData` class

Load the file into a `WorkoutData` instance:

```python
import chironpy
from chironpy import WorkoutData

print('Loading example marathon data from FIT file...')
example1 = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
data1 = WorkoutData.from_file(example1)

print('\nWorkoutData from FIT file:')
print(data1.columns)
print(data1.head())

```

Outputs:

```
WorkoutData from FIT file:
Index(['latitude', 'longitude', 'distance', 'unknown_87', 'heartrate',
       'cadence', 'temperature', 'fractional_cadence', 'unknown_135',
       'unknown_136', 'record_sequence', 'unknown_90', 'session', 'lap',
       'speed', 'elevation', 'time', 'is_moving', 'grade'],
      dtype='object')
                            latitude   longitude  distance  unknown_87  heartrate  ...   speed  elevation  time  is_moving     grade
datetime                                                                           ...
2025-02-24 00:15:21+00:00  34.686225  135.520607     0.000       146.0       80.0  ...  1.7640      23.40     0       True  0.000000
2025-02-24 00:15:22+00:00  34.686248  135.520601     2.572       116.8       80.8  ...  1.8778      23.36     1       True -0.029455
2025-02-24 00:15:23+00:00  34.686270  135.520595     5.144        87.6       81.6  ...  1.9916      23.32     2       True -0.029933
2025-02-24 00:15:24+00:00  34.686293  135.520589     7.716        58.4       82.4  ...  2.1054      23.28     3       True -0.030411
2025-02-24 00:15:25+00:00  34.686316  135.520583    10.288        29.2       83.2  ...  2.2192      23.24     4       True -0.030890

[5 rows x 19 columns]
```

Compute fastest efforts, maximum average heart rate etc over a range of distances within the workout:

```python
distances = [1000, 5000, 10000, 21100]

fastest1 = data1.fastest_distance_intervals(distances)
best_hr1 = data1.best_distance_intervals(distances, 'heartrate')

print(f'\n####\nBest efforts over {distances} meters for {example1}')
for i, best in enumerate(fastest1):
    if best is None:
        pace = None
    else:
        pace = best['value']/60 / distances[i] * 1000
    print(str(distances[i] / 1000) + 'km', pace, best, "heartrate:", best_hr1[i])
```

Outputs:

```
####
Best efforts over [1000, 5000, 10000, 21100] meters for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit
1.0km 3.1666666666666665 {'value': 190, 'distance': 1000, 'speed': 5.2631578947368425, 'start_index': 5845, 'stop_index': 6035} heartrate: {'value': 194.14252336448598, 'start_index': 3896, 'stop_index': 4110}
5.0km 3.356666666666667 {'value': 1007, 'distance': 5000, 'speed': 4.965243296921549, 'start_index': 574, 'stop_index': 1581} heartrate: {'value': 192.1921606118547, 'start_index': 3540, 'stop_index': 4586}
10.0km 3.405 {'value': 2043, 'distance': 10000, 'speed': 4.894762604013706, 'start_index': 483, 'stop_index': 2526} heartrate: {'value': 191.01557259223767, 'start_index': 2562, 'stop_index': 4649}
21.1km 3.4368088467614535 {'value': 4351, 'distance': 21100, 'speed': 4.849459894277178, 'start_index': 156, 'stop_index': 4507} heartrate: {'value': 188.79730962152303, 'start_index': 2733, 'stop_index': 7119}
```

Or compute fastest efforts, max average heart rate etc over a range of durations:

```python
durations = [30, 60, 120, 180, 300, 600, 1200, 1800, 3600]

fastest1 = data1.best_intervals(durations, 'speed')
best_hr1 = data1.best_intervals(durations, 'heartrate')

print(f'\n####\nBest efforts over {durations} seconds for {example1}')
for i, best in enumerate(fastest1):
    if best is None:
        pace = None
    else:
        pace = best['value']/60 / durations[i] * 1000
    print(str(durations[i] / 60) + 'min', pace, best, "heartrate:", best_hr1[i])

best_20min_hr = data1.best_intervals(1200, 'heartrate')[0]
print(f'\n####\nBest 20min heartrate for {example1}: {best_20min_hr} bpm')
best_5k_hr = data1.fastest_distance_intervals(5000, 'heartrate')[0]
print(f'Best 5k heartrate for {example1}: {best_5k_hr} bpm')
```

Outputs:

```
####
Best efforts over [30, 60, 120, 180, 300, 600, 1200, 1800, 3600] seconds for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit
0.5min 2.948777777777778 {'value': 5.3078, 'start_index': 759, 'stop_index': 789} heartrate: {'value': 200.1, 'start_index': 4073, 'stop_index': 4103}
1.0min 1.4249706018518515 {'value': 5.1298941666666655, 'start_index': 745, 'stop_index': 805} heartrate: {'value': 199.125, 'start_index': 4041, 'stop_index': 4101}
2.0min 0.7000248842592592 {'value': 5.040179166666666, 'start_index': 500, 'stop_index': 620} heartrate: {'value': 196.74166666666667, 'start_index': 4018, 'stop_index': 4138}
3.0min 0.4646144547325102 {'value': 5.0178361111111105, 'start_index': 442, 'stop_index': 622} heartrate: {'value': 194.50277777777777, 'start_index': 3957, 'stop_index': 4137}
5.0min 0.27489444444444444 {'value': 4.9481, 'start_index': 262, 'stop_index': 562} heartrate: {'value': 193.435, 'start_index': 3849, 'stop_index': 4149}
10.0min 0.13661450462962962 {'value': 4.918122166666667, 'start_index': 230, 'stop_index': 830} heartrate: {'value': 192.84483333333333, 'start_index': 3540, 'stop_index': 4140}
20.0min 0.0670034201388889 {'value': 4.824246250000001, 'start_index': 4395, 'stop_index': 5595} heartrate: {'value': 192.175, 'start_index': 3373, 'stop_index': 4573}
30.0min 0.044466041666666664 {'value': 4.8023324999999994, 'start_index': 3966, 'stop_index': 5766} heartrate: {'value': 191.59044444444444, 'start_index': 2720, 'stop_index': 4520}
60.0min 0.021955931712962964 {'value': 4.742481250000001, 'start_index': 2865, 'stop_index': 6465} heartrate: {'value': 189.61708333333334, 'start_index': 2137, 'stop_index': 5737}

####
Best 20min heartrate for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit: {'value': 192.175, 'start_index': 3373, 'stop_index': 4573} bpm
Best 5k heartrate for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit: None bpm

```

Elevation gain:

```python
print(f'Total elevation gain for {example1}: {data1.elevation_gain()} m')
```

Outputs:

```
Total elevation gain for chironpy/examples/data/18360138543_ACTIVITY_Osaka_Marathon_2025.fit: 286.0000000000019 m
```

## Analyse workout file directly

```python
import os
import chironpy

example = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
data = chironpy.read_file(example.path, resample=True, interpolate=True)

distances = [1000, 1500, 1608, 3000, 5000, 10000, 21100, 30000, 42200] # in metres
bests = chironpy.metrics.speed.multiple_fastest_distance_intervals(
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
