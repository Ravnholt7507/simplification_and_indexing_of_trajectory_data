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
