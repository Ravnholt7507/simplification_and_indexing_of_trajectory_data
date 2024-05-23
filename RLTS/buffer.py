import pandas as pd
import numpy as np
import datetime
import math
from queries import count_elements
from memory_track import MemoryTracker
from r_tree import init_rtree, create_mbr
from grid_index import init_grid_index

class TrajectoryEnv:
    def __init__(self, df, buffer_size, spatial_index = None):
        self.buffer_size = buffer_size
        self.k = 3
        self.buffer = pd.DataFrame(columns=['longitude', 'latitude', 'value', 'index']).to_numpy()
        self.current_index = 0
        self.acc_reward = 0
        self.trajectory_error = 0
        self.max_errors = np.zeros(buffer_size)
        self.ids = df[['taxi_id', 'datetime']].copy()
        df = df.assign(value=0.0)
        df['index'] = df.index
        self.original_trajectory = df.drop(columns=['taxi_id', 'datetime']).to_numpy()
        self.spatial_index_str = spatial_index
        self.spatial_index = None
        self.memory_tracker = MemoryTracker()
        self.raw_data_size = self.memory_tracker.track_memory_usage(self.original_trajectory)

 
    def reattach_identifiers(self, data):
        if isinstance(data, np.ndarray):
            numeric_df = pd.DataFrame(data, columns=['longitude', 'latitude', 'value', 'index'])
        elif isinstance(data, pd.DataFrame):
            numeric_df = data
        full_df = pd.merge(self.ids, numeric_df, left_index=True, right_on='index', how='right')
        full_df.drop(columns=['index', 'value'], inplace=True)
        return full_df
  
    def calculate_simplification_error(self):
        return self.trajectory_error

    def calculate_compression_ratio(self):
        original_points = len(self.original_trajectory)
        simplified_points = len(self.buffer)
        return original_points / simplified_points

    def calculate_overall_error(self):
        max_overall_error = 0
        for i in range(len(self.buffer) - 1):
            segment_start = self.buffer[i]
            segment_end = self.buffer[i + 1]
            segment_errors = []
            start_index = int(segment_start[3])
            end_index = int(segment_end[3]) if (int(segment_end[3]) < len(self.original_trajectory)) else len(self.original_trajectory)
            max_segment_error = 0
            for j in range(start_index, end_index):
                point = self.original_trajectory[j]
                distance = self.ped(point, segment_start, segment_end)
                segment_errors.append(distance)
                max_segment_error = max(distance, max_segment_error)
            max_overall_error += max_segment_error
        return max_overall_error

    def update_max_errors(self, dropped_index):
            self.max_errors[dropped_index-1] = self.calculate_segment_max_error(dropped_index-1)

    def calculate_segment_max_error(self, segment_index):
        segment_start = self.buffer[segment_index]
        segment_end = self.buffer[segment_index + 1]
        start_index = int(segment_start[3])
        end_index = int(segment_end[3]) if (int(segment_end[3]) < len(self.original_trajectory)) else len(self.original_trajectory)
        segment_errors = []
        max_segment_error = 0
        for i in range(start_index, end_index):
            point = self.original_trajectory[i]
            distance = self.ped(point, segment_start, segment_end)
            segment_errors.append(distance)
            max_segment_error = max(distance, max_segment_error)
        return max_segment_error

    def ped(self, current, next_point, prev_point):
        if np.array_equal(next_point[:2], prev_point[:2]):
            return 0
        line_vec = next_point[:2] - prev_point[:2]
        point_vec = prev_point[:2] - current[:2]
        cross_product = np.cross(line_vec, point_vec)
        distance = np.abs(cross_product) / np.linalg.norm(line_vec)
        return distance

    def get_maximum_error(self):
        return np.max(self.max_errors)

    def update_values(self, idx):
        if idx < 1 or idx > self.buffer_size-1:
            print("Warning: wrong index given")

        point = self.buffer[idx]
        prev_point = self.buffer[max(idx - 1, 0)]
        prev_prev_point = self.buffer[max(idx - 2, 0)]
        next_point = self.buffer[min(idx + 1, len(self.buffer) - 1)]
        next_next_point = self.buffer[min(idx + 2, len(self.buffer)-1)]

        if (idx-1) != 0:
            self.buffer[idx-1, 2] = max(self.ped(prev_point, next_point, prev_prev_point), self.ped(point, next_point, prev_prev_point))
        else:
            self.buffer[idx-1, 2] = 0

        if (idx+1) != self.buffer_size + 1 and (min(idx + 2, len(self.buffer)-1) != min(idx + 1, len(self.buffer) - 1)):
            self.buffer[idx+1, 2] = max(self.ped(next_point, next_next_point, prev_point), self.ped(point, next_next_point, prev_point))
        else:
            self.buffer[idx+1, 2] = 0

    def get_state(self):
        error_values = self.buffer[1:-1, 2]
        sorted_indices = np.argsort(error_values)[:self.k]
        sorted_errors = error_values[sorted_indices]
        original_indices = sorted_indices + 1
        return sorted_errors, original_indices.tolist()


    def interpolate_point(self, p1, p2, p3):
        total_time = (datetime.strptime(p2[2], '%Y-%m-%d %H:%M:%S') - datetime.strptime(p1[2], '%Y-%m-%d %H:%M:%S')).total_seconds()
        time_proportion = (datetime.strptime(p3[2], '%Y-%m-%d %H:%M:%S') - datetime.strptime(p1[2], '%Y-%m-%d %H:%M:%S')).total_seconds() / total_time if total_time != 0 else 0

        x = p1[0] + (p2[0] - p1[0]) * time_proportion
        y = p1[1] + (p2[1] - p1[1]) * time_proportion

        return (x, y)

    def euclidean_distance(self, p1, p2):
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


    def sed(self, p1, p2, p3):
        interpolated_point = self.interpolate_point(p1, p2, p3)
        return self.euclidean_distance(interpolated_point, (p3[0], p3[1]))

    def step(self, action):
        done = False
        state, indices = self.get_state()

        if self.current_index < len(self.original_trajectory):
            next_point = self.original_trajectory[self.current_index] # skal scannes som 0,0
            current_point = self.original_trajectory[self.current_index-1] #skal have ny værdi
            prev_point = self.original_trajectory[self.current_index-2]  #tidligere sidste værdi

            self.buffer[self.buffer_size][2] = self.ped(current_point, next_point, prev_point)
            self.buffer = np.concatenate((self.buffer, next_point.reshape(1, -1)))
            if self.spatial_index_str == 'rtree':
                next_point_mbr = create_mbr(self.reattach_identifiers(next_point.reshape(1, 4)))
                self.spatial_index.insert(next_point_mbr)
            if self.spatial_index_str == 'grid':
                self.spatial_index.insert_point(tuple(next_point[:2]))
        else:
            done = True

        index_to_drop = indices[action]
        self.update_values(index_to_drop)
        if self.spatial_index_str == 'rtree':
            point_to_remove = self.reattach_identifiers(self.buffer[index_to_drop].reshape(1,4))
            self.spatial_index.remove(point_to_remove)
        if self.spatial_index_str == 'grid':
            self.spatial_index.remove_point(tuple(self.buffer[index_to_drop, 0:2]))
        self.buffer = np.delete(self.buffer, index_to_drop, axis=0)
        self.update_max_errors(index_to_drop) #if self.current_index < len(self.original_trajectory) -1 else None
        self.trajectory_error = self.get_maximum_error()
        reward = -self.trajectory_error

        self.current_index += 1
        next_state, indices = self.get_state()

        # Track memory usage after each step
        self.memory_tracker.track_memory_usage(self.buffer)
        if self.spatial_index is not None:
            self.memory_tracker.track_memory_usage(self.spatial_index)

        return next_state, indices, reward, done

    def reset(self):
        self.trajectory_error = 0
        self.max_errors = np.zeros(self.buffer_size)
        self.buffer = self.original_trajectory[:self.buffer_size+1].copy() # Include one extra for initial state

        if self.spatial_index_str == 'rtree':
            self.spatial_index = init_rtree(self.reattach_identifiers(self.buffer), mbr_points=10)
        elif self.spatial_index_str == 'grid':
            self.spatial_index = init_grid_index(self.buffer[:, :2])


        self.current_index = self.buffer_size+1
        for i in range(1, self.buffer_size): #opdater værdier for p1, p2, p3
            self.buffer[i][2] = self.ped(self.buffer[i], self.buffer[i+1], self.buffer[i-1])
        initial_state, indices = self.get_state()

        self.memory_tracker.track_memory_usage(self.buffer)
        if self.spatial_index is not None:
            self.memory_tracker.track_memory_usage(self.spatial_index)
        return initial_state, indices
    
    def get_memory_statistics(self):
        stats = {
            "peak_memory_usage": self.memory_tracker.get_peak_memory_usage(),
            "average_memory_usage": self.memory_tracker.get_average_memory_usage(),
            "memory_overhead": self.memory_tracker.get_memory_overhead(self.raw_data_size)
        }

        if self.spatial_index is not None:
            spatial_index_size = self.memory_tracker.track_memory_usage(self.spatial_index)
            stats["spatial_index_size"] = spatial_index_size
            stats["memory_with_spatial_index"] = stats["peak_memory_usage"] + spatial_index_size
        else:
            stats["spatial_index_size"] = 0
            stats["memory_with_spatial_index"] = stats["peak_memory_usage"]

        return stats