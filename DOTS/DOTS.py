# from DOTS.error import interpolate_point, euclidean_distance, sed

# class Node:
#     def __init__(self, identifier, x, y, time, parent=None):
#         self.identifier = identifier
#         self.x = x
#         self.y = y
#         self.time = time
#         self.parent = parent
#         self.children = []

#     def add_child(self, child):
#         self.children.append(child)

# class LayeredDAG:
#     def __init__(self):
#         self.layers = []  # Start with an empty list of layers
#         self.last_index = 0  # Track the last index of data points added to the DAG

#     def add_initial_node(self, identifier, x, y, time):
#         """Adds the initial node to the graph."""
#         self.layers.append([Node(identifier, x, y, time)])

#     def display(self):
#         """Prints the graph layers for visualization, including parent ID for each node."""
#         for i, layer in enumerate(self.layers, start=1):
#             #print(f"Layer {i}:")
#             for node in layer:
#                 parent_id = 'None' if node.parent is None else node.parent.identifier
#                 #print(f"  Node {node.identifier} ({node.x}, {node.y}, {node.time}) - Parent ID: {parent_id}")

#     def add_trajectory_data(self, data_points, threshold, error_multiplier=1.5):
#         """Adds trajectory data points to the DAG using the DOTS algorithm."""
#         total_error_testing = 0
#         if not self.layers:
#             # Always add the first point as the singleton node in the layered DAG
#             self.add_initial_node(*data_points[0])
#             self.last_index = 1

#         new_layer = []
#         termination_set = []
#         previous_layer = self.layers[-1]

#         for index_j, point_j in enumerate(data_points[self.last_index:]):
#             best_node = None
#             lowest_error_percentage = float('inf') #Initialize to infinity. Then any numeric value will always be lower

#             for node_i in previous_layer:
#                 if node_i.identifier in termination_set:
#                     continue

#                 # Calculate the direct total distance from point_i to point_j
#                 direct_distance = 0
#                 for intermediate_index in range(node_i.identifier-1, point_j[0]-1):
#                     if intermediate_index < len(data_points) - 1:  # Ensure not out of bounds
#                         next_point = data_points[intermediate_index + 1]
#                         direct_distance += euclidean_distance((data_points[intermediate_index][1], data_points[intermediate_index][2]),
#                                                               (next_point[1], next_point[2]))

#                 # Calculate the total error for all points between point_i and point_j
#                 total_error = 0
#                 for intermediate_index in range(node_i.identifier, point_j[0]-1):
#                     intermediate_point = data_points[intermediate_index]
#                     error = sed((node_i.x, node_i.y, node_i.time),
#                                 (point_j[1], point_j[2], point_j[3]),
#                                 (intermediate_point[1], intermediate_point[2], intermediate_point[3]))**2
#                     total_error += error
#                 #print(f"Comparing {node_i.identifier} to {point_j[0]}: Direct distance = {direct_distance}, Total error = {total_error}")

#                 # Normalize error as a percentage of the direct distance
#                 error_percentage = (abs(((total_error / direct_distance) ) * 100)) if direct_distance != 0 else 0
#                 #print(f"Error_percentage between point {node_i.identifier} and {point_j[0]}: {error_percentage}%")

#                 if error_percentage < min(lowest_error_percentage, threshold):
#                     total_error_testing += total_error
#                     lowest_error_percentage = error_percentage
#                     best_node = node_i
#                     #print(f"Error percentage Updated: Point {node_i.identifier} added as best parent node for point {point_j[0]}")

#                 if error_percentage > error_multiplier * threshold:
#                     termination_set.append(node_i.identifier)
#                     #print(f"Point {node_i.identifier} has beeen added to the termination set")

#             # Check if the best node found is suitable to be the parent of the new node
#             if best_node and lowest_error_percentage < threshold:
#                 new_node = Node(point_j[0], point_j[1], point_j[2], point_j[3], parent=best_node)
#                 best_node.add_child(new_node)
#                 new_layer.append(new_node)
#                 self.last_index = point_j[0]  # Update last index as a new node is successfully added
#                 #print(f"The new layer currently contains: ")
#                 for node in new_layer:
#                     parent_id = 'None' if node.parent is None else node.parent.identifier
#                     #print(f"  Node {node.identifier} ({node.x}, {node.y}, {node.time}) - Parent ID: {parent_id}")

#             if len(termination_set) == len(previous_layer) or point_j[0] == len(data_points):
#                 #print("Termination set contains all nodes from previous layer in the DAG. Current layer construction is done.")
#                 if new_layer is not None:
#                    self.layers.append(new_layer)
#                 # If the termination set now has all the nodes from the previous layer, break
#                 break

#         return total_error_testing

#     def run_dots(self, data_points, threshold, error_multiplier=1.5):
#         i = 0
#         total_error_testing = 0
#         while i < len(data_points):
#             #print(f"Attempting construction of layer ")
#             total_error_testing += self.add_trajectory_data(data_points, threshold, error_multiplier)
#             if len(data_points) == self.last_index: # If no progress, break to prevent infinite loop
#                 break
#             i+1
#         print("total sed error for DOTS: ", total_error_testing)
#         return total_error_testing

#     def decode_trajectory(self):
#         """Decodes the trajectory from the last node with the highest identifier back to the initial node."""
#         if not self.layers:
#             return []

