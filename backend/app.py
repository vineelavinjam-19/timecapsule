from flask import Flask, request, jsonify
from flask_cors import CORS
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
from dotenv import load_dotenv
import joblib
import uuid
import hashlib
from datetime import timedelta
from datetime import datetime, timezone, timedelta

# -----------------------
# Load environment variables
# -----------------------
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")

if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
    raise Exception("❌ Missing EMAIL_USER or EMAIL_PASS")

# -----------------------
# Load ML model
# -----------------------
model = joblib.load("spam_model.pkl")

# -----------------------
# Blockchain Hash Function
# -----------------------
def generate_hash(data):
    return hashlib.sha256(
        data.encode()
    ).hexdigest()

# -----------------------
# Flask setup
# -----------------------
app = Flask(__name__)

CORS(
    app,
    resources={r"/*": {"origins": [
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]}},
    supports_credentials=True
)
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    

# -----------------------
# MongoDB setup
# -----------------------
client = MongoClient("mongodb://127.0.0.1:27017")
db = client.timecapsule
messages = db.messages

# -----------------------
# Spam Detection (HYBRID AI)
# -----------------------
def spam_check(message):

    proba = model.predict_proba([message])[0]
    spam_index = list(model.classes_).index("spam")
    ml_score = proba[spam_index]

    text = message.lower()

    keywords = [
        "free", "win", "winner", "money", "prize",
        "urgent", "click", "offer", "limited"
    ]

    rule_score = 0

    for word in keywords:
        if word in text:
            rule_score += 0.1

    if text.count("!") > 2:
        rule_score += 0.1

    if len(text) < 10:
        rule_score += 0.1

    final_score = (ml_score * 0.7) + rule_score

    print("ML:", ml_score, "RULE:", rule_score, "FINAL:", final_score)

    return final_score > 0.5, final_score

# -----------------------
# Email sending
# -----------------------
def send_email(to_email, subject, body, attachments=[]):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

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

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print("✅ SENT:", to_email)
        return True

    except Exception as e:
        print("❌ EMAIL ERROR:", e)
        return False

# -----------------------
# Scheduler
# -----------------------
def scheduler_loop():
    while True:
        now = datetime.now(timezone.utc)

        pending = messages.find({
            "sent": False,
            "send_at": {"$lte": now}
        })

        for msg in pending:
            unlock_link = (
                f"http://localhost:5500/unlock.html?"
                f"capsule_id={msg['capsule_id']}"
            )

            email_body = f"""
            Your Time Capsule is ready.

            Open it here:

            {unlock_link}

            You must sign in with the same Google account used to create it.
            """

            success = send_email(
                msg["email"],
                "Time Capsule Message",
                msg["message"],
                msg.get("attachments", [])
            )

            if success:
                messages.update_one(
                    {"_id": msg["_id"]},
                    {"$set": {"sent": True}}
                )

        time.sleep(10)

# -----------------------
# API ROUTE
# -----------------------

