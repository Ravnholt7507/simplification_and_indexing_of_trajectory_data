import torch
import matplotlib.pyplot as plt

def plot_side_by_side(df1, df2):
    # Create a figure with 1 row and 2 columns of subplots
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

    # Plot the first DataFrame in the first subplot
    axes[0].scatter(df1['latitude'], df1['longitude'])
    axes[0].plot(df1['latitude'], df1['longitude'], color='red')  # connect points with a line
    axes[0].set_title('Scatter Plot of First DataFrame')
    axes[0].set_xlabel('Latitude')
    axes[0].set_ylabel('Longitude')
    axes[0].grid(True)

    # Plot the second DataFrame in the second subplot
    axes[1].scatter(df2['latitude'], df2['longitude'])
    axes[1].plot(df2['latitude'], df2['longitude'], color='red')  # connect points with a line
    axes[1].set_title('Scatter Plot of Second DataFrame')
    axes[1].set_xlabel('Latitude')
    axes[1].set_ylabel('Longitude')
    axes[1].grid(True)

    # Show the plot
    plt.tight_layout()
    plt.show()

def simplify(original_trajectory, policy_network, env, threshold = 1.0):
    #env.original_trajectory = test_trajectory.assign(value=0.0)
    state = env.reset()

    done = False
    while not done:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        if env.calculate_overall_error() > threshold:
            print("threshold met")
            done = True
            break


        with torch.no_grad():  # Ensure no gradients are computed
            probs = policy_network(state_tensor)
            action = probs.argmax().item()  # Choose the best action

        next_state, _, done = env.step(action)
        state = next_state
        
    print("overall error: ", env.calculate_overall_error())
    print("compression ratio: ", env.calculate_compression_ratio())
    print("largest compression loss for single point: ", env.calculate_simplification_error())
    plot_side_by_side(original_trajectory, env.buffer)

    env.buffer = env.buffer.drop(columns=['value', 'index'])
    return env.buffer
