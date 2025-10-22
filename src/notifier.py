import requests, time, logging
from typing import Iterable

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_ids: Iterable[str] | None = None):
        self.token = bot_token
        self.base = f"https://api.telegram.org/bot{self.token}"
        self.chat_ids = set(chat_ids or [])

    def add_chat(self, chat_id: int | str):
        self.chat_ids.add(str(chat_id))

    def send(self, text: str):
        if not self.chat_ids:
            logging.warning("No chat_ids registered yet. Skipping send.")
            return
        for cid in list(self.chat_ids):
            try:
                requests.post(f"{self.base}/sendMessage", json={"chat_id": cid, "text": text})
                time.sleep(0.2)
            except Exception as e:
                logging.exception(f"send failed to {cid}: {e}")

    def get_updates(self, offset=None):
        try:
            r = requests.get(f"{self.base}/getUpdates", params={"timeout": 10, "offset": offset})
            return r.json()
        except Exception:
            return {}
