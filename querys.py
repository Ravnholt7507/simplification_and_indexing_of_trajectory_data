from r_tree import Rtree
# range query based on time
def time_query(start_time, end_time, tree:Rtree):
    result = []
    _time_query_rec(start_time, end_time, tree.root, result)
    return result

def _time_query_rec(start_time, end_time, node, result):
    if node.is_leaf:
        for mbr in node.children:
            if mbr["start"] >= start_time and mbr["end"] <= end_time:
                result.append(mbr["points"])
    else:
        for child in node.children:
            if child.mbr["start"] >= start_time and child.mbr["end"] <= end_time:
                _time_query_rec(start_time, end_time, child, result)


