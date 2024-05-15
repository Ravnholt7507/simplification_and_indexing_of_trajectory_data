import pandas as pd
import numpy as np

class SquishE:
    class PriorityQueue:
        def __init__(self):
            self.elements = []

        def empty(self):
            return len(self.elements) == 0

        def put(self, item, priority):
            self.elements.append((priority, item))
            self.elements.sort(reverse=True)

        def get(self):
            return self.elements.pop()[1]

    @staticmethod
    def calculate_sed(pi, pj, pk):
        """ Calculate Synchronized Euclidean Distance (SED) """
        xi, yi = pi
        xj, yj = pj
        xk, yk = pk

        num = abs((yk - yi) * (xj - xi) - (xk - xi) * (yj - yi))
        den = np.sqrt((yk - yi)**2 + (xk - xi)**2)
        return num / den if den != 0 else 0

    def __init__(self, df, compression_ratio):
        self.df = df
        self.compression_ratio = compression_ratio

    def compress(self):
        trajectory = self.df.values.tolist()
        n = len(trajectory)
        target_size = max(int(n / self.compression_ratio), 2)  # Ensure at least two points are retained
        pq = self.PriorityQueue()
        pred = {}
        succ = {}
        priority = {}
        
        # First and last points are fixed
        first_point, last_point = 0, len(trajectory) - 1
        priority[first_point] = float('inf')
        priority[last_point] = float('inf')
        
        for i in range(1, len(trajectory) - 1):
            priority[i] = float('inf')
            succ[i - 1] = i
            pred[i] = i - 1

            if len(pq.elements) < target_size - 2:  # -2 because first and last points are fixed
                if i > 1:
                    priority[i - 1] = self.calculate_sed(
                        trajectory[pred[i]], trajectory[i - 1], trajectory[i]
                    )
                pq.put(i, priority[i])
            else:
                while len(pq.elements) > target_size - 2:
                    min_priority_point = pq.get()
                    if min_priority_point in pred and min_priority_point in succ:
                        prev_point = pred[min_priority_point]
                        next_point = succ[min_priority_point]

                        if prev_point in succ and next_point in pred:
                            succ[prev_point] = next_point
                            pred[next_point] = prev_point

                        del pred[min_priority_point]
                        del succ[min_priority_point]

                        if prev_point in priority:
                            priority[prev_point] = self.calculate_sed(
                                trajectory[prev_point], trajectory[min_priority_point], trajectory[next_point]
                            )
                        if next_point in priority:
                            priority[next_point] = self.calculate_sed(
                                trajectory[prev_point], trajectory[next_point], trajectory[succ.get(next_point, next_point)]
                            )

        compressed_indices = [first_point] + sorted([i for _, i in pq.elements]) + [last_point]
        compressed_trajectory = [trajectory[i] for i in compressed_indices]
        return pd.DataFrame(compressed_trajectory, columns=self.df.columns)
    

def squish(df, compression_ratio):
    squishe = SquishE(df, compression_ratio)
    simplified_df = squishe.compress()
    return simplified_df
