import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------- PHISHING MODEL ----------------
phishing_data = pd.DataFrame({
    "url_length": np.random.randint(10,100,500),
    "has_https": np.random.randint(0,2,500),
    "has_at_symbol": np.random.randint(0,2,500),
    "is_phishing": np.random.randint(0,2,500)
})
X = phishing_data.drop("is_phishing", axis=1)
y = phishing_data["is_phishing"]
X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.2)
phishing_model = RandomForestClassifier()
phishing_model.fit(X_train,y_train)
joblib.dump(phishing_model, os.path.join(BASE_DIR,"backend/models/phishing_model.pkl"))

# Accuracy & Graph
y_pred = phishing_model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)
plt.imshow(cm)
plt.title("Phishing Confusion Matrix")
plt.colorbar()
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.savefig(os.path.join(BASE_DIR,"frontend/static/graph.png"))
plt.close()
print("Phishing Model Accuracy:", accuracy)

# ---------------- UPI FRAUD MODEL ----------------
upi_data = pd.DataFrame({
    "amount": np.random.randint(1,100000,500),
    "location_change": np.random.randint(0,2,500),
    "device_change": np.random.randint(0,2,500),
    "fraud": np.random.randint(0,2,500)
})
X2 = upi_data.drop("fraud", axis=1)
y2 = upi_data["fraud"]
X2_train, X2_test, y2_train, y2_test = train_test_split(X2,y2,test_size=0.2)
upi_model = RandomForestClassifier()
upi_model.fit(X2_train,y2_train)
joblib.dump(upi_model, os.path.join(BASE_DIR,"backend/models/upi_model.pkl"))
print("UPI Model Trained")

# ---------------- SMS SPAM MODEL ----------------
sms_data = pd.DataFrame({
    "length": np.random.randint(10,200,500),
    "has_free": np.random.randint(0,2,500),
    "has_win": np.random.randint(0,2,500),
    "spam": np.random.randint(0,2,500)
})

X_sms = sms_data.drop("spam", axis=1)
y_sms = sms_data["spam"]

sms_model = RandomForestClassifier()
sms_model.fit(X_sms,y_sms)
joblib.dump(sms_model,"backend/models/sms_model.pkl")


# ---------------- FRAUD CALL MODEL ----------------
call_data = pd.DataFrame({
    "duration": np.random.randint(1,600,500),
    "unknown_number": np.random.randint(0,2,500),
    "international": np.random.randint(0,2,500),
    "fraud": np.random.randint(0,2,500)
})

X_call = call_data.drop("fraud", axis=1)
y_call = call_data["fraud"]

call_model = RandomForestClassifier()
call_model.fit(X_call,y_call)
joblib.dump(call_model,"backend/models/call_model.pkl")