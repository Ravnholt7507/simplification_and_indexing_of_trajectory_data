
import matplotlib.pyplot as plt
import pandas as pd
import time
import numpy as np

class SpatialGridIndex:
    def __init__(self, dataframe, cell_size):
        self.df = dataframe
        self.cell_size = cell_size
        self.x_min = self.df['longitude'].min()
        self.x_max = self.df['longitude'].max()
        self.y_min = self.df['latitude'].min()
        self.y_max = self.df['latitude'].max()
        self.cells = {}
        self.insert_points()

    def insert_points(self):
        # Generate cell keys from dataframe coordinates
        keys = ((self.df[['longitude', 'latitude']].values - np.array([self.x_min, self.y_min])) / self.cell_size).astype(int)
        for (x, y), (longitude, latitude) in zip(keys, self.df[['longitude', 'latitude']].values):
            key_tuple = (x, y)
            if key_tuple not in self.cells:
                self.cells[key_tuple] = []
            self.cells[key_tuple].append((longitude, latitude, f"Point({longitude},{latitude})"))

def init_grid_index(df):
    return SpatialGridIndex(df, 0.05)