import pandas as pd
import numpy as np

class BatchMode_TrajectoryEnv:
    def __init__(self, df):
        self.buffer_size = len(df)
        self.k = 3
        self.w = 50
        self.current_index = 0
        self.acc_reward = 0
        self.trajectory_error = 0
        self.max_errors = np.zeros(len(df))
        self.ids = df[['taxi_id', 'datetime']].copy()
        df = df.assign(value=0.0)
        df['index'] = df.index
        self.trajectory = df.drop(columns=['taxi_id', 'datetime']).to_numpy()
        self.buffer = self.trajectory.copy()

    def reattach_identifiers(self, numeric_data):
        numeric_df = pd.DataFrame(numeric_data, columns=['longitude', 'latitude', 'value', 'index'])
        full_df = pd.merge(self.ids, numeric_df, left_index=True, right_on='index', how='right')
        full_df.drop(columns=['index', 'value'], inplace=True)
        return full_df

    def calculate_simplification_error(self):
        return self.trajectory_error

    def calculate_compression_ratio(self):
        original_points = len(self.trajectory)
        simplified_points = len(self.buffer)
        return original_points / simplified_points

    def calculate_overall_error(self):
        max_overall_error = 0
        for i in range(len(self.buffer) - 1):
            segment_start = self.buffer[i]
            segment_end = self.buffer[i + 1]
            segment_errors = []
            max_segment_error = 0
            for j in range(segment_start[3].astype(int), segment_end[3].astype(int)):
                point = self.trajectory[j]
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
        end_index = int(segment_end[3])
        segment_errors = []
        max_segment_error = 0
        for i in range(start_index, end_index):
            point = self.trajectory[i]
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

    def step(self, action):
     #   start = time.time()
        done = False
        state, indices = self.get_state()

        if len(self.buffer) > self.w:
            index_to_drop = indices[action]
            self.update_values(index_to_drop)
            self.buffer = np.delete(self.buffer, index_to_drop, axis=0)
            self.max_errors = np.delete(self.max_errors, index_to_drop, axis=0)

            self.update_max_errors(index_to_drop)
            self.trajectory_error = self.get_maximum_error()
            reward = -self.trajectory_error
            self.current_index += 1
        else:
            reward = 0
            done = True

        next_state, _ = self.get_state()
        return next_state, reward, done

    def reset(self):
        self.trajectory_error = 0
        self.buffer = self.trajectory.copy()
        self.max_errors = np.zeros(self.buffer_size)
        self.current_index = self.buffer_size+1
        for i in range(1, self.buffer_size-1): #opdater værdier for p1, p2, p3
            self.buffer[i][2] = self.ped(self.buffer[i], self.buffer[i+1], self.buffer[i-1])
        initial_state, _ = self.get_state()
        return initial_state