#         # Start from the last layer and find the node with the highest identifier
#         last_layer = self.layers[-1]
#         end_node = max(last_layer, key=lambda node: node.identifier)

#         # Traverse from the end node back to the start node
#         trajectory = []
#         current_node = end_node
#         while current_node is not None:
#             trajectory.append((current_node.identifier, current_node.x, current_node.y, current_node.time))
#             current_node = current_node.parent

#         # Since we traced from end to start, reverse the trajectory to start-to-end order
#         trajectory.reverse()
#         return trajectory

#     def pretty_print_decode(self):
#         trajectory = self.decode_trajectory()
#         pretty_print = []
#         for node in trajectory:
#             pretty_print.append(f"Point {node[0]}")
#         return pretty_print

from DOTS.error import interpolate_point, euclidean_distance, sed

class Node:
    def __init__(self, identifier, x, y, time, parent=None):
        self.identifier = identifier
        self.x = x
        self.y = y
        self.time = time
        self.parent = parent
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class LayeredDAG:
    def __init__(self):
        self.layers = []  # Start with an empty list of layers
        self.last_index = 0  # Track the last index of data points added to the DAG

    def add_initial_node(self, identifier, x, y, time):
        """Adds the initial node to the graph."""
        self.layers.append([Node(identifier, x, y, time)])

    def display(self):
        """Prints the graph layers for visualization, including parent ID for each node."""
        for i, layer in enumerate(self.layers, start=1):
            for node in layer:
                parent_id = 'None' if node.parent is None else node.parent.identifier

    def add_trajectory_data(self, data_points, threshold, error_multiplier=1.5):
        """Adds trajectory data points to the DAG using the DOTS algorithm."""
        total_error_testing = 0
        if not self.layers:
            # Always add the first point as the singleton node in the layered DAG
            self.add_initial_node(*data_points[0])
            self.last_index = 1

        new_layer = []
        termination_set = set()
        previous_layer = self.layers[-1]

        # Precompute euclidean distances to avoid recalculating them repeatedly
        precomputed_distances = {}
        for i in range(len(data_points) - 1):
            precomputed_distances[i] = euclidean_distance((data_points[i][1], data_points[i][2]), 
                                                          (data_points[i+1][1], data_points[i+1][2]))

        for point_j in data_points[self.last_index:]:
            best_node = None
            lowest_error_percentage = float('inf')  # Initialize to infinity. Then any numeric value will always be lower

            for node_i in previous_layer:
                if node_i.identifier in termination_set:
                    continue

                # Calculate the direct total distance from point_i to point_j
                direct_distance = sum(precomputed_distances[idx] for idx in range(node_i.identifier-1, point_j[0]-1) if idx < len(data_points) - 1)

                # Calculate the total error for all points between point_i and point_j
                total_error = sum(sed((node_i.x, node_i.y, node_i.time),
                                      (point_j[1], point_j[2], point_j[3]),
                                      (data_points[intermediate_index][1], data_points[intermediate_index][2], data_points[intermediate_index][3]))**2
                                  for intermediate_index in range(node_i.identifier, point_j[0]-1))

                # Normalize error as a percentage of the direct distance
                error_percentage = (abs(((total_error / direct_distance) ) * 100)) if direct_distance != 0 else 0

                if error_percentage < min(lowest_error_percentage, threshold):
                    total_error_testing += total_error
                    lowest_error_percentage = error_percentage
                    best_node = node_i

                if error_percentage > error_multiplier * threshold:
                    termination_set.add(node_i.identifier)

            # Check if the best node found is suitable to be the parent of the new node
            if best_node and lowest_error_percentage < threshold:
                new_node = Node(point_j[0], point_j[1], point_j[2], point_j[3], parent=best_node)
                best_node.add_child(new_node)
                new_layer.append(new_node)
                self.last_index = point_j[0]  # Update last index as a new node is successfully added

            if len(termination_set) == len(previous_layer) or point_j[0] == len(data_points):
                if new_layer is not None:
                    self.layers.append(new_layer)
                break

        return total_error_testing

    def run_dots(self, data_points, threshold, error_multiplier=1.5):
        total_error_testing = 0
        while self.last_index < len(data_points):
            total_error_testing += self.add_trajectory_data(data_points, threshold, error_multiplier)
            if len(data_points) == self.last_index:  # If no progress, break to prevent infinite loop
                break
        print("total sed error for DOTS: ", total_error_testing)
        return total_error_testing

    def decode_trajectory(self):
        """Decodes the trajectory from the last node with the highest identifier back to the initial node."""
        if not self.layers:
            return []

        # Start from the last layer and find the node with the highest identifier
        last_layer = self.layers[-1]
        end_node = max(last_layer, key=lambda node: node.identifier)

        # Traverse from the end node back to the start node
        trajectory = []
        current_node = end_node
        while current_node is not None:
            trajectory.append((current_node.identifier, current_node.x, current_node.y, current_node.time))
            current_node = current_node.parent

        # Since we traced from end to start, reverse the trajectory to start-to-end order
        trajectory.reverse()
        return trajectory

    def pretty_print_decode(self):
        trajectory = self.decode_trajectory()
        pretty_print = []
        for node in trajectory:
            pretty_print.append(f"Point {node[0]}")
        return pretty_print
