from datetime import datetime
import math
import pandas as pd

def make_all_mbrs(df, max_points):

    rest: int = len(df) % max_points
    loops: int = math.floor(len(df)/max_points)
    i: int = 0
    rectangles = []

    while i < loops:
        rectangles.append(create_mbr(df.head(max_points)))
        df = df.iloc[max_points:]
        i += 1
    if rest != 0:
        rectangles.append(create_mbr(df))
    return rectangles

# error_bound er skal vaere i kilometer
def create_mbr(df):
    if 'datetime' in df:
        for index, row in df.iterrows():
            df.loc[index, "start_time"] = df.loc[index, "datetime"]
            df.loc[index, "end_time"] = df.loc[index, "datetime"]

    min_lat = min(df["latitude"])
    max_lat = max(df["latitude"])
    min_lon = min(df["longitude"])
    max_lon = max(df["longitude"])
    start_time = min(df["start_time"])
    end_time = max(df["end_time"])

    mbr = {
        "count": len(df),
        "min": (min_lat, min_lon),
        "max": (max_lat, max_lon),
        "points": df,
        "start": start_time,
        "end": end_time
    }
    return mbr


def init_rtree(rectangles):
    rtree = Rtree()
    for element in rectangles:
        rtree.insert(element)

    return rtree


class Node:
    def __init__(self, mbr, is_leaf=True):
        self.is_leaf = is_leaf
        self.children = []
        self.mbr = mbr


class Rtree:
    def __init__(self, max_children=5):
        self.root = Node(mbr=None)
        self.max_children = max_children

    def insert(self, mbr):
        self.insert_mbr(mbr, self.root)

    def insert_mbr(self, mbr, node):
        if node.is_leaf:
            if len(node.children) < self.max_children:
                node.children.append(Node(mbr=mbr))
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
            if len(node.children) < self.max_children:
                node.children.append(Node(mbr=None))
                node.mbr = self.expand_mbr(node.mbr, mbr)
                self.insert_mbr(mbr, node.children[-1])
            else:
                self.split_node(node)
                self.insert_mbr(mbr, node)

    @staticmethod
    def split_node(node):
        child_1 = Node(mbr=node.mbr)
        child_1.is_leaf = node.is_leaf
        node.is_leaf = False
        for element in node.children:
            child_1.children.append(element)
        node.children = [child_1]

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
        # mbr1["points"] = pd.concat([mbr1["points"], mbr2["points"]])
        if datetime.strptime(mbr1["start"], '%Y-%m-%d %H:%M:%S') > datetime.strptime(mbr2["start"], '%Y-%m-%d %H:%M:%S'):
            mbr1["start"] = mbr2["start"]
        if datetime.strptime(mbr1["end"], '%Y-%m-%d %H:%M:%S') < datetime.strptime(mbr2["end"], '%Y-%m-%d %H:%M:%S'):
            mbr1["end"] = mbr2["end"]

        return mbr1
