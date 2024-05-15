import pandas as pd
import time
from DOTS.run_dots import dots
from compression_models import pmc_midrange
from pympler import asizeof
from squish import SquishE, squish
from r_tree import init_rtree
from grid_index import init_grid_index
from benchmarks import range_query_no_compression_no_indexing, test_query, compression_ratio, test_query_grid_index, calculate_range_query_accuracy, knn_no_indexing, print_full_size,knn_grid_index
from ui import plot_mbrs, plot_query
from RLTS.run_rlts import rlts
from queries import optimal_knn


def main():
    mbr_points = 5

    df = pd.read_csv("release/taxi_log_2008_by_id/10076.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])
    
    print(len(df))

    rlts_df = rlts(df, 50)
    rlts_rtree = init_rtree(rlts_df, mbr_points)

    squish_df = rlts(df, 50)
    squish_rtree = init_rtree(rlts_df, mbr_points)

    dag_df = dots(df, 0.05, 1.5)
    dag_rtree = init_rtree(dag_df, mbr_points)

    final_df = pmc_midrange(df, 0.02)

    # r_tree with compression
    rtree = init_rtree(final_df, mbr_points)

    # r_tree without compression
    no_comp_rtree = init_rtree(df, mbr_points)

    # grid index with no compression
    grid_index = init_grid_index(df)

    # example of query for range search
    coordinates = [39.9, 116.4, 39.92, 116.5]
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

    print("\nWITH SQUISH AND WITH R-TREE INDEXING:")
    test_query(coordinates, squish_rtree)

    print("\nWITH RLTS AND WITHOUT R-TREE INDEXING:")
    range_query_no_compression_no_indexing(coordinates, rlts_df)

    print(("\nWITH NO COMPRESSION AND WITH GRID INDEXING:"))
    test_query_grid_index(coordinates, grid_index)

    print("compression ratio for RLTS is: ", compression_ratio(df, rlts_df))
    print("compression ratio for DOTS is: ", compression_ratio(df, dag_df))
    print("compression ratio for PMC is: ", compression_ratio(df, final_df))

    print("---------- knn test ----------------:")
    print("----With r-tree:")
    start = time.perf_counter()
    print(optimal_knn((39.96769, 116.40239), no_comp_rtree))
    end = time.perf_counter()
    print("KNN with r-tree took ", end - start, "seconds to execute.")

    print("--Without r-tree:")
    start = time.perf_counter()
    print(knn_no_indexing((39.96769, 116.40239), df))
    end = time.perf_counter()
    print("KNN without r-tree took ", end - start, "seconds to execute.")

    print("--With Grid Index:")
    print(knn_grid_index((39.96769, 116.40239), grid_index))

    # Query accuracy tests
    print("range query accuracy with RLTS is: ", calculate_range_query_accuracy(coordinates, df, rlts_df))
    print("range query accuracy with DOTS is: ", calculate_range_query_accuracy(coordinates, df, dag_df))
    print("range query accuracy with PMC is: ", calculate_range_query_accuracy(coordinates, df, final_df))

    #Index memory usage
    #print_full_size(grid_index, 'grid_index')
    #print_full_size(rtree, 'r-tree')

main()
