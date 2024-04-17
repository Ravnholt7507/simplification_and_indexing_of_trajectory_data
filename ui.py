import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_query(longitudes, latitudes, query_area=None):
    fig, ax = plt.subplots()
    ax.plot(longitudes, latitudes)
    if query_area is not None:
        lat1, lon1, lat2, lon2 = query_area
        rect = patches.Rectangle((lon1, lat1),
                                 lon2-lon1,
                                 lat2-lat1,
                                 linewidth=1,
                                 edgecolor='r',
                                 facecolor='none')
        ax.add_patch(rect)

    plt.show()

def plot_mbrs(longitudes, latitudes, rtree):
    _, ax = plt.subplots()
    ax.plot(longitudes, latitudes)
    pretty_print_rec(rtree.root, ax)
    plt.show()

def pretty_print_rec(node, ax):
    if node.is_leaf:
        for child in node.children:
            print('Leaf:', child.mbr)
            lat1, lon1, lat2, lon2 = child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]
            rect = patches.Rectangle((lon1, lat1),
                                     lon2-lon1,
                                     lat2-lat1,
                                     linewidth=1,
                                     edgecolor='r',
                                     facecolor='none')
            ax.add_patch(rect)
    else:
        print('Internal Node:', len(node.children))
        for child in node.children:
            
            lat1, lon1, lat2, lon2 = child.mbr["min"][0], child.mbr["min"][1], child.mbr["max"][0], child.mbr["max"][1]
            rect = patches.Rectangle((lon1, lat1),
                                     lon2-lon1,
                                     lat2-lat1,
                                     linewidth=1,
                                     edgecolor='r',
                                     facecolor='none')
            ax.add_patch(rect)
            
            pretty_print_rec(child, ax)
