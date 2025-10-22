import time

class MemoryState:
    def __init__(self):
        self.last_prices = {}   # ticker -> (ts, price)
        self.seen_quakes = set()
        self.seen_items = set() # dedupe for news/rss
        self.update_offset = None
        self.chat_ids = set()

    def remember_price(self, ticker, price):
        self.last_prices[ticker] = (time.time(), float(price))

    def last_price(self, ticker):
        return self.last_prices.get(ticker)
