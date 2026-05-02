import numpy as np
import pytest
from chironpy.metrics.vert import (
    elevation_gain,
    elevation_smooth,
    elevation_smooth_time,
    grade_smooth,
    grade_smooth_time,
)

# Enough points for savgol_filter (window_len=21) after downsampling at sample_len=5m:
# need span >= 21*5 = 105m. Use 300 points at 1m spacing.
DISTANCES = np.arange(0, 300, 1.0)
N = len(DISTANCES)


class TestElevationGain:
    def test_flat(self):
        assert elevation_gain([100.0] * 10) == 0.0

    def test_pure_climb(self):
        elevations = [100.0 + i for i in range(10)]
        assert elevation_gain(elevations) == pytest.approx(9.0)

    def test_pure_descent(self):
        elevations = [100.0 - i for i in range(10)]
        assert elevation_gain(elevations) == 0.0

    def test_mixed(self):
        elevations = [0.0, 10.0, 5.0, 15.0]
        assert elevation_gain(elevations) == pytest.approx(20.0)


class TestElevationSmooth:
    def test_returns_array_same_length(self):
        elevations = np.full(N, 100.0)
        result = elevation_smooth(DISTANCES, elevations)
        assert len(result) == N

    def test_flat_input_stays_flat(self):
        elevations = np.full(N, 100.0)
        result = elevation_smooth(DISTANCES, elevations)
        assert np.allclose(result, 100.0, atol=1e-6)

    def test_linear_ramp_approximately_preserved(self):
        # A perfect linear ramp should survive smoothing with small edge distortion.
        elevations = 100.0 + DISTANCES * 0.05  # 5% grade
        result = elevation_smooth(DISTANCES, elevations)
        # Interior values (away from edges) should be close to original
        interior = slice(30, N - 30)
        assert np.allclose(result[interior], elevations[interior], atol=1.0)

    def test_noisy_input_is_smoothed(self):
        rng = np.random.default_rng(42)
        elevations = 100.0 + DISTANCES * 0.05 + rng.normal(0, 2.0, N)
        result = elevation_smooth(DISTANCES, elevations)
        # Smoothed output should have lower variance than noisy input
        assert result.std() < elevations.std()


class TestElevationSmoothTime:
    def test_returns_array_same_length(self):
        elevations = np.full(N, 100.0)
        result = elevation_smooth_time(elevations)
        assert len(result) == N

    def test_flat_input_stays_flat(self):
        elevations = np.full(N, 100.0)
        result = elevation_smooth_time(elevations)
        assert np.allclose(result, 100.0, atol=1e-6)


class TestGradeSmooth:
    def test_returns_array_same_length(self):
        elevations = np.full(N, 100.0)
        result = grade_smooth(DISTANCES, elevations)
        assert len(result) == N

    def test_flat_course_near_zero_grade(self):
        elevations = np.full(N, 100.0)
        result = grade_smooth(DISTANCES, elevations)
        assert np.allclose(result, 0.0, atol=1e-6)

    def test_linear_climb_positive_grade(self):
        elevations = 100.0 + DISTANCES * 0.05
        result = grade_smooth(DISTANCES, elevations)
        interior = slice(30, N - 30)
        assert np.all(result[interior] > 0)


class TestGradeSmoothTime:
    def test_returns_array_same_length(self):
        elevations = np.full(N, 100.0)
        result = grade_smooth_time(DISTANCES, elevations)
        assert len(result) == N

    def test_flat_course_near_zero_grade(self):
        elevations = np.full(N, 100.0)
        result = grade_smooth_time(DISTANCES, elevations)
        assert np.allclose(result, 0.0, atol=1e-6)


class TestShortRecordings:
    """Regression tests for recordings shorter than the SG filter window."""

    def test_elevation_smooth_time_short_data_no_error(self):
        # 2-second recording: fewer points than default window_len=21
        elevations = [100.0, 101.0]
        result = elevation_smooth_time(elevations)
        assert len(result) == 2

    def test_elevation_smooth_time_single_point(self):
        result = elevation_smooth_time([100.0])
        assert len(result) == 1

    def test_grade_smooth_time_short_data_no_error(self):
        distances = [0.0, 5.0]
        elevations = [100.0, 101.0]
        result = grade_smooth_time(distances, elevations)
        assert len(result) == 2

    def test_elevation_smooth_time_window_boundary(self):
        # Exactly window_len - 1 points (20 points, default window=21)
        elevations = np.full(20, 100.0)
        result = elevation_smooth_time(elevations)
        assert len(result) == 20
