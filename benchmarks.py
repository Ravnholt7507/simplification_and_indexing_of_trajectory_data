from queries import within

def range_query_no_compression_no_indexing(coordinates, points):
    results = []
    for index, row in points.iterrows():
        point = (row["latitude"], row["longitude"])
        if within(coordinates, point):
            results.append(row)
    return results
