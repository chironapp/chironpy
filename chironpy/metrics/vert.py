# Credit to @aaron-scroeder for the original code. Borrowed from
# aaron-schroeder/spatialfriend
# https://github.com/aaron-schroeder/spatialfriend/blob/master/spatialfriend/spatialfriend.py
import numpy as np
import pandas
import warnings
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import math

def elevation_gain(elevations):
  """Naive elevation gain calculation.

  TODO: Make this algorithm smarter so noise doesn't affect it as much.
  """
  return sum([max(elevations[i+1] - elevations[i], 0.0)
              for i in range(len(elevations) - 1)])


def elevation_smooth_time(elevations, sample_len=1,
                          window_len=21, polyorder=2):
  """Smooths noisy elevation time series.

  Because of GPS and DEM inaccuracy, elevation data is not smooth.
  Calculations involving terrain slope (the derivative of elevation
  with respect to distance, d_elevation/d_x) will not yield reasonable
  values unless the data is smoothed. 

  This method's approach follows the overview outlined in the 
  NREL paper found in the Resources section and cited in README.
  However, unlike the algorithm in the paper, which samples regularly
  over distance, this algorithm samples regularly over time (well, it 
  presumes the elevation values are sampled at even 1-second intervals.
  The body only cares about energy use over time, not over distance.
  The noisy elevation data is downsampled and passed through a 
  Savitzky-Golay (SG) filter. Parameters for the filters were not 
  described in the paper, so they must be tuned to yield intended
  results when applied to a particular type of data. Because the
  assumptions about user behavior depend on the activiy being performed,
  the parameters will likely differ for a road run, a trail run, or a
  trail hike.

  Args:
    elevations: Array-like object of elevations above sea level
                corresponding to each time.
    sample_len: A float describing the time (in seconds) between between
                desired resampled data. Default is 1.
    window_len: An integer describing the length of the window used
                in the SG filter. Must be positive odd integer.
    polyorder: An integer describing the order of the polynomial used
               in the SG filter, must be less than window_len.

  TODO(aschroeder) ? Combine a binomial filter with existing SG filter
                     and test effects on algorithm performance.
  """
  #times = np.arange(0, len(elevations))
  #
  #if isinstance(times[0], datetime.timedelta):
  #  times = [time.total_seconds() for time in times]
  #else:
  #  times = list(time)

  # Pass downsampled data through a Savitzky-Golay filter (attenuating
  # high-frequency noise).
  # TODO (aschroeder): Add a second, binomial filter?
  # TODO (aschroeder): Fix the scipy/signal/arraytools warning!
  with warnings.catch_warnings():
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=RuntimeWarning)
    elevs_smooth = savgol_filter(list(elevations), window_len, polyorder)

  return elevs_smooth


