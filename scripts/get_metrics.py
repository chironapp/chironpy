import sys
import os
from pathlib import Path

# # Add the project directory to sys.path
# sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import chironpy


# example = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
# data = chironpy.read_file(example.path, resample=True, interpolate=True)
example1 = os.path.join('chironpy', 'examples', 'data', '18360138543_ACTIVITY_Osaka_Marathon_2025.fit')
data1 = chironpy.read_file(example1, resample=True, interpolate=True)

example2 = os.path.join('chironpy', 'examples', 'data', '74d893f7-1349-4b2c-ac5f-60246396b8b1_local_strava_Osaka_Marathon_2025.json')
data2 = chironpy.read_file(example2, resample=True, interpolate=True)

print(data1.columns)
print(data2.columns)
mmp = data2["speed"].chironpy.mean_max()
print(mmp)

best1 = chironpy.metrics.core.best_distance_interval(data1['distance'])
print(best1)

best2 = chironpy.metrics.core.best_distance_interval(data2['distance'])
print(best2)

