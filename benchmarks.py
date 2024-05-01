from queries import range_query, grid_index_range_query, within
from haversine import haversine
import time


def test_query(coordinates, rtree):
    start = time.perf_counter()
    results = range_query(coordinates, rtree)
    end = time.perf_counter()
    print("Query took ", end - start, " seconds to execute.\n")

def test_query_grid_index(coordinates, grid_index):
    start = time.perf_counter()
    results = grid_index_range_query(coordinates, grid_index)
    end = time.perf_counter()
    print("Query took ", end - start, " seconds to execute.\n")


def range_query_no_compression_no_indexing(coordinates, points):
    start = time.perf_counter()
    results = []
    for index, row in points.iterrows():
        point = (row["latitude"], row["longitude"])
        if within(coordinates, point):
            results.append(row)
    end = time.perf_counter()
    print("Query took ", end - start, " seconds to execute.\n")
    return results


def knn_no_indexing(poi, df):
    closest_point = df.iloc[0]
    for index, row in df.iterrows():
        if haversine((row["latitude"], row["longitude"]), poi) < haversine((closest_point["latitude"], closest_point["longitude"]), poi):
            closest_point = row
    return closest_point

def compression_ratio(df, simplified_df):
    return len(df) / len(simplified_df)
