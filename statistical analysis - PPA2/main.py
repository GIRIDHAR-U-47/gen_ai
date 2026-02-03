import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load dataset
data = pd.read_csv("StudentsPerformance.csv")

# Select numerical columns
math = data['math score']
reading = data['reading score']
writing = data['writing score']

# Mean
print("Mean:")
print("Math:", np.mean(math))
print("Reading:", np.mean(reading))
print("Writing:", np.mean(writing))

# Variance
print("\nVariance:")
print("Math:", np.var(math))
print("Reading:", np.var(reading))
print("Writing:", np.var(writing))

# Standard Deviation
print("\nStandard Deviation:")
print("Math:", np.std(math))
print("Reading:", np.std(reading))
print("Writing:", np.std(writing))

# Correlation
print("\nCorrelation Matrix:")
print(data[['math score','reading score','writing score']].corr())

# Normal Distribution
normal_dist = np.random.normal(np.mean(math), np.std(math), 1000)

# Uniform Distribution
uniform_dist = np.random.uniform(min(math), max(math), 1000)

# Plot distributions
plt.figure(figsize=(10,4))

plt.subplot(1,2,1)
plt.hist(normal_dist, bins=30)
plt.title("Normal Distribution")

plt.subplot(1,2,2)
plt.hist(uniform_dist, bins=30)
plt.title("Uniform Distribution")

plt.show()
