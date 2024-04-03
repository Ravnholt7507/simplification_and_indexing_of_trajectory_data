# error_bound er skal vaere i kilometer
def create_mbr(df):
    min_lat = min(df["latitude"])
    max_lat = max(df["latitude"])
    min_lon = min(df["longitude"])
    max_lon = max(df["longitude"])
    start_time = df["start_time"].iloc[0]
    end_time = df["end_time"].iloc[-1]

    mbr = {
        "count": len(df),
        "min": (min_lat, min_lon),
        "max": (max_lat, max_lon),
        "points": df,
        "start": start_time,
        "end": end_time
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
        mbr1["end"] = mbr2["end"]

        return mbr1
