import os
import xml.etree.ElementTree as ET
from flask import Flask, request, abort
import requests
import hashlib
import hmac
import base64

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET")
RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UC6YO6az9CLMqJy3_3X2g0Vg"

def verify_signature(body, signature):
    hash = hmac.new(
        CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    return base64.b64encode(hash).decode("utf-8") == signature

def get_latest_videos(n=2):
    try:
        YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "key": YOUTUBE_API_KEY,
            "channelId": "UC6YO6az9CLMqJy3_3X2g0Vg",
            "part": "snippet",
            "order": "date",
            "maxResults": n,
            "type": "video"
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        videos = []
        for item in data.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            videos.append(f"🧘 {title}\n{link}")
        return videos if videos else ["今天暫時取不到影片，請稍後再試"]
    except Exception as e:
        return [f"取得影片失敗：{str(e)}"]

def reply_message(reply_token, messages):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": m} for m in messages]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data()

    if not verify_signature(body, signature):
        abort(400)

    data = request.get_json()
    for event in data.get("events", []):
        if event.get("type") == "message" and event.get("source", {}).get("type") == "group":
            text = event.get("message", {}).get("text", "")
            if "阿婆早操影片" in text:
                reply_token = event.get("replyToken")
                videos = get_latest_videos(1)
                reply_message(reply_token, videos)

    return "OK"

@app.route("/debug", methods=["GET"])
def debug():
    headers = {"Accept-Encoding": "identity"}
    resp = requests.get(RSS_URL, timeout=10, headers=headers)
    return resp.text[:500]

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
