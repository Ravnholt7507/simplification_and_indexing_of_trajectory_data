import pandas as pd
import math
from compression_models import pmc_midrange
from r_tree import Rtree, create_mbr
from querys import time_query, count_elements


# final test commit
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

    start_time = "2008-02-02 15:00:00"
    end_time = "2008-02-03 15:36:10"

    # pretty_print(rtree)

    return time_query(start_time, end_time, rtree)


def pretty_print(rtree):
    print("R-tree:")
    _pretty_print_rec(rtree.root, 0)


def _pretty_print_rec(node, counter):
    if node.is_leaf:
        print('Leaf:', len(node.children))
    else:
        print('Internal Node:', len(node.children))
        for child in node.children:
            _pretty_print_rec(child, counter+1)


print(main())
