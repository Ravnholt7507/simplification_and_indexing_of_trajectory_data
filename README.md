# INSTALLATION:
Simply clone the project and run `pip install -r requirements`

# USAGE:
## Initializing r-tree:

```
#load data to a dataframe

points_in_mbr = 10 #define how many points there should be in the leaf nodes

rtree = init_rtree(dataframe, points_in_mbr)
```
### Plotting your rtree:
This is usefull to see if you should add more or less points in each mbr
```
plot_mbrs(longitudes, latitudes, rtree)
```

## Example of time query:
```
start_time = "2008-02-02 15:00:00"
end_time = "2008-02-03 15:36:10"
time_query(start_time, end_time, rtree)
```
## Example of range query:
```
coordinates = [39.9, 116.4, 39.95, 116.6]
range_query(coordinates, rtree)
```
### Plotting your range query:
```
plot_query(longitudes, latitudes, query_area)
```