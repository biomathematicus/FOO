import numpy as np
import matplotlib.pyplot as plt
import random

# Step 1: Initialize Actors and Statements
num_actors = 1000
statements = ["s1", "s2"]
p12 = 0.06  # Probability that a holder of s1 changes to s2
p21 = 0.045  # Probability that a holder of s2 changes to s1

# Step 2: Define the update function for beliefs
def update_beliefs(beliefs, p12, p21):
    new_beliefs = beliefs.copy()
    for actor in beliefs:
        if beliefs[actor] == "s1" and random.random() < p12:
            new_beliefs[actor] = "s2"
        elif beliefs[actor] == "s2" and random.random() < p21:
            new_beliefs[actor] = "s1"
    return new_beliefs

# Step 3: Simulate the Network Dynamics
num_iterations = 100
epochs = 20

all_beliefs_over_time = []

for epoch in range(epochs):
    beliefs = {i: random.choice(statements) for i in range(num_actors)}
    beliefs_over_time = []
    
    for _ in range(num_iterations):
        beliefs = update_beliefs(beliefs, p12, p21)
        
        # Record the number of actors holding each belief
        count_s1 = sum(1 for belief in beliefs.values() if belief == statements[0])
        count_s2 = sum(1 for belief in beliefs.values() if belief == statements[1])
        beliefs_over_time.append((count_s1, count_s2))
    
    all_beliefs_over_time.append(beliefs_over_time)

# Convert to numpy array for easier manipulation
all_beliefs_over_time = np.array(all_beliefs_over_time)

# Calculate mean and confidence intervals
mean_beliefs_over_time = np.mean(all_beliefs_over_time, axis=0)
std_beliefs_over_time = np.std(all_beliefs_over_time, axis=0)

ci_s1_upper = mean_beliefs_over_time[:, 0] + 1.96 * std_beliefs_over_time[:, 0] / np.sqrt(epochs)
ci_s1_lower = mean_beliefs_over_time[:, 0] - 1.96 * std_beliefs_over_time[:, 0] / np.sqrt(epochs)
ci_s2_upper = mean_beliefs_over_time[:, 1] + 1.96 * std_beliefs_over_time[:, 1] / np.sqrt(epochs)
ci_s2_lower = mean_beliefs_over_time[:, 1] - 1.96 * std_beliefs_over_time[:, 1] / np.sqrt(epochs)

# Step 4: Plot the time series of beliefs
plt.figure(figsize=(10, 6))
plt.plot(mean_beliefs_over_time[:, 0], label='Mean trajectory of s1')
plt.plot(mean_beliefs_over_time[:, 1], label='Mean trajectory of s2')
plt.fill_between(range(num_iterations), ci_s1_lower, ci_s1_upper, color='blue', alpha=0.1)
plt.fill_between(range(num_iterations), ci_s2_lower, ci_s2_upper, color='red', alpha=0.1)
plt.axhline(y=num_actors * p21 / (p12 + p21), color='b', linestyle='--', label=f"Theoretical P1: {num_actors * p21 / (p12 + p21):.0f}")
plt.axhline(y=num_actors * p12 / (p12 + p21), color='r', linestyle='--', label=f"Theoretical P2: {num_actors * p12 / (p12 + p21):.0f}")
plt.xlabel('Iteration')
plt.ylabel('Number of Actors')
plt.title(f'Evolution of Beliefs Over Time (Average of {epochs} Epochs)')
plt.legend()
plt.savefig('FOO_Figure1.png', dpi=300)
plt.show()
