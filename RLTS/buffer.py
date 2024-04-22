import pandas as pd
import numpy as np

class TrajectoryEnv:
    def __init__(self, df, buffer_size=20):
        self.buffer_size = buffer_size
        self.k = 3
        self.buffer = pd.DataFrame(columns=['latitude', 'longitude', 'value', 'index'])
        self.current_index = 0
        self.acc_reward = 0
        self.trajectory_error = 0
        self.original_trajectory = df.assign(value=0.0, index=df.index)

    def calculate_simplification_error(self):
        return self.trajectory_error

    def calculate_compression_ratio(self):
        original_points = len(self.original_trajectory)
        simplified_points = len(self.buffer)
        return original_points / simplified_points

    def calculate_overall_error(self):
        max_overall_error = 0
        for i in range(len(self.buffer) - 1):
            segment_start = self.buffer.iloc[i]
            segment_end = self.buffer.iloc[i + 1]
            segment_errors = []
            max_segment_error = 0
            for j in range(segment_start['index'].astype(int), segment_end['index'].astype(int)):
                point = self.original_trajectory.iloc[j]
                distance = self.ped(point, segment_start, segment_end)
                segment_errors.append(distance)
                max_segment_error = max(distance, max_segment_error)
            max_overall_error += max_segment_error
        return max_overall_error

    def calculate_maximum_error(self):
        max_overall_error = 0
        for i in range(len(self.buffer) - 1):
            segment_start = self.buffer.iloc[i]
            segment_end = self.buffer.iloc[i + 1]
            segment_errors = []
            max_segment_error = 0
            for j in range(segment_start['index'].astype(int), segment_end['index'].astype(int)):
                point = self.original_trajectory.iloc[j]
                distance = self.ped(point, segment_start, segment_end)
                segment_errors.append(distance)
                max_segment_error = max(distance, max_segment_error)
            max_overall_error = max(max_overall_error, max_segment_error)
        return max_overall_error

    def ped(self, current, next_point, prev_point):
        point, next_point, prev_point = current[['latitude', 'longitude']], next_point[['latitude', 'longitude']], prev_point[['latitude', 'longitude']]
        if np.array_equal(next_point, prev_point):
            return 0
        return np.abs(np.cross(next_point-prev_point, prev_point-point)) / np.linalg.norm(next_point-prev_point)

    def update_values(self, idx):
        self.buffer.reset_index(drop=True, inplace=True)

        if idx < 1 or idx > self.buffer_size-1:
            print("Warning: wrong index given")

        point = self.buffer.iloc[idx]
        prev_point = self.buffer.iloc[max(idx - 1, 0)]
        prev_prev_point = self.buffer.iloc[max(idx - 2, 0)]
        next_point = self.buffer.iloc[min(idx + 1, len(self.buffer) - 1)]
        next_next_point = self.buffer.iloc[min(idx + 2, len(self.buffer)-1)]

        if (idx-1) != 0:
            self.buffer.at[idx-1, 'value'] = max(self.ped(prev_point, next_point, prev_prev_point), self.ped(point, next_point, prev_prev_point))
        else:
            self.buffer.at[idx-1, 'value'] = 0

        if (idx+1) != self.buffer_size + 1 and (min(idx + 2, len(self.buffer)-1) != min(idx + 1, len(self.buffer) - 1)):
            self.buffer.at[idx+1, 'value'] = max(self.ped(next_point, next_next_point, prev_point), self.ped(point, next_next_point, prev_point))
        else:
            self.buffer.at[idx+1, 'value'] = 0

    def get_state(self):
        if len(self.buffer) < self.k:
            return np.array([]), []

        errors = self.buffer['value'].iloc[1:-1].sort_values()[:self.k]
        state = errors.values
        indices = errors.index.tolist()
        return state, indices

    def step(self, action):
        done = False
        state, indices = self.get_state()

        if self.current_index < len(self.original_trajectory):
            next_point = self.original_trajectory.iloc[self.current_index] # skal scannes som 0,0
            current_point = self.original_trajectory.iloc[self.current_index-1] #skal have ny værdi
            prev_point = self.original_trajectory.iloc[self.current_index-2]  #tidligere sidste værdi

            self.buffer.at[self.buffer_size, 'value'] = self.ped(current_point, next_point, prev_point)
            self.buffer = self.buffer.reset_index(drop=True)
            self.buffer = pd.concat([self.buffer, pd.DataFrame([next_point])])
            self.buffer = self.buffer.reset_index(drop=True)

        else:
            done = True

        index_to_drop = indices[action]
        self.update_values(index_to_drop)
        self.buffer = self.buffer.drop(index_to_drop)
        self.buffer = self.buffer.reset_index(drop=True)

        self.trajectory_error = self.calculate_maximum_error()
        reward = -self.trajectory_error

        self.current_index += 1

        next_state, _ = self.get_state()
        return next_state, reward, done

    def reset(self):
        self.trajectory_error = 0
        self.buffer = self.original_trajectory.iloc[:self.buffer_size+1] # Include one extra for initial state
        self.current_index = self.buffer_size+1
        for i in range(1, self.buffer_size): #opdater værdier for p1, p2, p3
            self.buffer.at[i, 'value'] = self.ped(self.buffer.iloc[i], self.buffer.iloc[i+1], self.buffer.iloc[i-1])
        initial_state, _ = self.get_state()
        return initial_state