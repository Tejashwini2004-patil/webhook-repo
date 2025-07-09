from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import uuid

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["github_events"]
collection = db["events"]

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    action_type = None
    author = None
    from_branch = None
    to_branch = None

    # Identify action type
    if "pusher" in data:
        action_type = "PUSH"
        author = data["pusher"]["name"]
        to_branch = data["ref"].split("/")[-1]
    elif "pull_request" in data:
        action_type = "PULL_REQUEST"
        pr = data["pull_request"]
        author = pr["user"]["login"]
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]
    else:
        return jsonify({"message": "Not handled"}), 200

    event = {
        "_id": str(uuid.uuid4()),
        "request_id": data.get("pull_request", {}).get("id", None),
        "author": author,
        "action": action_type,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": datetime.utcnow().isoformat()
    }

    collection.insert_one(event)
    return jsonify({"message": "Event received"}), 200

@app.route('/events', methods=['GET'])
def get_events():
    events = list(collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(10))
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
