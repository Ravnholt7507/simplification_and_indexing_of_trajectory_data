from r_tree import Rtree
from datetime import datetime


# range query based on time
def time_query(start_time, end_time, tree):
    result = []
    result = _time_query_rec(start_time, end_time, tree.root, result)
    return result


def _time_query_rec(start_time, end_time, node, result):
    if node.is_leaf:
        # print(node.children)
        # print(node.mbr)
        for child in node.children:
            if datetime.strptime(child.mbr["start"], '%Y-%m-%d %H:%M:%S') >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'):
                
                for index, element in child.mbr["points"].iterrows():
                    print("tested: ", element["end_time"])
                    print("expected: ", end_time)
                    if datetime.strptime(element["end_time"], '%Y-%m-%d %H:%M:%S') < datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'):
                        result.append(element)
    else:
        for child in node.children:
            if datetime.strptime(child.mbr["start"], '%Y-%m-%d %H:%M:%S') >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'):
                _time_query_rec(start_time, end_time, child, result)
    return result


def count_elements(rtree):
    counter = 0
    counter = _count_elements(rtree.root, counter)
    return counter


def _count_elements(node, counter):
    if node.is_leaf:
        for child in node.children:
            counter += len(child.mbr["points"])
            if len(child.children) > 0:
                print("something is wrong with leafs")
        return counter
    else:
        for element in node.children:
            counter += _count_elements(element, counter)
        return counter
