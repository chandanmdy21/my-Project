import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "call_fraud.csv")

# Load dataset
df = pd.read_csv(file_path)

# Features & label
X = df[["duration", "unknown_number"]]
y = df["fraud"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, os.path.join(BASE_DIR, "call_model.pkl"))

print("✅ Call Fraud Model Trained Successfully")