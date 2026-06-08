import joblib
import os

BASE_DIR = os.path.dirname(__file__)

# ---------------- LOAD MODELS ----------------

sms_model = joblib.load(os.path.join(BASE_DIR, "sms_model.pkl"))
sms_vectorizer = joblib.load(os.path.join(BASE_DIR, "sms_vectorizer.pkl"))

phishing_model = joblib.load(os.path.join(BASE_DIR, "phishing_model.pkl"))
call_model = joblib.load(os.path.join(BASE_DIR, "call_model.pkl"))
upi_model = joblib.load(os.path.join(BASE_DIR, "upi_model.pkl"))

# ---------------- DARKWEB MODEL ----------------
darkweb_model = joblib.load(os.path.join(BASE_DIR, "darkweb_model.pkl"))
darkweb_vectorizer = joblib.load(os.path.join(BASE_DIR, "darkweb_vectorizer.pkl"))

print("✅ All Models Loaded Successfully")

# ---------------- FEATURE FUNCTIONS ----------------

def extract_url_features(url):
    return [
        len(url),
        1 if "https" in url else 0,
        url.count("."),
        url.count("-"),
        url.count("@"),
        1 if "login" in url.lower() else 0,
        1 if "verify" in url.lower() else 0
    ]

# ---------------- PREDICTION FUNCTIONS ----------------

# ---------------- SMS ----------------
def predict_sms(message):
    vec = sms_vectorizer.transform([message])
    prediction = sms_model.predict(vec)[0]
    prob = sms_model.predict_proba(vec)[0].max()
    return prediction, prob


# ---------------- PHISHING ----------------
def predict_phishing(features):
    pred = phishing_model.predict([features])[0]
    prob = phishing_model.predict_proba([features])[0][1]
    return pred, prob


# ---------------- UPI ----------------
def predict_upi(amount, location_change, device_change):
    features = [[amount, location_change, device_change]]
    prediction = upi_model.predict(features)[0]
    prob = upi_model.predict_proba(features)[0][1]
    return prediction, prob


# ---------------- CALL ----------------
def predict_call(duration, unknown_number):
    features = [[duration, unknown_number]]
    prediction = call_model.predict(features)[0]
    prob = call_model.predict_proba(features)[0][1]
    return prediction, prob


# ---------------- DARKWEB ----------------
def predict_darkweb(text):
    vec = darkweb_vectorizer.transform([text])
    prediction = darkweb_model.predict(vec)[0]
    prob = darkweb_model.predict_proba(vec)[0].max()
    return prediction, prob