# app.py

from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import threading
import time
import os
from flask_cors import CORS

# -------------------------
# Flask App
# -------------------------
app = Flask(__name__)
CORS(app)

# -------------------------
# Email credentials
# -------------------------
EMAIL_ADDRESS = "vinnivinjam@gmail.com"
EMAIL_PASSWORD = "kbndunbsrluxgsyz"   # 16-character Gmail App Password

# -------------------------
# MongoDB setup
# -------------------------
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.timecapsule
messages = db.messages

# -------------------------
# Email sending function
# -------------------------
def send_email(to_email, subject, body, attachments=[]):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach files
        for file_path in attachments:
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{os.path.basename(file_path)}"'
                )
                msg.attach(part)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("[SENT ✅]", to_email)
        return True

    except Exception as e:
        print("[ERROR ❌]", e)
        return False

# -------------------------
# Scheduler (checks every 10 seconds for testing)
# -------------------------
def scheduler():
    while True:
        now = datetime.now(timezone.utc)

        unsent_messages = messages.find({
            "sent": False,
            "send_at": {"$lte": now}
        })

        for msg in unsent_messages:
            attachments = msg.get("attachments", [])
            success = send_email(
                msg["email"],
                "🕰 Time Capsule Message",
                msg["message"],
                attachments
            )
            if success:
                messages.update_one(
                    {"_id": msg["_id"]},
                    {"$set": {"sent": True}}
                )
            else:
                messages.update_one(
                    {"_id": msg["_id"]},
                    {"$set": {"sent": "failed"}}
                )

        time.sleep(10)  # check every 10s for testing (can increase later)

# -------------------------
# Routes
# -------------------------
@app.route("/save", methods=["POST"])
def save_message():
    try:
        if not request.is_json:
            return jsonify({"status": "error", "message": "Request must be JSON"}), 400

        data = request.get_json()
        # Convert send_at to UTC datetime
        data["send_at"] = datetime.fromisoformat(data["send_at"]).astimezone(timezone.utc)
        data["sent"] = False
        if "attachments" not in data:
            data["attachments"] = []

        messages.insert_one(data)
        return jsonify({"status": "saved"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route("/status", methods=["GET"])
def check_status():
    all_msgs = list(messages.find({}, {"_id": 0}))
    return jsonify(all_msgs)

@app.route("/")
def home():
    return "✅ Time Capsule Backend Running"

# -------------------------
# Start app + scheduler
# -------------------------
if __name__ == "__main__":
    # Start scheduler in background
    threading.Thread(target=scheduler, daemon=True).start()
    # Run Flask app
    app.run(debug=False)  # set debug=False to avoid scheduler thread restart issues
