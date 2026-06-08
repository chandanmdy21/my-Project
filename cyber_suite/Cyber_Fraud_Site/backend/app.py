from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import datetime
import requests

from pyzbar.pyzbar import decode
import cv2

# ---------------- QR SCANNER FUNCTION ----------------

def scan_qr_code(image_path):
    img = cv2.imread(image_path)
    decoded_objects = decode(img)

    for obj in decoded_objects:
        return obj.data.decode("utf-8")

    return None

from flask_socketio import SocketIO, emit


from utils.feature_extractor import extract_url_features

# ✅ AI Models
from models.model import (
    predict_sms,
    predict_phishing,
    predict_upi,
    predict_call
)

# ---------------- APP CONFIG ----------------

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

app.secret_key = "cyber_fraud_secret_key"

socketio = SocketIO(app)


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password_hash TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        input_data TEXT,
        result TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ---------------- SAVE LOG ----------------

def save_log(type_name, input_data, result):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO logs(type,input_data,result,timestamp) VALUES(?,?,?,?)",
        (type_name, input_data, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    conn.commit()
    conn.close()

    # 🔥 SEND REAL-TIME UPDATE
    socketio.emit("new_log", {
        "type": type_name,
        "input": input_data,
        "result": result
    })
# ---------------- ROOT ----------------

@app.route("/")
def root():
    return redirect(url_for("login"))

# ---------------- REGISTER ----------------

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    confirm = request.form["confirm_password"]

    if password != confirm:
        return render_template("login.html", error="Passwords do not match", form_type="register")

    hashed = generate_password_hash(password)

    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password_hash) VALUES(?,?)",
            (username, hashed)
        )

        conn.commit()
        conn.close()

        return render_template("login.html", success_msg="Registration Successful", form_type="login")

    except sqlite3.IntegrityError:
        return render_template("login.html", error="Username exists", form_type="register")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["logged_in"] = True
            session["user_id"] = user["id"]
            # --- ADD THIS LINE BELOW ---
            session["username"] = username 
            # ---------------------------
            return redirect(url_for("home"))

        return render_template("login.html", error="Invalid login")

    return render_template("login.html")
# ---------------- HOME ----------------

@app.route("/home")
def home():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route('/profile')
def profile():
    # Debugging: Print to your terminal to see if the session exists
    print(f"Current Session: {session}") 
    
    if 'username' not in session:
        # If it's redirecting here, your login didn't save the session correctly
        return redirect('/login') 
        
    return render_template('profile.html')

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT type, COUNT(*) FROM logs GROUP BY type")
    data = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM logs")
    total = cursor.fetchone()[0]

    conn.close()

    labels = [row[0] for row in data]
    values = [row[1] for row in data]

    return render_template("dashboard.html", labels=labels, values=values, total=total)

# ---------------- SMS ----------------

@app.route("/sms")
def sms():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    return render_template("sms.html")

@app.route("/check_sms", methods=["POST"])
def check_sms():
    data = request.get_json()
    message = data.get("message", "").lower()

    spam_words = ["win", "free", "offer", "click", "urgent", "prize", "congratulations", "claim", "winner"]

    if any(word in message for word in spam_words):
        result = "⚠️ Spam SMS"
    else:
        result = "✅ Legit SMS"

    save_log("SMS", message, result)
    return jsonify({"result": result})

# ---------------- PHISHING ----------------

@app.route("/phishing")
def phishing():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    return render_template("phishing.html")

@app.route("/check_phishing", methods=["POST"])
def check_phishing():
    data = request.get_json()
    url = data.get("url", "").lower()

    if not url:
        return jsonify({"result": "❌ URL required"}), 400

    # 🔥 RULE-BASED DETECTION (STRONG)
    suspicious_words = ["login", "verify", "update", "bank", "free", "urgent", "account"]

    if any(word in url for word in suspicious_words) or len(url) > 40:
        result = "⚠️ Phishing Website "
    else:
        result = "✅ Safe Website"

    save_log("Phishing", url, result)
    return jsonify({"result": result})

# ---------------- DARK WEB ----------------

