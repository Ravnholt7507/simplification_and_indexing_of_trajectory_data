# import pandas as pd
# import numpy as np

# class SpatialGridIndex:
#     def __init__(self, dataframe, cell_size):
#         self.df = dataframe.copy()
#         self.cell_size = cell_size
#         self.x_min = self.df['longitude'].min()
#         self.x_max = self.df['longitude'].max()
#         self.y_min = self.df['latitude'].min()
#         self.y_max = self.df['latitude'].max()
#         self.df['cell_x'] = ((self.df['longitude'] - self.x_min) / self.cell_size).astype(int)
#         self.df['cell_y'] = ((self.df['latitude'] - self.y_min) / self.cell_size).astype(int)
#         self.cells = {}
#         self.insert_points()

#     def insert_points(self):
#         for _, row in self.df.iterrows():
#             key_tuple = (row['cell_x'], row['cell_y'])
#             if key_tuple not in self.cells:
#                 self.cells[key_tuple] = []
#             self.cells[key_tuple].append((row['longitude'], row['latitude'], f"Point({row['longitude']},{row['latitude']})"))

#     def insert_point(self, point):
#         longitude, latitude = point
#         cell_x = int((longitude - self.x_min) / self.cell_size)
#         cell_y = int((latitude - self.y_min) / self.cell_size)
#         key_tuple = (cell_x, cell_y)
#         if key_tuple not in self.cells:
#             self.cells[key_tuple] = []
#         self.cells[key_tuple].append((longitude, latitude, f"Point({longitude},{latitude})"))
        
#         new_row = pd.DataFrame({'longitude': [longitude], 'latitude': [latitude], 'cell_x': [cell_x], 'cell_y': [cell_y]})
#         self.df = pd.concat([self.df, new_row], ignore_index=True)

#     def remove_point(self, point):
#         longitude, latitude = point
#         cell_x = int((longitude - self.x_min) / self.cell_size)
#         cell_y = int((latitude - self.y_min) / self.cell_size)
#         key_tuple = (cell_x, cell_y)
#         if key_tuple in self.cells:
#             self.cells[key_tuple].remove((longitude, latitude, f"Point({longitude},{latitude})"))
#             if not self.cells[key_tuple]:
#                 del self.cells[key_tuple]
#             self.df = self.df[~((self.df['longitude'] == longitude) & (self.df['latitude'] == latitude))]

#     def _get_cell(self, point):
#         longitude, latitude = point
#         cell_x = int((longitude - self.x_min) / self.cell_size)
#         cell_y = int((latitude - self.y_min) / self.cell_size)
#         return (cell_x, cell_y)

#     def _get_surrounding_cells(self, cell):
#         cell_x, cell_y = cell
#         cells = [(cell_x + i, cell_y + j) for i in range(-1, 2) for j in range(-1, 2)]
#         return cells
    
# def init_grid_index(df):
#     return SpatialGridIndex(df, 0.05)

import pandas as pd
import numpy as np
import time

class SpatialGridIndex:
    def __init__(self, dataframe, cell_size):
        self.df = dataframe.copy()
        self.cell_size = cell_size
        self.x_min = self.df['longitude'].min()
        self.x_max = self.df['longitude'].max()
        self.y_min = self.df['latitude'].min()
        self.y_max = self.df['latitude'].max()
        self.df['cell_x'] = ((self.df['longitude'] - self.x_min) / self.cell_size).astype(int)
        self.df['cell_y'] = ((self.df['latitude'] - self.y_min) / self.cell_size).astype(int)
        self.cells = {}
        self.insert_points()

    def insert_points(self):
        for _, row in self.df.iterrows():
            key_tuple = (row['cell_x'], row['cell_y'])
            if key_tuple not in self.cells:
                self.cells[key_tuple] = []
            point = (row['longitude'], row['latitude'], f"Point({row['longitude']},{row['latitude']})")
            self.cells[key_tuple].append(point)
         #   print(f"Inserted {point} into cell {key_tuple}")
            
    def insert_point(self, point):
     #   print("Insert point:", point)
        longitude, latitude = point
        cell_x = int((longitude - self.x_min) / self.cell_size)
        cell_y = int((latitude - self.y_min) / self.cell_size)
        key_tuple = (cell_x, cell_y)
        if key_tuple not in self.cells:
            self.cells[key_tuple] = []
        self.cells[key_tuple].append((longitude, latitude, f"Point({longitude},{latitude})"))
     #   print(f"Inserted {(longitude, latitude, f'Point({longitude},{latitude})')} into cell {key_tuple}")

        new_row = pd.DataFrame({'longitude': [longitude], 'latitude': [latitude], 'cell_x': [cell_x], 'cell_y': [cell_y]})
        self.df = pd.concat([self.df, new_row], ignore_index=True)

    def remove_point(self, point):
    #    print("Remove point:", point)
        longitude, latitude = point
        cell_x = int((longitude - self.x_min) / self.cell_size)
        cell_y = int((latitude - self.y_min) / self.cell_size)
        key_tuple = (cell_x, cell_y)
        if key_tuple in self.cells:
            try:
                self.cells[key_tuple].remove((longitude, latitude, f"Point({longitude},{latitude})"))
                #print(f"Removed {(longitude, latitude, f'Point({longitude},{latitude})')} from cell {key_tuple}")
                if not self.cells[key_tuple]:
                    del self.cells[key_tuple]
                self.df = self.df[~((self.df['longitude'] == longitude) & (self.df['latitude'] == latitude))]
            except ValueError:
                None

    def _get_cell(self, point):
        longitude, latitude = point
        cell_x = int((longitude - self.x_min) / self.cell_size)
        cell_y = int((latitude - self.y_min) / self.cell_size)
        return (cell_x, cell_y)

    def _get_surrounding_cells(self, cell):
        cell_x, cell_y = cell
        cells = [(cell_x + i, cell_y + j) for i in range(-1, 2) for j in range(-1, 2)]
        return cells

# Function to initialize the grid index from data
def init_grid_index(data):
    if isinstance(data, np.ndarray):
        df = pd.DataFrame(data, columns=['latitude', 'longitude'])
    elif isinstance(data, pd.DataFrame):
        df = data
    return SpatialGridIndex(df, 0.05)