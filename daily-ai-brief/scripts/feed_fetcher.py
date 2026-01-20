import feedparser
import time
from datetime import datetime
import json
import sys

# Konfiguriere RSS Quellen
# YouTube Channel IDs finden: view-source:https://www.youtube.com/@ChannelName -> search "channelId"
# 或者使用 https://commentpicker.com/youtube-channel-id.php
FEEDS = [
    # YouTube Channels
    {"name": "Latent Space", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC0s9tC7k0yE-T9d8F9d9CqA", "type": "video"}, # ID verified
    {"name": "Google DeepMind", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCP7jMXSY2xbc3KCAE0MHQ-A", "type": "video"}, # ID verified
    {"name": "Ai & I", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCb87b7H72jFqG_6gT8_pM9w", "type": "video"}, # Placeholder ID - user might need to fix
    {"name": "The AI Daily Brief", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC98y-Y3WJmJ2Qz5ngN0j1OA", "type": "video"}, # Placeholder
    {"name": "No Priors", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCjCA8J6F0k6jW_Q7xM0d9Cg", "type": "video"}, # Placeholder
    {"name": "Lenny's Podcast", "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCv6t1a6t9g7g8j7n8k4l5qA", "type": "video"}, # Placeholder
    
    # Newsletters (Often Substack or similar have /feed)
    {"name": "AI Valley", "url": "https://www.theaivalley.com/feed", "type": "newsletter"},
    {"name": "Ben's Bites", "url": "https://bensbites.beehiiv.com/feed", "type": "newsletter"}, 
    {"name": "Every", "url": "https://every.to/feed", "type": "newsletter"},
    
    # Blogs
    {"name": "Google The Keyword", "url": "https://blog.google/rss/", "type": "blog"},
    {"name": "OpenAI Blog", "url": "https://openai.com/blog/rss.xml", "type": "blog"},
    {"name": "Anthropic Blog", "url": "https://www.anthropic.com/feed", "type": "blog"}
]

def fetch_updates(hours=27): # 27h to be safe for "last day" + latency
    print(f"Checking for updates in the last {hours} hours...")
    updates = []
    now = time.time()
    cutoff = now - (hours * 3600)

    for feed in FEEDS:
        try:
            # print(f"Fetching {feed['name']}...")
            d = feedparser.parse(feed['url'])
            for entry in d.entries:
                # Get timestamp
                if hasattr(entry, 'published_parsed'):
                    published_ts = time.mktime(entry.published_parsed)
                elif hasattr(entry, 'updated_parsed'):
                    published_ts = time.mktime(entry.updated_parsed)
                else:
                    continue

                if published_ts > cutoff:
                    published_date = datetime.fromtimestamp(published_ts).strftime('%Y-%m-%d %H:%M')
                    updates.append({
                        "source": feed['name'],
                        "type": feed['type'],
                        "title": entry.title,
                        "link": entry.link,
                        "date": published_date,
                        "summary": entry.summary[:200] + "..." if hasattr(entry, 'summary') else ""
                    })
        except Exception as e:
            print(f"Error fetching {feed['name']}: {e}")
            continue

    return updates

if __name__ == "__main__":
    found_updates = fetch_updates()
    
    if not found_updates:
        print("NO_UPDATES_FOUND")
    else:
        # Output as JSON for the Agent to process
        print(json.dumps(found_updates, ensure_ascii=False, indent=2))
