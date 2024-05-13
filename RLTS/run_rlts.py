import torch
from RLTS.buffer import TrajectoryEnv
from RLTS.batch_mode import BatchMode_TrajectoryEnv
from RLTS.policy import PolicyNetwork
import time
import matplotlib.pyplot as plt

def rlts(df, threshold):
    start_time = time.time()
    env = BatchMode_TrajectoryEnv(df)
    policy_network = PolicyNetwork(input_size=env.k, hidden_size=20, output_size=env.k)
    policy_network.state_dict(torch.load("RLTS/models/batch_model"))
    policy_network.eval()

    state, indices = env.reset()

    done = False
    while not done:
        state_tensor = torch.FloatTensor(state).unsqueeze(0)

        with torch.no_grad():
            probs = policy_network(state_tensor)
            action = probs.argmax().item()
            if env.exceeds_threshold(indices[action], threshold):
                print("threshold met")
                done = True
                break

        next_state, indices, _, done = env.step(action)
        indices = indices
        state = next_state

    complete_df = env.reattach_identifiers(env.buffer)
    end_time = time.time()
    print("RLTS time: ", end_time - start_time)
    return complete_df