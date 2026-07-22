import os
import requests
from datetime import datetime
import pytz

CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# 苗栗經緯度
LAT = 24.5602
LON = 120.8214

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

def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": LAT,
            "longitude": LON,
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_probability_max",
            "timezone": "Asia/Taipei",
            "forecast_days": 1
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        daily = data["daily"]
        
        temp_max = daily["temperature_2m_max"][0]
        temp_min = daily["temperature_2m_min"][0]
        precip = daily["precipitation_probability_max"][0]
        code = daily["weathercode"][0]

        # 天氣代碼轉中文
        if code == 0:
            desc = "晴天☀️"
        elif code in [1, 2, 3]:
            desc = "多雲🌤"
        elif code in [45, 48]:
            desc = "有霧🌫"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
            desc = "有雨🌧"
        elif code in [71, 73, 75]:
            desc = "有雪❄️"
        elif code in [95, 96, 99]:
            desc = "雷雨⛈"
        else:
            desc = "天氣不定"

        rain_msg = f"☔ 降雨機率 {precip}%，記得帶傘！地板濕滑請小心！\n" if precip >= 50 else ""
        
        return f"🌡 今天苗栗天氣：{desc}\n🌡 氣溫：{temp_min}°C - {temp_max}°C\n{rain_msg}"
    except Exception as e:
        return ""

def get_greeting():
    tz = pytz.timezone("Asia/Taipei")
    now = datetime.now(tz)
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    weekday = weekdays[now.weekday()]
    date_str = now.strftime(f"%m月%d日 （週{weekday}）")
    return f"📅 {date_str}\n\n💌 早安！記得多喝水，運動後要休息喔！"

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
    video = get_latest_video()
    weather = get_weather()
    greeting = get_greeting()
    
    if video and USER_ID:
        message = f"{greeting}\n\n{weather}\n{video}"
        push_message(USER_ID, message)
        print("訊息已傳送！")
    else:
        print("找不到影片或 USER_ID 未設定")
