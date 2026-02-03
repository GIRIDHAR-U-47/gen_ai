import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Load dataset
data = pd.read_csv("StudentsPerformance.csv")

# Select features (independent variables) and target (dependent variable)
X = data[['reading score', 'writing score']]
y = data['math score']

# Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Create Linear Regression model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Predict values
y_pred = model.predict(X_test)

# Evaluation
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("Mean Squared Error:", mse)
print("R2 Score:", r2)

# Display coefficients
print("\nModel Coefficients:")
print("Reading Score Weight:", model.coef_[0])
print("Writing Score Weight:", model.coef_[1])
print("Intercept:", model.intercept_)
