import numpy as np
import matplotlib.pyplot as plt
import random

# Parameters
num_actors = 1000
statements = ["s1", "s2"]
initial_energy = 1000
replenish_rate = 100
e_s1 = 10 # Energy required to verify s1
e_s2 = 3  # Energy required to verify s2
k12 = 0.03
k21 = 0.02

# Initialize beliefs and energy budgets
beliefs = {i: random.choice(statements) for i in range(num_actors)}
energies = {i: initial_energy for i in range(num_actors)}
f_s1 = {i: 0 for i in range(num_actors)}
f_s2 = {i: 0 for i in range(num_actors)}

# Interaction function
def interact(actor_from, actor_to, beliefs, energies, f_s1, f_s2, e_s1, e_s2, replenish_rate):
    statement = beliefs[actor_from]
    if statement == "s1":
        if energies[actor_to] >= e_s1:
            energies[actor_to] -= e_s1
            f_s1[actor_to] += 1
    else:
        if energies[actor_to] >= e_s2:
            energies[actor_to] -= e_s2
            f_s2[actor_to] += 1
    energies[actor_to] += replenish_rate

# Update function for beliefs
def update_beliefs(beliefs, f_s1, f_s2, k12, k21):
    new_beliefs = beliefs.copy()
    for actor in beliefs:
        p12 = k12 * f_s2[actor]
        p21 = k21 * f_s1[actor]
        if beliefs[actor] == "s1" and random.random() < p12:
            new_beliefs[actor] = "s2"
        elif beliefs[actor] == "s2" and random.random() < p21:
            new_beliefs[actor] = "s1"
    return new_beliefs

# Simulation
num_iterations = 10000
beliefs_over_time = []

for _ in range(num_iterations):
    actor_from = random.choice(range(num_actors))
    actor_to = random.choice(range(num_actors))
    if actor_from != actor_to:
        interact(actor_from, actor_to, beliefs, energies, f_s1, f_s2, e_s1, e_s2, replenish_rate)
    
    beliefs = update_beliefs(beliefs, f_s1, f_s2, k12, k21)
    
    # Record the number of actors holding each belief
    count_s1 = sum(1 for belief in beliefs.values() if belief == statements[0])
    count_s2 = sum(1 for belief in beliefs.values() if belief == statements[1])
    beliefs_over_time.append((count_s1, count_s2))

# Plot the time series of beliefs
beliefs_over_time = np.array(beliefs_over_time)
plt.figure(figsize=(10, 6))
plt.plot(beliefs_over_time[:, 0], label='Belief s1')
plt.plot(beliefs_over_time[:, 1], label='Belief s2')
plt.xlabel('Iteration')
plt.ylabel('Number of Actors')
plt.title('Evolution of Beliefs Over Time with Verification Energy')
plt.legend()
plt.show()

plt.savefig('FOO_Figure2.pdf', dpi=300)
