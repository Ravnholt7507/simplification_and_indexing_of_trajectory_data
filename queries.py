from datetime import datetime
import pandas as pd
from haversine import haversine

# range query based on time
def time_query(start_time, end_time, tree):
    result = []
    result = _time_query_rec(start_time, end_time, tree.root, result)
    return result


# recursive part of range query
def _time_query_rec(start_time, end_time, node, result):
    if node.is_leaf:
        # print(node.children)
        # print(node.mbr)
        for child in node.children:
            if datetime.strptime(child.mbr["start"], '%Y-%m-%d %H:%M:%S') >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'):

                for index, element in child.mbr["points"].iterrows():
                    # print("tested: ", element["end_time"])
                    # print("expected: ", end_time)
                    if datetime.strptime(element["end_time"], '%Y-%m-%d %H:%M:%S') <= datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'):
                        result.append(element)
    else:
        for child in node.children:
            if datetime.strptime(child.mbr["start"], '%Y-%m-%d %H:%M:%S') >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'):
                result = _time_query_rec(start_time, end_time, child, result)
    return result


# use to count elements of leafs in rtree
def count_elements(rtree):
    counter = 0
    counter = _count_elements(rtree.root, counter)
    return counter

# recursive part of count elements
def _count_elements(node, counter):
    if node.is_leaf:
        for child in node.children:
            counter += len(child.mbr["points"])
            if len(child.children) > 0:
                print("something is wrong with leafs")
        return counter
    else:
        for element in node.children:
            counter = _count_elements(element, counter)
        return counter


def range_query(coordinates, rtree):
    result = []
    result = _range_query(coordinates, rtree.root, result)
    if not None:
        print("The query returned ", len(result), " result(s)")
    return result


# recursion part of range_query
def _range_query(coordinates, node, result):
    if node.is_leaf:
        for child in node.children:
            mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
            if intersection(coordinates, mbr):
                for index, row in child.mbr["points"].iterrows():
                    point = (row["latitude"], row["longitude"])
                    if within(coordinates, point):
                        result.append(row)
    else:
        for child in node.children:
            mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
            if mbr_within(coordinates, mbr):
                result.append(child.mbr["points"])
            elif intersection(coordinates, mbr):
                _range_query(coordinates, child, result)

    return result


# using Seperating Axis Theorem
def intersection(coordinates, mbr):
    cor_x_min, cor_y_min, cor_x_max, cor_y_max = coordinates
    mbr_x_min, mbr_y_min, mbr_x_max, mbr_y_max = mbr
    return not (cor_x_max < mbr_x_min or
                cor_x_min > mbr_x_max or
                cor_y_max < mbr_y_min or
                cor_y_min > mbr_y_max)


def mbr_within(coordinates, mbr):
    mbr_x_min, mbr_y_min, mbr_x_max, mbr_y_max = mbr
    return (within(coordinates, (mbr_x_min, mbr_y_min)) and within(coordinates, (mbr_x_max, mbr_y_max)))


def within(coordinates, point):
    cor_x_min, cor_y_min, cor_x_max, cor_y_max = coordinates
    point_x, point_y = point

    if cor_x_min <= point_x and cor_y_min <= point_y and cor_x_max >= point_x and cor_y_max >= point_y:
        return True

    return False


def grid_index_range_query(bbox, grid):
    miny, minx, maxy, maxx = bbox
    result_rows = []
    x_range = range(int((minx - grid.x_min) / grid.cell_size), int((maxx - grid.x_min) / grid.cell_size) + 1)
    y_range = range(int((miny - grid.y_min) / grid.cell_size), int((maxy - grid.y_min) / grid.cell_size) + 1)
    for i in x_range:
        for j in y_range:
            key = (i, j)
            if key in grid.cells:
                result_rows.extend([{"longitude": x, "latitude": y} for x, y, _ in grid.cells[key] if minx <= x <= maxx and miny <= y <= maxy])
    print("The query returned ", len(result_rows), " result(s)")
    return pd.DataFrame(result_rows)


def naive_knn(poi, rtree):
    result = []
    _naive_knn(poi, rtree.root, result)
    if len(result) > 1:
        distances = []
        for element in result:
            distances.append(haversine((element["latitude"], element["longitude"]), poi))
        return result[distances.index(min(distances))]  

    return result
def _naive_knn(poi, node, result):
    is_within = False
    if node.is_leaf:
        distances = []
        for child in node.children:
            mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
            if within(mbr, poi):
                result.append(closest_point(child.mbr["points"], poi))
                is_within = True
        if not is_within:
            distances = []
            for child in node.children:
                mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
                distances.append(distance_rectangles(mbr, poi))
            result.append(closest_point(node.children[distances.index(min(distances))].mbr["points"], poi))
    else:
        for child in node.children:
            mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
            if within(mbr, poi):
                _naive_knn(poi, child, result)
                is_within = True 
        if not is_within:
            distances = []
            for child in node.children:
                mbr = [child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]]
                distances.append(distance_rectangles(mbr, poi))
            _naive_knn(poi, node.children[distances.index(min(distances))], result)
    return result

            
def distance_rectangles(mbr, poi):
    lat1, lon1, lat2, lon2 = mbr
    lat_p, lon_p = poi
    distances = [haversine((lat_p, lon_p), (lat1, lon1)),  # Distance to left edge
                 haversine((lat_p, lon_p), (lat1, lon2)),  # Distance to right edge
                 haversine((lat_p, lon_p), (lat2, lon1)),  # Distance to bottom edge
                 haversine((lat_p, lon_p), (lat2, lon2))   # Distance to top edge
                 ]

    return min(distances)


def closest_point(points, poi):
    distances = []
    lat_p, lon_p = poi
    for index, row in points.iterrows():
        distances.append(haversine((lat_p, lon_p), (row["latitude"], row["longitude"])))
    return points.iloc[distances.index(min(distances))]

