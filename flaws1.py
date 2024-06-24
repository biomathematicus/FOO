import numpy as np
import matplotlib.pyplot as plt
import random

# Step 1: Initialize Actors and Statements
num_actors = 1000
statements = ["s1", "s2"]
beliefs = {i: random.choice(statements) for i in range(num_actors)}

# Step 2: Define the probabilities for changing beliefs
p12 = 0.06  # Probability that a holder of s1 changes to s2
p21 = 0.045  # Probability that a holder of s2 changes to s1
# https://nij.ojp.gov/topics/articles/domestic-radicalization-and-deradicalization-insights-family-and-friends

# Step 3: Define the update function for beliefs
def update_beliefs(beliefs, p12, p21):
    new_beliefs = beliefs.copy()
    for actor in beliefs:
        if beliefs[actor] == "s1" and random.random() < p12:
            new_beliefs[actor] = "s2"
        elif beliefs[actor] == "s2" and random.random() < p21:
            new_beliefs[actor] = "s1"
    return new_beliefs

# Step 4: Simulate the Network Dynamics
num_iterations = 1000
beliefs_over_time = []

for _ in range(num_iterations):
    beliefs = update_beliefs(beliefs, p12, p21)
    
    # Record the number of actors holding each belief
    count_s1 = sum(1 for belief in beliefs.values() if belief == statements[0])
    count_s2 = sum(1 for belief in beliefs.values() if belief == statements[1])
    beliefs_over_time.append((count_s1, count_s2))

# Step 5: Plot the time series of beliefs
beliefs_over_time = np.array(beliefs_over_time)
plt.figure(figsize=(10, 6))
plt.plot(beliefs_over_time[:, 0], label='Belief s1')
plt.plot(beliefs_over_time[:, 1], label='Belief s2')
plt.xlabel('Iteration')
plt.ylabel('Number of Actors')
plt.title('Evolution of Beliefs Over Time')
plt.legend()
plt.savefig('FOO_Figure1.png', dpi=300)
plt.show()
x
# plt.savefig('FOO_Figure1.pdf')
