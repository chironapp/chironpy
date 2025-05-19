import numpy as np
from typing import Optional

def fastest_distance_interval(
    distance: np.ndarray,
    window: float = 1000.0
) -> Optional[dict]:
    """
    Finds the shortest number of seconds needed to cover the target_distance
    based on 1Hz-sampled cumulative distance data.

    Args:
        distance (np.ndarray): Cumulative distance array in meters (1Hz sampling).
        window (float): Distance window to evaluate, in meters.

    Returns:
        dict: { "value": seconds, "start_index": i, "stop_index": j }
        None: if no valid interval is found
    """
    best_time = float("inf")
    best_start_idx = best_end_idx = -1
    n = len(distance)

    for i in range(n):
        target = distance[i] + window
        j = np.searchsorted(distance, target, side="left")

        if j >= n:
            break  # Beyond data range

        duration = j - i  # seconds, assuming 1Hz sampling
        if duration < best_time:
            best_time = duration
            best_start_idx = i
            best_end_idx = j

    if best_start_idx == -1:
        return None

    return {
        "value": best_time,
        "distance": window,
        "speed": window / best_time,  # m/s
        "start_index": best_start_idx,
        "stop_index": best_end_idx
    }


def multiple_fastest_distance_intervals(
    distance: np.ndarray,
    windows: list[float]
) -> list[Optional[dict]]:
    """
    Finds the shortest number of seconds needed to cover each target distance
    in the provided list of distance windows.

    Args:
        distance (np.ndarray): Cumulative distance array in meters (1Hz sampling).
        windows (list[float]): List of distance windows to evaluate, in meters.

    Returns:
        list[Optional[dict]]: A list of results for each distance window. Each result is a dictionary:
            { "value": seconds, "start_index": i, "stop_index": j }
            or None if no valid interval is found for a window.
    """
    results = []
    for window in windows:
        result = fastest_distance_interval(distance, window=window)
        results.append(result)
    return results
