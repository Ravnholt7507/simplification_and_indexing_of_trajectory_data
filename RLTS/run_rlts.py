import torch
from RLTS.buffer import TrajectoryEnv
from RLTS.batch_mode import BatchMode_TrajectoryEnv
from RLTS.policy import PolicyNetwork
from RLTS.train import train
import time
import matplotlib.pyplot as plt

def rlts(df, size, spatial_index = None, mode="online"):
    start_time = time.time()
    #env = BatchMode_TrajectoryEnv(df)
    env = TrajectoryEnv(df, size, spatial_index)
    policy_network = PolicyNetwork(input_size=env.k, hidden_size=20, output_size=env.k)
    #train(env, policy_network, 100)
    policy_network.state_dict(torch.load("RLTS/models/online_model"))
    policy_network.eval()

    state, indices = env.reset()

    done = False
    while not done:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():
            probs = policy_network(state_tensor)
            action = probs.argmax().item()

        next_state, indices, _, done = env.step(action)
        indices = indices
        state = next_state

    complete_df = env.reattach_identifiers(env.buffer)
    end_time = time.time()
    total_error = env.calculate_overall_error()
    print("RLTS time: ", end_time - start_time)

    # Get and print memory statistics
    memory_stats = env.get_memory_statistics()
    print("Memory Statistics:", memory_stats)

    return complete_df, total_error