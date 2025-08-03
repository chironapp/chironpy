import pytest
import pandas as pd
import numpy as np
from chironpy.models.workout import WorkoutData


class TestWorkoutData:
    """Test cases for WorkoutData class."""
    
    def create_sample_workout(self, start_time, duration_seconds=10, speed_values=None):
        """Helper method to create a sample WorkoutData object."""
        if speed_values is None:
            speed_values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        # Ensure we have the right number of values
        if len(speed_values) != duration_seconds:
            # Interpolate or repeat to match duration
            speed_values = np.interp(
                np.linspace(0, len(speed_values)-1, duration_seconds),
                range(len(speed_values)),
                speed_values
            )
        
        data = {
            'speed': speed_values,
            'power': np.arange(100, 100 + duration_seconds * 10, 10),
            'heartrate': np.arange(120, 120 + duration_seconds * 2, 2),
            'distance': np.cumsum([0] + [1] * (duration_seconds - 1)),
            'elevation': np.arange(0, duration_seconds, 1)
        }
        
        # Create datetime index
        time_index = pd.date_range(start_time, periods=duration_seconds, freq='1S')
        df = pd.DataFrame(data, index=time_index)
        df.index.name = 'time'
        
        return WorkoutData.from_raw(df, resample=True, interpolate=True)
    
    def test_merge_many_empty_list(self):
        """Test merge_many with empty list raises ValueError."""
        with pytest.raises(ValueError, match="Cannot merge empty list"):
            WorkoutData.merge_many([])
    
    def test_merge_many_invalid_types(self):
        """Test merge_many with non-WorkoutData objects raises ValueError."""
        workout1 = self.create_sample_workout(pd.Timestamp('2025-01-01 10:00:00'))
        with pytest.raises(ValueError, match="All items must be WorkoutData objects"):
            WorkoutData.merge_many([workout1, "not a workout"])
    
    def test_merge_many_single_workout(self):
        """Test merge_many with single workout returns copy."""
        workout = self.create_sample_workout(pd.Timestamp('2025-01-01 10:00:00'))
        result = WorkoutData.merge_many([workout])
        
        # Should be a copy, not the same object
        assert result is not workout
        # But should have the same data
        pd.testing.assert_frame_equal(result, workout)
    
    def test_merge_many_two_workouts_non_overlapping(self):
        """Test merging two workouts with non-overlapping time ranges."""
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=5,
            speed_values=[1, 2, 3, 4, 5]
        )
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'),  # 10 minutes later
            duration_seconds=5,
            speed_values=[6, 7, 8, 9, 10]
        )
        
        result = WorkoutData.merge_many([workout1, workout2])
        
        # Check total duration
        expected_duration = 10  # 5 + 1 gap + 5 - 1 (last second overlaps conceptually)
        assert len(result) == expected_duration
        
        # Check that workouts are continuous in time column
        assert 'time' in result.columns
        time_values = result['time'].values
        assert time_values[0] == 0  # First workout starts at 0
        assert time_values[4] == 4   # First workout ends at 4
        assert time_values[5] == 5   # Second workout starts at 5
        assert time_values[-1] == 9  # Second workout ends at 9
        
        # Check speed values are preserved
        assert list(result['speed'].iloc[:5]) == [1, 2, 3, 4, 5]
        assert list(result['speed'].iloc[5:]) == [6, 7, 8, 9, 10]
    
    def test_merge_many_chronological_sorting(self):
        """Test that workouts are sorted chronologically."""
        # Create workouts in reverse chronological order
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'), 
            duration_seconds=3,
            speed_values=[6, 7, 8]
        )
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'),
            duration_seconds=3,
            speed_values=[1, 2, 3]
        )
        
        result = WorkoutData.merge_many([workout2, workout1])  # Note: wrong order
        
        # Should still be sorted correctly
        assert list(result['speed'].iloc[:3]) == [1, 2, 3]  # workout1 first
        assert list(result['speed'].iloc[3:]) == [6, 7, 8]  # workout2 second
    
    def test_merge_many_distance_continuity(self):
        """Test that distance is continuous across merged workouts."""
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=3
        )
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'),
            duration_seconds=3
        )
        
        result = WorkoutData.merge_many([workout1, workout2])
        
        # Distance should be continuous
        distance_values = result['distance'].values
        max_workout1_distance = workout1['distance'].iloc[-1]
        
        # Second workout should start where first ended
        assert distance_values[3] == max_workout1_distance + workout2['distance'].iloc[0]
    
    def test_merge_many_metadata_properties(self):
        """Test that metadata properties work correctly on merged data."""
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=5
        )
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'),
            duration_seconds=5
        )
        
        result = WorkoutData.merge_many([workout1, workout2])
        
        # Check start and end times
        assert result.start_time == workout1.start_time
        # End time should be the adjusted end time of workout2
        
        # Check duration
        expected_duration = 9  # 5 + 5 - 1 (for the gap)
        assert result.duration == expected_duration
    
    def test_merge_many_derived_columns(self):
        """Test that derived columns are recomputed correctly."""
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=3
        )
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'),
            duration_seconds=3
        )
        
        result = WorkoutData.merge_many([workout1, workout2])
        
        # Check that is_moving column exists and is computed correctly
        assert 'is_moving' in result.columns
        # All our test speeds are > 0.5, so should all be True
        assert all(result['is_moving'])
    
    def test_merge_many_three_workouts(self):
        """Test merging three workouts."""
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=2,
            speed_values=[1, 2]
        )
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:05:00'),
            duration_seconds=2,
            speed_values=[3, 4]
        )
        workout3 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:15:00'),
            duration_seconds=2,
            speed_values=[5, 6]
        )
        
        result = WorkoutData.merge_many([workout1, workout2, workout3])
        
        # Should have 6 total records (2 + 2 + 2)
        assert len(result) == 6
        
        # Check speed continuity
        expected_speeds = [1, 2, 3, 4, 5, 6]
        assert list(result['speed']) == expected_speeds
        
        # Check time continuity
        expected_times = [0, 1, 2, 3, 4, 5]
        assert list(result['time']) == expected_times
    
    def test_merge_many_preserves_all_columns(self):
        """Test that all columns from all workouts are preserved."""
        # Create workout with extra column
        workout1 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=2
        )
        workout1['cadence'] = [80, 85]
        
        workout2 = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:10:00'),
            duration_seconds=2
        )
        workout2['temperature'] = [20, 21]
        
        result = WorkoutData.merge_many([workout1, workout2])
        
        # Should have all columns from both workouts
        expected_columns = set(workout1.columns) | set(workout2.columns)
        assert set(result.columns) == expected_columns
        
        # Check that missing values are handled (should be NaN)
        assert pd.isna(result['cadence'].iloc[2])  # workout2 doesn't have cadence
        assert pd.isna(result['temperature'].iloc[0])  # workout1 doesn't have temperature
    
    def test_workout_data_properties(self):
        """Test basic WorkoutData properties."""
        workout = self.create_sample_workout(
            pd.Timestamp('2025-01-01 10:00:00'), 
            duration_seconds=5
        )
        
        assert workout.start_time == pd.Timestamp('2025-01-01 10:00:00')
        assert workout.end_time == pd.Timestamp('2025-01-01 10:00:04')
        assert workout.duration == 4  # 0, 1, 2, 3, 4 seconds
        
        # Test with empty workout
        empty_workout = WorkoutData(pd.DataFrame())
        assert empty_workout.start_time is None
        assert empty_workout.end_time is None
        assert empty_workout.duration == 0
