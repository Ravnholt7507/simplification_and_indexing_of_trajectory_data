from queries import range_query, grid_index_range_query, within, knn_query_grid_index, optimal_knn
from DOTS.run_dots import dots
from RLTS.run_rlts import rlts
from compression_models import pmc_midrange
import numpy as np
import pandas as pd
from r_tree import init_rtree
from squish import squish, SquishE
from grid_index import init_grid_index
import os
import csv
from pympler import asizeof
import random
import heapq
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

def knn_no_indexing(point, df):
    closest_point = df.iloc[0]
    for index, row in df.iterrows():
        if haversine((row["latitude"], row["longitude"]), point) < haversine((closest_point["latitude"], closest_point["longitude"]), point):
            closest_point = row
    return closest_point

def knn_grid_index(point, grid_index):
    start = time.perf_counter()
    results = knn_query_grid_index(grid_index, point, 2)
    end = time.perf_counter()
    print("Query took ", end - start, " seconds to execute.\n")


def compression_ratio(df, simplified_df):
    return len(df) / len(simplified_df)


def calculate_range_query_accuracy(bbox, original_df, simplified_df):
    min_y, min_x, max_y, max_x = bbox

    def points_in_bbox(df):
        return df[(df['longitude'] >= min_x) & (df['longitude'] <= max_x) & (df['latitude'] >= min_y) & (df['latitude'] <= max_y)]

    original_in_bbox = points_in_bbox(original_df)
    simplified_in_bbox = points_in_bbox(simplified_df)
    count_original_in_bbox = len(original_in_bbox)
    count_simplified_in_bbox = len(simplified_in_bbox)

    if count_original_in_bbox != 0:
        accuracy = (count_simplified_in_bbox / count_original_in_bbox)
    else:
        accuracy = 1

    return accuracy

def print_full_size(grid_index, label):
    print(f"Full memory size of {label}: {asizeof.asizeof(grid_index)} bytes")

# Function to print full memory usage of an object
def print_full_size(obj, label):
    print(f"Full memory size of {label}: {asizeof.asizeof(obj)} bytes")

def get_random_bbox(min_lat, min_lon, max_lat, max_lon):
    lat1 = random.uniform(min_lat, max_lat)
    lat2 = random.uniform(min_lat, max_lat)
    lon1 = random.uniform(min_lon, max_lon)
    lon2 = random.uniform(min_lon, max_lon)
    min_lat = min(lat1, lat2)
    max_lat = max(lat1, lat2)
    min_lon = min(lon1, lon2)
    max_lon = max(lon1, lon2)
    return [min_lat, min_lon, max_lat, max_lon]

def get_random_trajectory(min_rows=1000, max_rows=10000):
    folder_path = "release/taxi_log_2008_by_id"
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
    random.shuffle(files)

    for file_path in files:
        df = pd.read_csv(file_path, names=["taxi_id", "datetime", "longitude", "latitude"])
        if len(df) > min_rows and len(df) < max_rows:
            return df

    return None

def get_trajectories(min_rows=0, max_rows=20000):
    folder_path = "release/taxi_log_2008_by_id"
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
    random.shuffle(files)
    dfs = []

    for file_path in files:
        df = pd.read_csv(file_path, names=["taxi_id", "datetime", "longitude", "latitude"])
        if len(df) > min_rows and len(df) < max_rows:
            dfs.append(df)
        if len(dfs) > 41:
            break

    return dfs

def eval_accuracy(test_count):
    i = 0
    rlts_values = []
    pmc = []
    dag = []

    while i < test_count:
        print("round: ", i)
        df = get_random_trajectory()
        bbox = get_random_bbox(df["latitude"].min(), df["longitude"].min(), df["latitude"].max(), df["longitude"].max())

        dag_df, _ = dots(df, 0.05, 1.5)
        dag.append(calculate_range_query_accuracy(bbox, df, dag_df))

        rlts_df, _ = rlts(df, len(dag_df))
        rlts_values.append(calculate_range_query_accuracy(bbox, df, rlts_df))

        pmc_df = pmc_midrange(df, 0.02)
        pmc.append(calculate_range_query_accuracy(bbox, df, pmc_df))
        i += 1
    dict = {"rlts": rlts_values, "pmc": pmc, "dag": dag}
    df = pd.DataFrame(dict)
    df.to_csv("eval_accuracy.csv")




