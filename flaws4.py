import numpy as np
import matplotlib.pyplot as plt

# Parameters
k12 = 0.3   # Base transition rate from s1 to s2
k21 = 0.5   # Base transition rate from s2 to s1
alpha = 0.2 # Sensitivity factor for s2 interactions
beta = 5    # Adjustment for the influence of s2
gamma = 0.1 # Rate adjustment based on the prevalence of s2

# Initial states
P = np.array([0.5, 0.5])  # Start with equal belief in s1 and s2

# Time parameters
T = 1000  # Total time steps

# Interaction counts over time (simulated data)
N_s2 = np.random.poisson(lam=10, size=T)  # Number of interactions involving s2

def transition_probabilities(t):
    """Calculate transition probabilities based on the interaction frequencies."""
    p12_t = min(k12, alpha * N_s2[t] / (beta + N_s2[t]))
    p21_t = k21 * np.exp(-gamma * N_s2[t])
    return p12_t, p21_t

# Storage for tracking changes in P(t)
P_history = np.zeros((T, 2))
P_history[0] = P

# Simulate the Markov process
for t in range(1, T):
    p12_t, p21_t = transition_probabilities(t)
    T_t = np.array([
        [1 - p12_t, p12_t],
        [p21_t, 1 - p21_t]
    ])
    P = np.dot(P, T_t)
    P_history[t] = P

# Plotting the results
plt.plot(P_history[:, 0], label='Proportion believing in s1')
plt.plot(P_history[:, 1], label='Proportion believing in s2')
plt.xlabel('Time')
plt.ylabel('Proportion of Beliefs')
plt.title('Dynamics of Beliefs in a Discursive Network')
plt.legend()
plt.savefig('FOO_Figure4.png', dpi=300)
plt.show()


