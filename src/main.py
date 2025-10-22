import os, time, logging
from utils import env
from state import MemoryState
from notifier import TelegramNotifier
from feeds import fetch_rss_items, fetch_quakes, REUTERS_RSS, AP_TOPNEWS, ALJAZEERA
from triggers import market_checks, now_ist_str

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
CHAT_ID = env("TELEGRAM_CHAT_ID")  # optional
POLL_INTERVAL = env("POLL_INTERVAL_SEC", 20, int)
WINDOW_MIN = env("WINDOW_MINUTES", 30, int)
EQ_MIN_MAG = env("EQ_MIN_MAG", 6.5, float)

if not BOT_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN not set.")

state = MemoryState()
notifier = TelegramNotifier(BOT_TOKEN, [CHAT_ID] if CHAT_ID else [])

def handle_bot_registration():
    updates = notifier.get_updates(state.update_offset)
    if not updates or not updates.get("ok"):
        return
    for upd in updates.get("result", []):
        state.update_offset = upd["update_id"] + 1
        msg = upd.get("message") or {}
        text = (msg.get("text") or "").strip().lower()
        chat = msg.get("chat") or {}
        cid = chat.get("id")
        if text in ("/start", "start", "/register", "register"):
            notifier.add_chat(cid)
            state.chat_ids.add(str(cid))
            notifier.send("✅ Registered for Global Alerts – You will receive high impact alerts here.")

def geo_news_scan():
    alerts = []
    for url in (REUTERS_RSS, AP_TOPNEWS, ALJAZEERA):
        for item in fetch_rss_items(url, limit=8):
            key = f"{url}|{item['id']}"
            if key in state.seen_items:
                continue
            title = (item["title"] or "").lower()
            summary = (item["summary"] or "").lower()
            text = f"{title} {summary}"

            hits = ["attack", "war", "missile", "coup", "explosion", "sanction", "nuclear",
                    "pandemic", "outbreak", "tsunami", "earthquake", "default", "collapse"]
            if any(h in text for h in hits):
                alerts.append(f"📰 {item['title']}\n{item['link']}")

            state.seen_items.add(key)
    if alerts:
        alerts.insert(0, f"🚨 BREAKING NEWS ({now_ist_str()})")
    return alerts

def quake_scan():
    alerts = []
    for q in fetch_quakes():
        if q["id"] in state.seen_quakes:
            continue
        state.seen_quakes.add(q["id"])
        try:
            mag = float(q["mag"] or 0)
        except:
            mag = 0
        if mag >= EQ_MIN_MAG:
            alerts.append(f"🌋 EARTHQUAKE M{mag:.1f} — {q['place']}\n{q['url']}")
    if alerts:
        alerts.insert(0, f"🚨 NATURAL ALERT ({now_ist_str()})")
    return alerts

def send_alerts(batch):
    if batch:
        notifier.send("\n\n".join(batch))

def main():
    logging.info("Bot started. Send /start to register your Telegram.")
    while True:
        try:
            handle_bot_registration()
            send_alerts(geo_news_scan())
            send_alerts(quake_scan())
            send_alerts(market_checks(state, window_minutes=WINDOW_MIN))
        except Exception as e:
            logging.exception(f"Loop Error: {e}")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