@app.route("/darkweb")
def darkweb():
    if not session.get("logged_in"):
        return redirect(url_for("index"))
    return render_template("darkweb.html")


def check_email_breach(email):
    breached = [
        "test@gmail.com",
        "admin@yahoo.com",
        "user123@hotmail.com",
        "victim@outlook.com"
    ]
    return email.lower() in breached


@app.route("/check_darkweb", methods=["POST"])
def check_darkweb():
    data = request.get_json()
    email = data.get("email", "").strip().lower()

    if check_email_breach(email):
        result = "⚠️ Breached Email Found"
    else:
        result = "✅ Safe Email"

    save_log("DarkWeb", email, result)
    return jsonify({"result": result})

# ---------------- UPI ----------------

@app.route("/upi")
def upi():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    return render_template("upi.html")

@app.route("/check_upi", methods=["POST"])
def check_upi():
    try:
        # ---------------- INPUT ----------------
        amount = float(request.form.get("amount", 0))
        location = int(request.form.get("location_change", 0))
        device = int(request.form.get("device_change", 0))
        upi_id = request.form.get("upi_id", "")

        # ---------------- QR SCAN ----------------
        if "qr_image" in request.files:
            file = request.files["qr_image"]
            file_path = "temp_qr.png"
            file.save(file_path)

            qr_data = scan_qr_code(file_path)

            if qr_data:
                upi_id = qr_data  # Extracted from QR

    except:
        return jsonify({"result": "❌ Invalid input"}), 400

    # ---------------- BLACKLIST ----------------
    fraud_upi_ids = [
        "fraud@upi",
        "scam@paytm",
        "hack@okaxis",
        "fake@oksbi"
    ]

    # ---------------- ML PREDICTION ----------------
    prediction, prob = predict_upi(amount, location, device)

    # ---------------- RULE LOGIC ----------------
    if upi_id in fraud_upi_ids:
        result = "🚨 FRAUD UPI ID DETECTED"

    elif amount > 50000:
        result = "🚨 HIGH AMOUNT TRANSACTION"

    elif location == 1 or device == 1:
        result = "⚠️ SUSPICIOUS DEVICE / LOCATION"

    elif prob > 0.7:
        result = "🚨 HIGH RISK"

    elif prob > 0.4:
        result = "⚠️ MEDIUM RISK"

    else:
        result = "✅ LOW RISK"

    result += f" ({round(prob*100)}%)"

    save_log("UPI", f"{upi_id} | ₹{amount}", result)

    return jsonify({
        "result": result,
        "upi_id": upi_id
    })

# ---------------- CALL ----------------

@app.route("/call")
def call():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    return render_template("call.html")

@app.route("/check_call", methods=["POST"])
def check_call():
    data = request.get_json()

    try:
        duration = float(data.get("duration", 0))
        unknown = int(data.get("unknown_number", 0))
        phone = data.get("phone", "")
    except:
        return jsonify({"result": "Invalid input"}), 400

    # 🚨 Known fraud numbers (for testing)
    fraud_numbers = [
        "9999999999",
        "8888888888",
        "+911234567890",
        "0000000000"
    ]

    # ML prediction
    prediction, prob = predict_call(duration, unknown)

    # ---------------- RULE-BASED LOGIC ----------------
    if phone in fraud_numbers:
        result = "🚨 BLACKLISTED FRAUD NUMBER"

    elif unknown == 1 and duration < 20:
        result = "⚠️ Suspicious Short Call"

    elif prob > 0.7:
        result = "🚨 HIGH RISK CALL"

    elif prob > 0.4:
        result = "⚠️ MEDIUM RISK CALL"

    else:
        result = "✅ SAFE CALL"

    result += f" ({round(prob*100)}%)"

    save_log("Call", f"{phone} | {duration}", result)
    return jsonify({"result": result})
# ---------------- ADMIN ----------------

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect(url_for("index.html"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()

    conn.close()

    return render_template("admin.html", logs=logs)

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------- RUN ----------------

if __name__ == "__main__":
    socketio.run(app, debug=True)