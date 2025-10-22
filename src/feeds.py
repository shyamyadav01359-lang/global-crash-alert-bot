import time, requests, feedparser, logging
from typing import List, Dict

# Fast global news RSS feeds
REUTERS_RSS = "https://feeds.reuters.com/reuters/worldNews"
AP_TOPNEWS  = "https://rss.apnews.com/apf-topnews"
ALJAZEERA   = "https://www.aljazeera.com/xml/rss/all.xml"

# USGS Earthquakes feed (significant quakes, last hour)
USGS_SIG = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson"

def fetch_rss_items(url: str, limit: int = 10) -> List[Dict]:
    try:
        feed = feedparser.parse(url)
        items = []
        for e in (feed.entries or [])[:limit]:
            items.append({
                "id": getattr(e, "id", getattr(e, "link", "")),
                "title": getattr(e, "title", ""),
                "link": getattr(e, "link", ""),
                "published": getattr(e, "published", ""),
                "summary": getattr(e, "summary", "")[:500]
            })
        return items
    except Exception as e:
        logging.warning(f"RSS error {url}: {e}")
        return []

def fetch_quakes():
    try:
        r = requests.get(USGS_SIG, timeout=10)
        j = r.json()
        out = []
        for f in j.get("features", []):
            props = f.get("properties", {})
            out.append({
                "id": f.get("id"),
                "mag": props.get("mag"),
                "place": props.get("place"),
                "time": props.get("time"), # ms since epoch
                "url": props.get("url"),
            })
        return out
    except Exception as e:
        logging.warning(f"USGS error: {e}")
        return []
