from datetime import datetime
import math

def interpolate_point(p1, p2, p3):
    """
    Interpolates a point on the line segment between p1 and p2 that is temporally aligned with p3.

    Each point is a tuple (x, y, time), where time is a datetime object.

    Returns a tuple (x, y) representing the interpolated point.
    """
    # Calculate total time difference and the proportion for p3
    total_time = (p2[2] - p1[2]).total_seconds()
    time_proportion = (p3[2] - p1[2]).total_seconds() / total_time if total_time != 0 else 0

    # Linear interpolation for x and y coordinates
    x = p1[0] + (p2[0] - p1[0]) * time_proportion
    y = p1[1] + (p2[1] - p1[1]) * time_proportion

    return (x, y)

def euclidean_distance(p1, p2):
    """
    Calculate the Euclidean distance between two points (x1, y1) and (x2, y2).
    """
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def sed(p1, p2, p3):
    """
    Calculate the Synchronized Euclidean Distance (SED) from p3 to the line segment [p1, p2].

    Each point is a tuple (x, y, time), where time is a datetime object.
    """
    interpolated_point = interpolate_point(p1, p2, p3)
    return euclidean_distance(interpolated_point, (p3[0], p3[1]))