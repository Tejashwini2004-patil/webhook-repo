from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
db = client["webhook_db"]
collection = db["actions"]

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json
        print("✅ Webhook received:", data)  # For debugging

        # Safely extract fields
        action_type = data.get("action", "unknown")
        sender = data.get("sender", {}).get("login", "unknown")
        from_branch = data.get("pull_request", {}).get("head", {}).get("ref", "")
        to_branch = data.get("pull_request", {}).get("base", {}).get("ref", data.get("ref", ""))

        payload = {
            "request_id": str(uuid.uuid4()),
            "author": sender,
            "action": action_type.upper(),
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": datetime.utcnow().strftime("%d-%m-%Y %I:%M %p")
        }

        collection.insert_one(payload)
        return jsonify({"status": "received"}), 200

    except Exception as e:
        print("❌ Error handling webhook:", str(e))
        return jsonify({"error": "Invalid payload"}), 200  # Always return 200 to avoid webhook failure

if __name__ == "__main__":
    app.run(port=5000)
