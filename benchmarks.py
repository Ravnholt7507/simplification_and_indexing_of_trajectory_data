from queries import within
from queries import range_query, grid_index_range_query
import time


def test_query(coordinates, rtree):
    start = time.time()
    results = range_query(coordinates, rtree)
    end = time.time()
    print("Query took ", end - start, " seconds to execute.\n")

def test_query_grid_index(coordinates, grid_index):
    start = time.perf_counter()
    results = grid_index_range_query(coordinates, grid_index)
    end = time.perf_counter()
    print("Query took ", end - start, " seconds to execute.\n")


def range_query_no_compression_no_indexing(coordinates, points):
    start = time.time()
    results = []
    for index, row in points.iterrows():
        point = (row["latitude"], row["longitude"])
        if within(coordinates, point):
            results.append(row)
    end = time.time()
    print("Query took ", end - start, " seconds to execute.\n")
    return results


def compression_ratio(df, simplified_df):
    return len(df) / len(simplified_df)
