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
