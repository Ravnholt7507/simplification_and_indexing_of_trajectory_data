from datetime import datetime


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
        for element in result:
            print("_________________________________")
            print(element)
            print("_________________________________")
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
            if intersection(coordinates, mbr):
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


def within(coordinates, point):
    cor_x_min, cor_y_min, cor_x_max, cor_y_max = coordinates
    point_x, point_y = point 

    if cor_x_min <= point_x and cor_y_min <= point_y and cor_x_max >= point_x and cor_y_max >= point_y:
        return True
    
    return False