def eval_time(min_points, max_points, output_file='timing_results.csv'):
    time_DOTS = 0
    time_RLTS = 0
    trajectories = get_trajectories(min_points, max_points)
    if len(trajectories) > 100: #we want max hundred trajectories
        trajectories = trajectories[:100]
    n_of_trajectories = len(trajectories)
    print(n_of_trajectories)

    with open(output_file, 'a', newline='') as f:
        writer = csv.writer(f)
        # Write the header row

        for df in trajectories:
            start = time.perf_counter()
            result, _ = dots(df, 0.1, 1)
            end = time.perf_counter()
            dots_time = end - start
            time_DOTS += dots_time

            compression = len(result)
            print(len(df))
            print(compression)
            if compression < 10:
                compression = 10

            start = time.perf_counter()
            rlts(df, compression)
            end = time.perf_counter()
            rlts_time = end - start
            time_RLTS += rlts_time

            # start = time.perf_counter()
            # squish(df, (len(df)/compression))
            # end = time.perf_counter()
            # squish_time = end - start

            # Write the times for each run to the CSV file
            writer.writerow([dots_time, rlts_time, max_points])

    avg_DOTS_time = (time_DOTS / n_of_trajectories)
    avg_RLTS_time = (time_RLTS / n_of_trajectories)
    return avg_DOTS_time, avg_RLTS_time

def compression_time_test():
    print("Running compression time test")
    eval_time(100, 500) #min and max points in the trajectory
    eval_time(500, 1000)
    eval_time(1000, 1500)
    eval_time(1500, 2000)
    eval_time(2000, 3000)
    eval_time(3000, 4000)
    eval_time(4000, 5000)


def _error_vs_ratio_test(error_bound):
    total_error_dots = 0
    total_error_rlts = 0
    i= 0
    compression_rates = 0
    trajectories = get_trajectories(1800, 2000)
    trajectories = trajectories[:5]
    #sample the overall error for 20 trajectories
    for df in trajectories:
        print(i)
        dots_df, dots_error = dots(df, error_bound, 1.5)
        total_error_dots += dots_error
        rlts_df, rlts_error = rlts(df, len(dots_df))
        total_error_rlts += rlts_error
        compr_rate = len(df) / len(dots_df)
        compression_rates += compr_rate
        i += 1
    #We find the average error over all trajectories
    total_error_dots = (total_error_dots / len(trajectories))
    total_error_rlts = (total_error_rlts / len(trajectories))
    avg_compression_rate = compression_rates / len(trajectories)
    return total_error_rlts, total_error_dots, avg_compression_rate

def error_vs_ratio_test():
    print("Running Error vs ratio test for RLTS and DOTS")
    rlts_errors = []
    dots_errors = []
    compr_rates = []
    error_bounds = [0.1, 1, 2, 3, 4, 5]
    for x in error_bounds:
        total_error_rlts, total_error_dots, avg_comp_rate = _error_vs_ratio_test(x)
        rlts_errors.append(total_error_rlts)
        dots_errors.append(total_error_dots)
        compr_rates.append(avg_comp_rate)
    print(rlts_errors, dots_errors, compr_rates)


def knn_no_indexing_haversine(point, df, k):
    min_heap = []
    for index, row in df.iterrows():
        heapq.heappush(min_heap, haversine((row["latitude"], row["longitude"]), point))

    k_smallest_distances = heapq.nsmallest(k, min_heap)
    sum_k_smallest = sum(k_smallest_distances)
    return sum_k_smallest

