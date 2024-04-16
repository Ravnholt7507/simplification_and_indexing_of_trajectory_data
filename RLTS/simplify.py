import torch

def simplify(test_trajectory, policy_network, env):

    env.original_trajectory = test_trajectory.assign(value=0.0)
    state = env.reset()

    done = False
    while not done:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():  # Ensure no gradients are computed
            probs = policy_network(state_tensor)
            action = probs.argmax().item()  # Choose the best action

        next_state, _, done = env.step(action)
        state = next_state

    print("compression ratio: ", env.calculate_compression_ratio())
    print("largest compression loss for single point: ", env.calculate_simplification_error())

    return env.buffer