import os
import json
from flask import Flask, request, abort
import requests
import hashlib
import hmac
import base64

app = Flask(__name__)

CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")

def verify_signature(body, signature):
    hash = hmac.new(
        CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode("utf-8") == signature

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data()

    if not verify_signature(body, signature):
        abort(400)

    data = request.get_json()
    for event in data.get("events", []):
        if event.get("type") == "follow":
            user_id = event.get("source", {}).get("userId", "")
            print(f"新好友 User ID: {user_id}")

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
