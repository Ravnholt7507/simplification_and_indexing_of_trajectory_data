from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from DOTS import Node, LayeredDAG

# Sample data points with identifiers, coordinates (x, y), and a simple integer time step
data_points = [
    (1, 0, 0, datetime.now()),
    (2, 1, 2, datetime.now() + timedelta(seconds=1)),
    (3, 2, 4, datetime.now() + timedelta(seconds=2)),
    (4, 3, 6, datetime.now() + timedelta(seconds=3)),
    (5, 5, 8, datetime.now() + timedelta(seconds=4)),
    (6, 8, 10, datetime.now() + timedelta(seconds=5)),
    (7, 10, 10, datetime.now() + timedelta(seconds=6)),
    (8, 13, 10, datetime.now() + timedelta(seconds=7))
]

threshold = 5.1

error_multiplier = 1.5

dag = LayeredDAG()

dag.run_dots(data_points, threshold, error_multiplier)

dag.display()


decoded_trajectory = dag.decode_trajectory()
print(decoded_trajectory)
s = dag.pretty_print_decode()
print(s)


## For visual reprsentation of result
x1, y1 = zip(*[(x, y) for _, x, y, _ in data_points])
x2, y2 = zip(*[(x, y) for _, x, y, _ in decoded_trajectory])

# Create plots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plotting the first dataset
ax1.plot(x1, y1, marker='o', linestyle='-', color='blue')
ax1.set_title('Original Trajectory')
ax1.set_xlabel('X Coordinate')
ax1.set_ylabel('Y Coordinate')
ax1.grid(True)

# Plotting the second dataset
ax2.plot(x2, y2, marker='o', linestyle='-', color='green')
ax2.set_title('DOTS simplified Trajectory')
ax2.set_xlabel('X Coordinate')
ax2.set_ylabel('Y Coordinate')
ax2.grid(True)

plt.tight_layout()
plt.show()