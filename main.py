import pandas as pd
from compression_models import pmc_midrange
from r_tree import init_rtree, make_all_mbrs
from queries import time_query, count_elements, range_query
import time
from benchmarks import range_query_no_compression_no_indexing
from ui import plot_query


def main():
    mbr_points = 10
    df = pd.read_csv("release/taxi_log_2008_by_id/1.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])


    final_df = pmc_midrange(df, 0.02)

    # r_tree with compression
    rectangles = make_all_mbrs(final_df, mbr_points)

    rtree = init_rtree(rectangles)

    # r_tree without compression
    rectangles = make_all_mbrs(df, mbr_points)

    no_comp_rtree = init_rtree(rectangles)
    # examples of time queries
    # start_time = "2008-02-02 15:00:00"
    # end_time = "2008-02-03 15:36:10"

    # example of query for range search

    coordinates = [39.9, 116.4, 39.95, 116.6]
    print("WITH PMC-COMPRESSION AND WITH R-TREE INDEXING:")

    start = time.time()
    results = range_query(coordinates, rtree)
    # results = time_query(start_time, end_time, rtree)
    end = time.time()

    print("Query with PMC-midrange compression and r-tree indexing took ", end - start, " seconds to execute.")
    print("\nWITHOUT PMC-COMPRESSION AND WITH R-TREE INDEXING")
    start = time.time()
    results = range_query(coordinates, no_comp_rtree)
    end = time.time()
    print("Query without PMC-midrange compression and with r-tree indexing took ", end - start, " seconds to execute.")

    print("\nWITHOUT PMC-COMPRESSION AND WITHOUT R-TREE INDEXING:")

    start = time.time()
    bench_results = range_query_no_compression_no_indexing(coordinates, df)
    end = time.time()
    print("Query without compression and r-tree indexing took ", end - start, "seconds to execute.")

    plot_query(df["longitude"], df["latitude"], coordinates)
    return results

# call to check integrity of leafs
def pretty_print(rtree):
    print("R-tree:")
    _pretty_print_rec(rtree.root)


def _pretty_print_rec(node):
    if node.is_leaf:
        for child in node.children:
            print('Leaf:', child.mbr)
    else:
        print('Internal Node:', len(node.children))
        for child in node.children:
            _pretty_print_rec(child)


main()
