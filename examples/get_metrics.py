import sys
import os
from pathlib import Path
from chironpy.metrics.speed import multiple_fastest_distance_intervals
from chironpy.metrics.vert import elevation_gain
from chironpy.metrics.core import best_interval, best_distance_interval

# # Add the project directory to sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chironpy


# example = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
# data = chironpy.read_file(example.path, resample=True, interpolate=True)
print('loading example marathon data from FIT file')
example1 = os.path.join('chironpy', 'examples', 'data', '18360138543_ACTIVITY_Osaka_Marathon_2025.fit')
data1 = chironpy.read_file(example1, resample=True, interpolate=True)
print('loading same example marathon data from locally saved strava streams json file')
example2 = os.path.join('chironpy', 'examples', 'data', '74d893f7-1349-4b2c-ac5f-60246396b8b1_local_strava_Osaka_Marathon_2025.json')
data2 = chironpy.read_file(example2, resample=True, interpolate=True)

print(data1.columns)
print(data1.head())
print(data2.columns)
print(data2.head())
# mmp = data1["enhanced_speed"].chironpy.mean_max()
# print(mmp)
# mmp = data2["speed"].chironpy.mean_max()
# print(mmp)

print("enhanced_speed")
print(data1["enhanced_speed"])
print(data2["speed"])
print("speed compare")
# print(data1["enhanced_speed"] - data2["speed"])

# best1 = chironpy.metrics.core.best_distance_interval(data1['distance'])
# print(best1)
distances = [1000, 1500, 1609, 5000, 10000, 21100, 30000, 42195, 50000]
bests1 = multiple_fastest_distance_intervals(data1['distance'], windows=distances)
print(f'best efforts over {distances} for {example1}')
for i, best in enumerate(bests1):
    if best is None:
        pace = None
    else:
        pace = best['value']/60 / distances[i] * 1000
    print(str(distances[i] / 1000) + 'km', pace, best)


# best2 = chironpy.metrics.core.best_distance_interval(data2['distance'])
# print(best2)
bests2 = multiple_fastest_distance_intervals(data2['distance'], windows=distances)
print(f'best efforts over {distances} for {example2}')
for i, best in enumerate(bests2):
    if best is None:
        pace = None
    else:
        pace = best['value']/60 / distances[i] * 1000
    print(str(distances[i] / 1000) + 'km', pace, best)