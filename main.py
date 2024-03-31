import pandas.core.frame
from haversine import haversine
import pandas as pd
import math


# another test comment
def main():
    mbr_points = 10
    df = pd.read_csv("release/taxi_log_2008_by_id/1.txt",
                     sep=",",
                     names=["taxi_id", "datetime", "longitude", "latitude"])

    final_df = pmc_midrange(df, 0.02)
    rest: int = len(final_df) % mbr_points
    loops: int = math.floor(len(final_df)/mbr_points)
    i: int = 0
    rectangles = []

    while i < loops:
        rectangles.append(create_mbr(final_df.head(mbr_points)))
        final_df = final_df.iloc[mbr_points:]
        i += 1
    if rest != 0:
        rectangles.append(create_mbr(final_df))

    rtree = Rtree()
    for element in rectangles:
        rtree.insert(element)

    pretty_print(rtree)

    return rtree


# error_bound er skal vaere i kilometer
def pmc_midrange(df: pandas.core.frame.DataFrame, error_bound: int):
    current_lat = df["latitude"].iloc[0]
    current_lon = df["longitude"].iloc[0]
    list_taxi_id = [df["taxi_id"].iloc[0]]
    list_start_time = [df["datetime"].iloc[0]]
    list_longitude = [df["longitude"].iloc[0]]
    list_latitude = [df["latitude"].iloc[0]]
    list_end_time = []
    list_counter = []
    counter = 1

    for i, row in df.iterrows():
        if haversine((current_lat, current_lon), (row["latitude"], row["longitude"])) > error_bound:
            list_end_time.append(df["datetime"].iloc[i-1])
            list_counter.append(counter)

            list_taxi_id.append(row["taxi_id"])
            list_start_time.append(row["datetime"])
            list_longitude.append(row["longitude"])
            list_latitude.append(row["latitude"])
            current_lat = df["latitude"].iloc[i]
            current_lon = df["longitude"].iloc[i]
            counter = 1
        else:
            counter += 1
    list_end_time.append(df["datetime"].iloc[-1])
    list_counter.append(counter)

    list_concat = {
        "taxi_id": list_taxi_id,
        "start_time": list_start_time,
        "longitude": list_longitude,
        "latitude": list_latitude,
        "counter": list_counter,
        "end_time": list_end_time
    }

    pmc_df = pd.DataFrame(list_concat)
    return pmc_df


def create_mbr(df: pandas.core.frame.DataFrame):
    min_lat = min(df["latitude"])
    max_lat = max(df["latitude"])
    min_lon = min(df["longitude"])
    max_lon = max(df["longitude"])

    mbr = {
        "count": len(df),
        "min": (min_lat, min_lon),
        "max": (max_lat, max_lon),
        "points": df
    }

    return mbr


class Node:
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.children = []
        self.mbr = None


class Rtree:
    def __init__(self, max_children=5):
        self.root = Node()
        self.max_children = max_children

    def insert(self, mbr):
        self.insert_mbr(mbr, self. root)

    def insert_mbr(self, mbr, node):
        if node.is_leaf:
            if len(node.children) < self.max_children:
                node.children.append(mbr)
                if node.mbr is None:
                    node.mbr = mbr
                else:
                    node.mbr = self.expand_mbr(node.mbr, mbr)
            else:
                self.split_node(node)
                self.insert_mbr(mbr, node)
        else:
            for child in node.children:
                if len(child.children) < self.max_children:
                    self.insert_mbr(mbr, child)
                    node.mbr = self.expand_mbr(node.mbr, mbr)
                    return
            self.insert_mbr(mbr, node.children[0])
            node.mbr = self.expand_mbr(node.mbr, mbr)

    @staticmethod
    def split_node(node):
        node.is_leaf = False
        child_1 = Node()
        child_2 = Node()
        child_1.mbr = node.mbr
        child_1.children = node.children
        node.children = [child_1, child_2]

    @staticmethod
    def expand_mbr(mbr1, mbr2):
        x_min1, y_min1, x_max1, y_max1 = mbr1["min"][0], mbr1["min"][1], mbr1["max"][0], mbr1["max"][1]
        x_min2, y_min2, x_max2, y_max2 = mbr2["min"][0], mbr2["min"][1], mbr2["max"][0], mbr2["max"][1]

        x_min = min(x_min1, x_min2)
        y_min = min(y_min1, y_min2)
        x_max = max(x_max1, x_max2)
        y_max = max(y_max1, y_max2)

        mbr1["min"] = (x_min, y_min)
        mbr1["max"] = (x_max, y_max)

        return mbr1


def pretty_print(rtree):
    print("R-tree:")
    _pretty_print_rec(rtree.root)


def _pretty_print_rec(node):
    if node.is_leaf:
        print('Leaf:', node.children)
    else:
        print('Internal Node:', node.mbr)
        for child in node.children:
            _pretty_print_rec(child)


print(main())

