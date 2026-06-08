import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

BASE_DIR = os.path.dirname(__file__)
csv_path = os.path.join(BASE_DIR, "darkweb.csv")

df = pd.read_csv(csv_path)

X = df["text"]
y = df["label"]

vectorizer = TfidfVectorizer()
X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

model = LogisticRegression()
model.fit(X_train, y_train)

joblib.dump(model, "darkweb_model.pkl")
joblib.dump(vectorizer, "darkweb_vectorizer.pkl")

print("Darkweb model trained successfully")