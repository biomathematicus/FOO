import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import poisson, binom

# Parameters
num_actors_1 = 1000  # Number of actors in network N1
num_actors_2 = 1000  # Number of actors in network N2
num_iterations = 200  # Number of time steps in each epoch
epochs = 20  # Number of epochs

# Probability parameters
p12 = 0.05  # Probability that a true statement becomes false in N1
q12 = 0.10  # Probability that a false statement becomes true in N1
p21 = 0.03  # Probability that a true statement becomes false in N2
q21 = 0.07  # Probability that a false statement becomes true in N2
lambda1 = 5  # Rate of falsehood generation in N1
lambda2 = 6  # Rate of falsehood generation in N2
d12 = 0.1  # Detection probability of falsehoods in N1 by N2
d21 = 0.1  # Detection probability of falsehoods in N2 by N1

# Simulation function
def simulate_epoch(num_actors_1, num_actors_2, p12, q12, p21, q21, lambda1, lambda2, d12, d21, num_iterations):
    T1, F1 = np.random.randint(1, 100, size=2)  # Initial true and false statements in N1
    T2, F2 = np.random.randint(1, 100, size=2)  # Initial true and false statements in N2
    T1_over_time, F1_over_time = [T1], [F1]
    T2_over_time, F2_over_time = [T2], [F2]
    
    for t in range(num_iterations):
        X1 = poisson.rvs(lambda1)  # New falsehoods in N1
        X2 = poisson.rvs(lambda2)  # New falsehoods in N2
        Y12 = binom.rvs(F1, d12)  # Falsehoods in N1 detected by N2
        Y21 = binom.rvs(F2, d21)  # Falsehoods in N2 detected by N1
        Z1 = binom.rvs(T1, p12)  # True statements in N1 becoming false
        Z2 = binom.rvs(T2, p21)  # True statements in N2 becoming false
        W1 = binom.rvs(F1, q12)  # False statements in N1 becoming true
        W2 = binom.rvs(F2, q21)  # False statements in N2 becoming true

        T1 = T1 - Z1 + W1
        F1 = F1 + X1 + Z1 - W1 - Y12
        T2 = T2 - Z2 + W2
        F2 = F2 + X2 + Z2 - W2 - Y21
        
        T1_over_time.append(T1)
        F1_over_time.append(F1)
        T2_over_time.append(T2)
        F2_over_time.append(F2)
    
    return T1_over_time, F1_over_time, T2_over_time, F2_over_time

# Run simulation for multiple epochs
all_T1, all_F1, all_T2, all_F2 = [], [], [], []

for epoch in range(epochs):
    T1_over_time, F1_over_time, T2_over_time, F2_over_time = simulate_epoch(
        num_actors_1, num_actors_2, p12, q12, p21, q21, lambda1, lambda2, d12, d21, num_iterations)
    all_T1.append(T1_over_time)
    all_F1.append(F1_over_time)
    all_T2.append(T2_over_time)
    all_F2.append(F2_over_time)

# Convert to numpy arrays
all_T1 = np.array(all_T1)
all_F1 = np.array(all_F1)
all_T2 = np.array(all_T2)
all_F2 = np.array(all_F2)

# Ensure consistent lengths
mean_T1 = np.mean(all_T1, axis=0)
mean_F1 = np.mean(all_F1, axis=0)
mean_T2 = np.mean(all_T2, axis=0)
mean_F2 = np.mean(all_F2, axis=0)

std_T1 = np.std(all_T1, axis=0)
std_F1 = np.std(all_F1, axis=0)
std_T2 = np.std(all_T2, axis=0)
std_F2 = np.std(all_F2, axis=0)

ci_T1_upper = mean_T1 + 1.96 * std_T1 / np.sqrt(epochs)
ci_T1_lower = mean_T1 - 1.96 * std_T1 / np.sqrt(epochs)
ci_F1_upper = mean_F1 + 1.96 * std_F1 / np.sqrt(epochs)
ci_F1_lower = mean_F1 - 1.96 * std_F1 / np.sqrt(epochs)
ci_T2_upper = mean_T2 + 1.96 * std_T2 / np.sqrt(epochs)
ci_T2_lower = mean_T2 - 1.96 * std_T2 / np.sqrt(epochs)
ci_F2_upper = mean_F2 + 1.96 * std_F2 / np.sqrt(epochs)
ci_F2_lower = mean_F2 - 1.96 * std_F2 / np.sqrt(epochs)

# Plotting the results
plt.figure(figsize=(14, 8))

plt.subplot(2, 1, 1)
plt.plot(mean_T1, label='Mean T1')
plt.plot(mean_F1, label='Mean F1')
plt.fill_between(range(num_iterations+1), ci_T1_lower, ci_T1_upper, color='blue', alpha=0.1)
plt.fill_between(range(num_iterations+1), ci_F1_lower, ci_F1_upper, color='red', alpha=0.1)
plt.xlabel('Time steps')
plt.ylabel('Number of Statements')
plt.title('Network N1: True and False Statements Over Time')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(mean_T2, label='Mean T2')
plt.plot(mean_F2, label='Mean F2')
plt.fill_between(range(num_iterations+1), ci_T2_lower, ci_T2_upper, color='blue', alpha=0.1)
plt.fill_between(range(num_iterations+1), ci_F2_lower, ci_F2_upper, color='red', alpha=0.1)
plt.xlabel('Time steps')
plt.ylabel('Number of Statements')
plt.title(f'Network N2: True and False Statements Over Time ({epochs} Epochs)')
plt.legend()

plt.tight_layout()
plt.savefig('FOO_Figure2.png', dpi=300)
plt.show()
