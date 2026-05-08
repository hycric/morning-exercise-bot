import os
import requests

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

def get_latest_video():
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "channelId": "UC6YO6az9CLMqJy3_3X2g0Vg",
        "part": "snippet",
        "order": "date",
        "maxResults": 1,
        "type": "video"
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    items = data.get("items", [])
    if not items:
        return None
    item = items[0]
    title = item["snippet"]["title"]
    video_id = item["id"]["videoId"]
    return f"🧘 早安！今天的早操影片：\n{title}\nhttps://www.youtube.com/watch?v={video_id}"

def push_message(user_id, text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    resp = requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=body)
    print(f"Status: {resp.status_code}, Response: {resp.text}")

if __name__ == "__main__":
    message = get_latest_video()
    if message and USER_ID:
        push_message(USER_ID, message)
        print("訊息已傳送！")
    else:
        print("找不到影片或 USER_ID 未設定")