def calculate_knn_query_accuracy(point, original_df, simplified_df, k=1):

    print(point)

    o_result = knn_no_indexing_haversine(point, original_df, k)
    s_result = knn_no_indexing_haversine(point, simplified_df, k)
    if s_result == 0 and o_result == 0:
        accuracy = 1 
    else: 
        if s_result != 0:
            accuracy = o_result / s_result
        else:
            accuracy = 0

    print(accuracy)
    return accuracy

def build_index_time(index_type):
    sizes = [100, 1000, 5000, 10000, 20000]
    build_times = []
    trajectories = get_trajectories(154600, 154700)
    trajectory = trajectories[0]
    for size in sizes:
        traj = trajectory[:size]
        start_time = time.perf_counter()
        if index_type == 'grid':
            index = init_grid_index(traj)
        elif index_type == 'rtree':
            index = init_rtree(traj, mbr_points=10)
        end_time = time.perf_counter()
        build_times.append((end_time-start_time))
    print(build_times)

#build_index_time('rtree')

def find_longest_dataframe():
    folder_path = "release/taxi_log_2008_by_id"
    files = [os.path.join(folder_path, file) for file in os.listdir(folder_path)]
    dfs = []
    for file_path in files:
        df = pd.read_csv(file_path, names=["taxi_id", "datetime", "longitude", "latitude"])
        dfs.append(df)
    # Find the longest dataframe
    longest_df = max(dfs, key=lambda df: len(df))

    print("The longest dataframe is:")
    print(len(longest_df))
    print(longest_df)
    longest_df = longest_df.drop_duplicates(subset=['latitude', 'longitude'], keep='first')
    print(len(longest_df))


#find_longest_dataframe()


def index_runtime_test(index_type, num_tests=100, random_seed=42):
    random.seed(random_seed)  # Set the random seed for reproducibility
    sizes = [10000, 50000, 100000, 150000]
    knn_times = []
    range_times = []
    trajectories = get_trajectories(154600, 154700)
    trajectory = trajectories[0]
    trajectory = trajectory.drop_duplicates(subset=['latitude', 'longitude'], keep='first')
    trajectory = trajectory[trajectory['latitude'].astype(str).str.startswith('39') & trajectory['longitude'].astype(str).str.startswith('116')]

    for size in sizes:
        traj = trajectory[:size]
        lat_min, lon_min, lat_max, lon_max = traj["latitude"].min(), traj["longitude"].min(), traj["latitude"].max(), traj["longitude"].max()

        range_test_times = []
        knn_test_times = []
        for _ in range(num_tests):  # Number of random tests
            range_query_bbox = get_random_bbox(lat_min, lon_min, lat_max, lon_max)
            knn_point = tuple(traj.sample(n=1)[['latitude', 'longitude']].iloc[0])

            if index_type == 'grid':
                grid_index = init_grid_index(traj)
                start_time = time.perf_counter()
                grid_index_range_query(range_query_bbox, grid_index)
                end_time = time.perf_counter()
                range_test_times.append((end_time - start_time))

                start_time = time.perf_counter()
                knn_query_grid_index(grid_index, knn_point, 1)
                end_time = time.perf_counter()
                knn_test_times.append((end_time - start_time))

            elif index_type == 'rtree':
                rtree_index = init_rtree(traj, mbr_points=10)
                start_time = time.perf_counter()
                range_query(range_query_bbox, rtree_index)
                end_time = time.perf_counter()
                range_test_times.append((end_time - start_time))

                start_time = time.perf_counter()
                optimal_knn(knn_point, rtree_index)
                end_time = time.perf_counter()
                knn_test_times.append((end_time - start_time))

        range_times.append(np.mean(range_test_times))
        knn_times.append(np.mean(knn_test_times))

    print("Range query times: ", range_times)
    print("kNN query times: ", knn_times)



index_runtime_test('rtree')
#error_vs_ratio_test()
#compression_time_test()
#eval_accuracy(10)

