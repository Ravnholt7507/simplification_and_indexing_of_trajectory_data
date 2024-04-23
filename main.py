import pandas as pd
from DOTS.run_dots import dots
from compression_models import pmc_midrange
from r_tree import init_rtree
from benchmarks import range_query_no_compression_no_indexing, test_query
from ui import plot_mbrs
from RLTS.simplify import rlts, plot_side_by_side


def main():
    mbr_points = 5 

    df = pd.read_csv("release/taxi_log_2008_by_id/1.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])


    dag_df = dots(df, 0.05, 1.5)
    dag_rtree = init_rtree(dag_df, mbr_points)

    rlts_df = rlts(df)
    rlts_rtree = init_rtree(rlts_df, mbr_points)

    final_df = pmc_midrange(df, 0.02)

    # r_tree with compression
    rtree = init_rtree(final_df, mbr_points)

    # r_tree without compression
    no_comp_rtree = init_rtree(df, mbr_points)
     
    # example of query for range search
    coordinates = [39.9, 116.4, 39.95, 116.6]
    # coordinates = [39.5, 116, 40, 117]
    print("WITH PMC-COMPRESSION AND WITH R-TREE INDEXING:")
    test_query(coordinates, rtree)
    
    print("WITHOUT PMC-COMPRESSION AND WITH R-TREE INDEXING")
    test_query(coordinates, no_comp_rtree)

    print("\nWITHOUT PMC-COMPRESSION AND WITHOUT R-TREE INDEXING:")
    range_query_no_compression_no_indexing(coordinates, df)

    print("WITH DOTS AND WITH R-TREE INDEXING:")
    test_query(coordinates, dag_rtree)

    print("\nWITH RLTS AND WITH R-TREE INDEXING:")
    test_query(coordinates, rlts_rtree)
main()
