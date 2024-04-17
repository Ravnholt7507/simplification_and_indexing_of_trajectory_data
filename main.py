import pandas as pd
import torch
from dataloader import load_single_file, load_bulk
from compression_models import pmc_midrange
from r_tree import init_rtree, make_all_mbrs
from queries import time_query, count_elements, range_query
from RLTS.simplify import simplify
from RLTS.train import train
from RLTS.policy import PolicyNetwork
from RLTS.buffer import TrajectoryEnv
from benchmarks import range_query_no_compression_no_indexing, test_query
from ui import plot_query, plot_mbrs


def main():
    mbr_points = 10

    df = pd.read_csv("release/taxi_log_2008_by_id/1.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])
    """    
    env = TrajectoryEnv(df)
    policy_network = PolicyNetwork(input_size=env.k, hidden_size=15, output_size=env.k)
    train(env, policy_network, 1) # resultate bliver lagt i RLTS/models/test_model som bliver hentet på næste linje
    policy_network.load_state_dict(torch.load("RLTS/models/test_model"))
    policy_network.eval()
    simplify(df, policy_network, env)
    
    """

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

    # print("\nWITH RLTS AND WITH R-TREE INDEXING:")
    # start = time.time()
    # bench_results = range_query()
    # end = time.time()
    # print("Query without compression and r-tree indexing took ", end - start, "seconds to execute.")

main()
