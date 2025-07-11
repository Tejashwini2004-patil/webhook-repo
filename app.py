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
    data = request.json
    action_type = data.get("action")
    payload = {
        "request_id": str(uuid.uuid4()),
        "author": data["sender"]["login"],
        "action": action_type.upper(),
        "from_branch": data.get("pull_request", {}).get("head", {}).get("ref", ""),
        "to_branch": data.get("pull_request", {}).get("base", {}).get("ref", data.get("ref", "")),
        "timestamp": datetime.utcnow().strftime("%d-%m-%Y %I:%M %p")
    }
    collection.insert_one(payload)
    return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(port=5000)
