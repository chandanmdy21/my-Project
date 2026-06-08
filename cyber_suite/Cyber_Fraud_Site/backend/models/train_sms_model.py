import pandas as pd
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

# Get correct path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "spam.csv")

# Load dataset
df = pd.read_csv(file_path, encoding="latin-1")
df = df.rename(columns={"v1": "label", "v2": "message"})

X = df["message"]
y = df["label"]

# Split data (IMPORTANT)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Convert text → numbers
vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Test accuracy
y_pred = model.predict(X_test_vec)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save model
joblib.dump(model, os.path.join(BASE_DIR, "sms_model.pkl"))
joblib.dump(vectorizer, os.path.join(BASE_DIR, "sms_vectorizer.pkl"))

print("✅ SMS AI Model Trained Successfully")