def elevation_smooth(distances, elevations, sample_len=5.0,
                     window_len=21, polyorder=2):
  """Smooths noisy elevation data for use in grade calculations.

  Because of GPS and DEM inaccuracy, elevation data is not smooth.
  Calculations involving terrain slope (the derivative of elevation
  with respect to distance, d_elevation/d_x) will not yield reasonable
  values unless the data is smoothed. 

  This method's approach follows the overview outlined in the 
  NREL paper found in the Resources section and cited in README.
  The noisy elevation data is downsampled and passed through a 
  Savitzy-Golay (SG) filter. Parameters for the filters were not 
  described in the paper, so they must be tuned to yield intended
  results when applied to the data.

  Args:
    distances: Array-like object of cumulative distances along a path. 
    elevations: Array-like object of elevations above sea level
                corresponding to the same path.
    sample_len: A float describing the distance (in meters) between
                data samples. Data will be resampled at this interval.
    window_len: An integer describing the length of the window used
                in the SG filter. Must be positive odd integer.
    polyorder: An integer describing the order of the polynomial used
               in the SG filter, must be less than window_len.

  TODO(aschroeder) ? Combine a binomial filter with existing SG filter
                   and test effects on algorithm performance.
  """
  distances = pandas.Series(distances, name='distance')
  elevations = pandas.Series(elevations, name='elevation')

  # Subsample elevation data in evenly-spaced intervals, with each
  # point representing elevation value at the interval midpoint. 
  n_sample = math.ceil((distances.iloc[-1] - distances.iloc[0]) / sample_len)
  xvals = np.linspace(distances.iloc[0], distances.iloc[-1], n_sample + 1)
  interp_fn = interp1d(distances, elevations, kind='linear')
  elevations_ds = interp_fn(xvals)

  # Create a DataFrame to handle calculations.
  data_ds = pandas.DataFrame(data=elevations_ds, columns=['elevation'])
  data_ds['distance'] = xvals

  #idx = pandas.cut(distances, n_sample)

  #with warnings.catch_warnings():
  #  warnings.simplefilter('ignore', category=RuntimeWarning)
  #  data_ds = elevations.groupby(idx).apply(np.median).interpolate(
  #      limit_direction='both').to_frame()
  #data_ds['distance'] = pandas.IntervalIndex(
  #    data_ds.index.get_level_values('distance')).mid

  # Pass downsampled data through a Savitzky-Golay filter (attenuating
  # high-frequency noise). Calculate elevations at the original distance
  # values via interpolation.
  # TODO (aschroeder): Add a second, binomial filter?
  # TODO (aschroeder): Fix the scipy/signal/arraytools warning!
  with warnings.catch_warnings():
    warnings.simplefilter(action='ignore', category=FutureWarning)
    warnings.simplefilter(action='ignore', category=RuntimeWarning)
    data_ds['sg'] = savgol_filter(data_ds['elevation'], window_len, polyorder)

  # Backfill the elevation values at the original distances by
  # interpolation between the downsampled, smoothed points.
  interp_function = interp1d(
      data_ds['distance'], data_ds['sg'], 
      #fill_value='extrapolate', kind='linear')
      fill_value='extrapolate', kind='quadratic')
  smooth = interp_function(distances)

  # TODO (aschroeder): Switch this back when done.
  #return data_ds
  return smooth


def grade_smooth_time(distances, elevations):
  """Calculates smoothed point-to-point grades based on time.

  This method assumes elevation values are evenly sampled with respect
  to time.

  Args:
    distances: Array-like object of cumulative distances sampled at each
               second along a path. 
    elevations: Array-like object of elevations above sea level
                corresponding to the same path.
  """
  distances = pandas.Series(distances).reset_index(drop=True)
  elevations = pandas.Series(elevations).reset_index(drop=True)
  elevations_smooth = pandas.Series(elevation_smooth_time(elevations))
 
  grade = elevations_smooth.diff() / distances.diff()

  # Clean up spots with NaNs from dividing by zero distance.
  # This assumes the distances and elevations arrays have no NaNs.
  grade.fillna(0, inplace=True) 

  return np.array(grade)


def grade_smooth(distances, elevations):
  """Calculates smoothed point-to-point grades based on distance.

  TODO(aschroeder): Check if distances and elevations are same length.
  Args:
    distances: Array-like object of cumulative distances along a path. 
    elevations: Array-like object of elevations above sea level
                corresponding to the same path.
  """
  distances = pandas.Series(distances).reset_index(drop=True)
  elevations = pandas.Series(elevations).reset_index(drop=True)
  elevations_smooth = pandas.Series(elevation_smooth(distances, elevations))
 
  grade = elevations_smooth.diff() / distances.diff()

  # Clean up spots with NaNs from dividing by zero distance.
  # This assumes the distances and elevations arrays have no NaNs.
  grade.fillna(0, inplace=True) 

  return np.array(grade)


def grade_raw(distances, elevations):
  """Calculates unsmoothed point-to-point grades.

  TODO(aschroeder): check if distances and elevations are same length.
  Args:
    distances: Array-like object of cumulative distances along a path. 
    elevations: Array-like object of elevations above sea level
                corresponding to the same path.
  """
  distances = pandas.Series(distances).reset_index(drop=True)
  elevations = pandas.Series(elevations).reset_index(drop=True)

  grade = elevations.diff() / distances.diff()

  # Clean up spots with NaNs from dividing by zero distance.
  # This assumes the distances and elevations arrays have no NaNs.
  grade.fillna(0, inplace=True) 

  return np.array(grade)