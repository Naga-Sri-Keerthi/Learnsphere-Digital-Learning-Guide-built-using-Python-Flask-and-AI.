import os
import requests

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

def search_videos(topic):
    if not YOUTUBE_API_KEY:
        return [
            {"title": f"Introduction to {topic}", "channel": "YouTube learning search",
             "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+tutorial"},
            {"title": f"{topic} for Beginners", "channel": "YouTube learning search",
             "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+for+beginners"},
            {"title": f"{topic} Explained", "channel": "YouTube learning search",
             "url": f"https://www.youtube.com/results?search_query={topic.replace(' ', '+')}+explained"}
        ]
    try:
        r = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={"part":"snippet", "q":topic, "type":"video", "maxResults":3,
                    "key":YOUTUBE_API_KEY},
            timeout=20
        )
        r.raise_for_status()
        data = r.json()
        return [{
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": "https://www.youtube.com/watch?v=" + item["id"]["videoId"]
        } for item in data.get("items", [])]
    except Exception:
        return []
