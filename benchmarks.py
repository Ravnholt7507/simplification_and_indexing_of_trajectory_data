from queries import within
from queries import range_query
import time


def test_query(coordinates, rtree):
    start = time.time()
    results = range_query(coordinates, rtree)
    end = time.time()
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