@app.route("/save", methods=["POST", "OPTIONS"])
def save_message():

    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        email = request.form.get("email")
        owner_email = request.form.get("owner_email")
        message = request.form.get("message")
        send_at = request.form.get("send_at")

        if not email or not owner_email or not message or not send_at:
            return jsonify({
                "error": "Missing fields"
            }), 400

        # -----------------------
        # SPAM CHECK
        # -----------------------
        is_spam, score = spam_check(message)

        if is_spam:
            return jsonify({
                "status": "rejected",
                "message": "Spam detected 🚫",
                "score": float(score)
            }), 400

        send_at_dt = datetime.fromisoformat(
            send_at
        ).astimezone(timezone.utc)

        # -----------------------
        # FILE UPLOADS
        # -----------------------
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)

        files = request.files.getlist("files")
        saved_files = []

        for file in files:
            if file.filename:
                path = os.path.join(
                    upload_folder,
                    file.filename
                )
                file.save(path)
                saved_files.append(path)

        last_capsule = messages.find_one(
            sort=[("_id", -1)]
        )
        if last_capsule:
            previous_hash = last_capsule.get(
                "capsule_hash"
            )
        else:
            previous_hash = "GENESIS_BLOCK"

        # -----------------------
        # CAPSULE ID
        # -----------------------
        capsule_id = str(uuid.uuid4())

        # -----------------------
        # BLOCKCHAIN HASH
        # -----------------------

        last_capsule = messages.find_one(
            sort=[("_id", -1)]
        )

        if last_capsule:
            previous_hash = last_capsule.get(
                "capsule_hash",
                "GENESIS_BLOCK"
            )
        else:
            previous_hash = "GENESIS_BLOCK"

        capsule_hash = generate_hash(
            owner_email +
            email +
            message +
            capsule_id +
            previous_hash
        )
        # -----------------------
        # SAVE TO DB
        # -----------------------
        messages.insert_one({
            "capsule_id": capsule_id,

            "capsule_hash": capsule_hash,
            "previous_hash": previous_hash,

            "owner_email": owner_email,
            "email": email,

            "message": message,
            "send_at": send_at_dt,

            "attachments": saved_files,

            "sent": False,

            # Access workflow
            "access_requested": False,
            "request_status": None,

            "request_reason": None,
            "request_note": None,

            "approved_by": None,
            "approved_at": None,

            "temporary_access": False,
            "access_expires": None,

            "audit_logs": []
        })

        return jsonify({
            "status": "saved",
            "capsule_id": capsule_id,
            "capsule_hash": capsule_hash,
            "spam_score": float(score)
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
# -----------------------
# VERIFY RECIPIENT
# -----------------------
@app.route("/verify-recipient", methods=["POST"])
def verify_recipient():

    try:

        data = request.json

        capsule_id = data.get(
            "capsule_id"
        )

        user_email = data.get(
            "user_email"
        )

        capsule = messages.find_one({
            "capsule_id": capsule_id
        })

        if not capsule:

            return jsonify({
                "valid": False,
                "message": "Capsule not found"
            }), 404

        return jsonify({
            "valid":
            capsule["email"] == user_email
        })

    except Exception as e:

        return jsonify({
            "valid": False,
            "error": str(e)
        }), 500
# -----------------------
# Request Access
# -----------------------   
@app.route("/request-access", methods=["POST"])
def request_access():

    data = request.json

    capsule_id = data.get("capsule_id")
    owner_email = data.get("owner_email")

    reason = data.get("reason")
    note = data.get("note")

    capsule = messages.find_one({
        "capsule_id": capsule_id
    })

    if not capsule:
        return jsonify({
            "success": False,
            "message": "Capsule not found"
        })

    messages.update_one(
        {
            "capsule_id": capsule_id
        },
        {
            "$set": {
                "access_requested": True,
                "request_status": "pending",
                "request_reason": reason,
                "request_note": note,
                "requested_by": owner_email,
                "requested_at": datetime.now(
                    timezone.utc
                )
            },

            "$push": {
                "audit_logs": {
                    "action":
                    "ACCESS_REQUESTED",

                    "by":
                    owner_email,

                    "at":
                    datetime.now(
                        timezone.utc
                    )
                }
            }
        }
    )

    return jsonify({
        "success": True
    })

# -----------------------
# Approve Access
# -----------------------  
@app.route("/approve-access", methods=["POST"])
def approve_access():

    data = request.json

    capsule_id = data["capsule_id"]

    recipient_email = data["recipient_email"]

    capsule = messages.find_one({
        "capsule_id": capsule_id
    })

    if not capsule:

        return jsonify({
            "success": False
        })

    if capsule["email"] != recipient_email:

        return jsonify({
            "success": False
        })

    expiry = datetime.now(
        timezone.utc
    ) + timedelta(hours=24)

    messages.update_one(
        {
            "capsule_id": capsule_id
        },
        {
            "$set": {
                "temporary_access": True,
                "access_expires": expiry,

                "request_status":
                "approved",

                "approved_by":
                recipient_email,

                "approved_at":
                datetime.now(timezone.utc)
            }
        }
    )

    return jsonify({
        "success": True
    })
# -----------------------
# verify-sender-access
# -----------------------   
    
@app.route("/verify-sender-access", methods=["POST"])
def verify_sender_access():

    data = request.json

    capsule_id = data["capsule_id"]

    owner_email = data["owner_email"]

    capsule = messages.find_one({
        "capsule_id": capsule_id
    })

    if not capsule:

        return jsonify({
            "valid": False
        })

    if capsule["owner_email"] != owner_email:

        return jsonify({
            "valid": False
        })

    if not capsule["temporary_access"]:

        return jsonify({
            "valid": False,
            "message":
            "Recipient approval required"
        })

    if datetime.now(timezone.utc) > capsule["access_expires"]:

        return jsonify({
            "valid": False,
            "message":
            "Access expired"
        })

    return jsonify({
        "valid": True
    })

    
 # -----------------------
# Unlock Capsule
# -----------------------
@app.route("/unlock/<capsule_id>", methods=["GET"])
def unlock_capsule(capsule_id):

    capsule = messages.find_one({
        "capsule_id": capsule_id
    })

    if not capsule:
        return jsonify({
            "status": "error",
            "message": "Capsule not found"
        }), 404

    # -----------------------
    # Blockchain verification
    # -----------------------
    previous_hash = capsule.get(
        "previous_hash",
        ""
    )

    current_hash = generate_hash(
        capsule["owner_email"] +
        capsule["email"] +
        capsule["message"] +
        capsule["capsule_id"] +
        previous_hash
    )

    if current_hash != capsule["capsule_hash"]:
        return jsonify({
            "status": "error",
            "message":
            "Capsule integrity compromised"
        }), 403

    # -----------------------
    # User verification
    # -----------------------
    user_email = request.args.get(
        "recipient_email"
    )

    if not user_email:
        return jsonify({
            "status": "error",
            "message":
            "Email missing"
        }), 400

    # -----------------------
    # Unlock date check
    # -----------------------
    send_at = capsule["send_at"]

    if send_at.tzinfo is None:
        send_at = send_at.replace(
            tzinfo=timezone.utc
        )

    now = datetime.now(
        timezone.utc
    )

    if send_at > now:

        return jsonify({
            "status": "locked",
            "unlock_time":
            send_at.isoformat()
        }), 403

    # -----------------------
    # Recipient can open
    # -----------------------
    if user_email == capsule["email"]:
        messages.update_one(
            {
                "capsule_id": capsule_id
            },
            {
                "$push": {
                    "audit_logs": {
                        "action":
                        "CAPSULE_OPENED",

                        "by":
                        user_email,

                        "at":
                        datetime.now(
                            timezone.utc
                        )
                    }
                }
            }
        )

        return jsonify({
            "status":
            "unlocked",

            "capsule_id":
            capsule["capsule_id"],

            "message":
            capsule["message"],

            "attachments":
            capsule.get(
                "attachments",
                []
            ),

            "recipient_access":
            True
        })

    # -----------------------
    # Temporary owner access
    # -----------------------
    if user_email == capsule["owner_email"]:

        if capsule.get(
            "temporary_access",
            False
        ):

            expiry = capsule.get(
                "access_expires"
            )

            # No expiry stored
            if expiry is None:

                return jsonify({
                    "status":
                    "unlocked",

                    "capsule_id":
                    capsule["capsule_id"],

                    "message":
                    capsule["message"],

                    "attachments":
                    capsule.get(
                        "attachments",
                        []
                    ),

                    "owner_access":
                    True
                })

            if expiry.tzinfo is None:
                expiry = expiry.replace(
                    tzinfo=timezone.utc
                )

            # Still valid
            if expiry > now:
                messages.update_one(
                    {
                        "capsule_id": capsule_id
                    },
                    {
                        "$push": {
                            "audit_logs": {
                                "action":
                                "CAPSULE_OPENED",

                                "by":
                                user_email,

                                "at":
                                datetime.now(
                                    timezone.utc
                                )
                            }
                        }
                    }
                )

                return jsonify({
                    "status":
                    "unlocked",

                    "capsule_id":
                    capsule["capsule_id"],

                    "message":
                    capsule["message"],

                    "attachments":
                    capsule.get(
                        "attachments",
                        []
                    ),

                    "owner_access":
                    True
                })

            # Expired
            messages.update_one(
                {
                    "capsule_id": capsule_id
                },
                {
                    "$push": {
                        "audit_logs": {
                            "action":
                            "CAPSULE_OPENED",
                            "by":
                            user_email,
                            "at":
                            datetime.now(
                                timezone.utc
                            )
                        }
                    }
                }
            )

            return jsonify({
                "status":
                "denied",
                "message":
                "Temporary access expired ⏰"
            }), 403

        return jsonify({
            "status":
            "denied",
            "message":
            "Recipient approval required"
        }), 403

    # -----------------------
    # Everyone else denied
    # -----------------------
    return jsonify({
        "status":
        "denied",
        "message":
        "Access denied ❌"
    }), 403
# -----------------------
# Pending Requests
# -----------------------
@app.route("/pending-requests/<recipient_email>")
def pending_requests(recipient_email):

    requests = list(
        messages.find({
            "email": recipient_email,
            "request_status": "pending"
        })
    )

    result = []

    for req in requests:

        requested_at = req.get("requested_at")

        result.append({
            "capsule_id": req["capsule_id"],
            "reason": req.get(
                "request_reason"
            ),
            "note": req.get(
                "request_note"
            ),
            "requested_by": req.get(
                "requested_by"
            ),
            "requested_at":
                requested_at.isoformat()
                if requested_at else None
        })

    return jsonify(result)
# -----------------------
# Approve Request
# -----------------------
@app.route("/approve-request", methods=["POST"])
def approve_request():

    try:

        data = request.json

        capsule_id = data.get(
            "capsule_id"
        )

        recipient_email = data.get(
            "recipient_email"
        )

        capsule = messages.find_one({
            "capsule_id": capsule_id
        })

        if not capsule:
            return jsonify({
                "success": False,
                "message": "Capsule not found"
            }), 404

        if capsule["email"] != recipient_email:
            return jsonify({
                "success": False,
                "message": "Unauthorized"
            }), 403

        messages.update_one(
            {
                "capsule_id": capsule_id
            },
            {
                "$set": {
                    "request_status": "approved",
                    "approved_by": recipient_email,
                    "approved_at":
                        datetime.now(
                            timezone.utc
                        ),
                    "temporary_access":
                        True,
                    "access_expires":
                        datetime.now(
                            timezone.utc
                        )
                        + timedelta(
                            minutes=10
                        )
                },

                "$push": {
                    "audit_logs": {
                        "action":
                        "ACCESS_APPROVED",

                        "by":
                        recipient_email,

                        "at":
                        datetime.now(
                            timezone.utc
                        )
                    }
                }
            }
        )

        return jsonify({
            "success": True
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# -----------------------
# Reject Request
# -----------------------
@app.route("/reject-request", methods=["POST"])
def reject_request():

    try:

        data = request.json

        capsule_id = data.get(
            "capsule_id"
        )

        recipient_email = data.get(
            "recipient_email"
        )

        capsule = messages.find_one({
            "capsule_id": capsule_id
        })

        if not capsule:
            return jsonify({
                "success": False
            }), 404

        if capsule["email"] != recipient_email:
            return jsonify({
                "success": False
            }), 403

        messages.update_one(
            {
                "capsule_id": capsule_id
            },
            {
                "$set": {
                    "request_status":
                    "rejected"
                }
            }
        )

        return jsonify({
            "success": True
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    

# -----------------------
# Validate Blockchain
# -----------------------
@app.route("/validate-chain", methods=["GET"])
def validate_chain():

    capsules = list(
        messages.find().sort("_id", 1)
    )

    if len(capsules) <= 1:
        return jsonify({
            "valid": True,
            "message": "Blockchain verified"
        })

    for i in range(1, len(capsules)):

        current = capsules[i]
        previous = capsules[i - 1]

        if "previous_hash" not in current:
            continue

        if "capsule_hash" not in previous:
            continue

        # Check chain link
        if current["previous_hash"] != previous["capsule_hash"]:

            return jsonify({
                "valid": False,
                "message": "Blockchain chain broken",
                "broken_capsule":
                current["capsule_id"]
            })

        # Check data integrity
        expected_hash = generate_hash(
            current["owner_email"] +
            current["email"] +
            current["message"] +
            current["capsule_id"] +
            current["previous_hash"]
        )

        if expected_hash != current["capsule_hash"]:

            return jsonify({
                "valid": False,
                "message": "Capsule tampered",
                "broken_capsule":
                current["capsule_id"]
            })

    return jsonify({
        "valid": True,
        "message":
        "Blockchain chain verified"
    })
# -----------------------
# dashboard
# -----------------------
@app.route("/dashboard/<email>")
def dashboard(email):

    total = messages.count_documents({
        "$or": [
            {"owner_email": email},
            {"email": email}
        ]
    })

    sent = messages.count_documents({
        "$or": [
            {"owner_email": email},
            {"email": email}
        ],
        "sent": True
    })

    locked = messages.count_documents({
        "$or": [
            {"owner_email": email},
            {"email": email}
        ],
        "sent": False
    })

    pending = messages.count_documents({
        "email": email,
        "request_status": "pending"
    })

    return jsonify({
        "total": total,
        "sent": sent,
        "locked": locked,
        "pending": pending
    })
# -----------------------
# List Capsules (for dashboard table)
# -----------------------
@app.route("/capsules/<email>")
def list_capsules(email):

    docs = list(
        messages.find({
            "$or": [
                {"owner_email": email},
                {"email": email}
            ]
        }).sort("_id", -1).limit(20)
    )

    result = []

    for doc in docs:

        send_at = doc.get("send_at")

        if send_at and send_at.tzinfo is None:
            send_at = send_at.replace(tzinfo=timezone.utc)

        if doc.get("request_status") == "approved":
            status = "ACCESS_APPROVED"
        elif doc.get("sent"):
            status = "DELIVERED"
        else:
            status = "LOCKED"

        result.append({
            "capsule_id": doc.get("capsule_id"),
            "recipient": doc.get("email"),
            "unlock_time": send_at.isoformat() if send_at else None,
            "status": status
        })

    return jsonify(result)

# -----------------------
# Audit Logs
# -----------------------
@app.route("/audit/<capsule_id>")
def get_audit_logs(capsule_id):

    capsule = messages.find_one(
        {
            "capsule_id": capsule_id
        }
    )

    if not capsule:
        return jsonify([])

    logs = capsule.get(
        "audit_logs",
        []
    )

    return jsonify(logs)
# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    return "Time Capsule Running 🚀"

# -----------------------
# START SERVER
# -----------------------
if __name__ == "__main__":
    threading.Thread(target=scheduler_loop, daemon=True).start()
    app.run(host="127.0.0.1", port=5000, debug=False)