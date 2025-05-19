import os
import chironpy
from chironpy import WorkoutData

print('Loading example marathon data from FIT file...')
# example1 = chironpy.examples(path="18360138543_ACTIVITY_Osaka_Marathon_2025.fit")
example1 = os.path.join('chironpy', 'examples', 'data', '18360138543_ACTIVITY_Osaka_Marathon_2025.fit')
data1 = WorkoutData.from_file(example1)

print('loading same example marathon data from locally saved strava streams json file')
# example2 = chironpy.examples(path="74d893f7-1349-4b2c-ac5f-60246396b8b1_local_strava_Osaka_Marathon_2025.json")
example2 = os.path.join('chironpy', 'examples', 'data', '74d893f7-1349-4b2c-ac5f-60246396b8b1_local_strava_Osaka_Marathon_2025.json')
data2 = WorkoutData.from_file(example2)

print('\nWorkoutData from FIT file:')
print(data1.columns)
print(data1.head())
print('\nWorkoutData from locally saved Strava streams:')
print(data2.columns)
print(data2.head())

print(data1["speed"])
print(data2["speed"])


distances = [1000, 5000, 10000, 21100]
durations = [30, 60, 120, 180, 300, 600, 1200, 1800, 3600]
fastest1 = data1.fastest_distance_intervals(distances)
best_hr1 = data1.best_distance_intervals(distances, 'heartrate')
print(f'\n####\nBest efforts over {distances} meters for {example1}')
for i, best in enumerate(fastest1):
    if best is None:
        pace = None
    else:
        pace = best['value']/60 / distances[i] * 1000
    print(str(distances[i] / 1000) + 'km', pace, best, "heartrate:", best_hr1[i])

print(f'\n####\nBest efforts over {durations} seconds for {example1}')
fastest1 = data1.best_intervals(durations, 'speed')
best_hr1 = data1.best_intervals(durations, 'heartrate')
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

print('\n\n####')
print(f'Total elevation gain for {example1}: {data1.elevation_gain()} m')
print(f'Total elevation gain for {example2}: {data2.elevation_gain()} m')
# print(best2)
bests2 = data2.fastest_distance_intervals(distances)
print(f'\n\n####\nBest efforts over {distances} for {example2}')
for i, best in enumerate(bests2):
    pace = best['value']/60 / distances[i] * 1000
    print(distances[i], pace, best)