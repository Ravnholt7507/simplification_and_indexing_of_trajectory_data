import numpy as np
from pympler import asizeof

class MemoryTracker:
    def __init__(self):
        self.memory_usages = []

    def track_memory_usage(self, obj):
        current_usage = asizeof.asizeof(obj)
        self.memory_usages.append(current_usage)
        return current_usage

    def get_peak_memory_usage(self):
        return max(self.memory_usages)

    def get_average_memory_usage(self):
        return sum(self.memory_usages) / len(self.memory_usages)

    def get_memory_overhead(self, raw_data_size):
        peak_usage = self.get_peak_memory_usage()
        return peak_usage - raw_data_size