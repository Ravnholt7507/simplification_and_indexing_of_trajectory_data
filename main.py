import pandas as pd
import math
from compression_models import pmc_midrange
from r_tree import Rtree, create_mbr
from queries import time_query, count_elements, range_query
import time


def main():
    mbr_points = 10
    df = pd.read_csv("release/taxi_log_2008_by_id/1.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])

    final_df = pmc_midrange(df, 0.02)
    rest: int = len(final_df) % mbr_points
    loops: int = math.floor(len(final_df)/mbr_points)
    i: int = 0
    rectangles = []

    while i < loops:
        rectangles.append(create_mbr(final_df.head(mbr_points)))
        final_df = final_df.iloc[mbr_points:]
        i += 1
    if rest != 0:
        rectangles.append(create_mbr(final_df))

    rtree = Rtree()
    for element in rectangles:
        rtree.insert(element)

    for child in rtree.root.children:
        rtree.root.find_leafs(child)

    # examples of time queries
    # start_time = "2008-02-02 15:00:00"
    # end_time = "2008-02-03 15:36:10"

    # example of query for range search
    coordinates = [39.92123, 116.51172, 39.9213, 116.52]
    
    start = time.time()
    results = range_query(coordinates, rtree)
    # results = time_query(start_time, end_time, rtree)
    end = time.time()
    
    print("Query took ", end - start, " seconds to execute.")

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
