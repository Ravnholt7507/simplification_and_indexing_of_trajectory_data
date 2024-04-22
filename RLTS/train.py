import torch
from torch.distributions import Categorical
import torch.nn as nn
import torch.nn.functional as F

# Assume PolicyNetwork and other necessary imports and classes are defined above

def train(env, policy_network, episodes, initial_epsilon=0.9, epsilon_decay=0.995, min_epsilon=0.01, discount_factor=0.99):
    optimizer = torch.optim.Adam(policy_network.parameters(), lr=0.001)
    epsilon = initial_epsilon

    for episode in range(episodes):
        state = env.reset()
        done = False
        log_probs = []
        rewards = []
        total_reward = 0

        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            probs = policy_network(state_tensor)
            m = Categorical(probs)

            # if random.random() < epsilon:
            #     action = torch.tensor(random.choice(range(env.k)), dtype=torch.int64)
            # else:
            action = m.sample()

            log_prob = m.log_prob(action)
            next_state, reward, done = env.step(action.item())

            log_probs.append(log_prob)
            rewards.append(reward)

            state = next_state

        epsilon = max(min_epsilon, epsilon * epsilon_decay)

        # Calculate discounted rewards
        # discounted_rewards = []
        # cumulative_reward = 0
        # for reward in reversed(rewards):
        #     cumulative_reward = reward + discount_factor * cumulative_reward
        #     discounted_rewards.insert(0, cumulative_reward)

        with torch.no_grad():
            rewards = torch.tensor(rewards)
            accumulative_rewards = []
            std = rewards.std() if rewards.std() > 0 else 1e-7

            for i in range(len(rewards)):
                normalized = ((rewards[i] - rewards.mean()) / std)
                accumulative_rewards.append(normalized)

        rewards = accumulative_rewards

        # Update policy
        rewards_tensor = torch.tensor(rewards, dtype=torch.float)
        policy_loss = torch.cat([-log_prob * reward for log_prob, reward in zip(log_probs, rewards_tensor)]).sum()

        optimizer.zero_grad()
        policy_loss.backward()
        optimizer.step()

        if episode % 100 == 0:
            print(f"Episode {episode}, Loss: {policy_loss.item()}")
            torch.save(policy_network.state_dict(), "RLTS/models/test_model")