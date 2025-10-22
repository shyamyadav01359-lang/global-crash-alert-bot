from datetime import datetime
from dateutil import tz
import yfinance as yf
import time

# IST timezone
IST = tz.gettz("Asia/Kolkata")

def now_ist_str():
    return datetime.now(tz=IST).strftime("%d-%m-%Y %H:%M:%S IST")

# Yahoo Finance tickers
TICKERS = {
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW": "^DJI",
    "DAX": "^GDAXI",
    "Nikkei": "^N225",
    "HangSeng": "^HSI",
    "VIX": "^VIX",
    "DXY": "DX-Y.NYB",   # Dollar Index alternative ticker
    "Crude": "CL=F",
    "Gold": "GC=F",
}

def fetch_price(ticker):
    data = yf.download(tickers=ticker, period="1d", interval="1m", progress=False)
    if data is None or data.empty:
        return None
    return float(data["Close"].iloc[-1])

def pct_change(old, new):
    if old is None or old == 0: 
        return 0.0
    return (new - old) / old * 100.0

def market_checks(state, window_minutes=30):
    alerts = []
    for name, yft in TICKERS.items():
        price = fetch_price(yft)
        if price is None:
            continue

        prev = state.last_price(name)
        state.remember_price(name, price)

        if prev:
            _, old_price = prev
            change = pct_change(old_price, price)

            # Thresholds (default PRO mode)
            if name in ("S&P500","NASDAQ","DOW") and abs(change) >= 2.0:
                alerts.append(f"📉 {name} {change:.2f}% in last {window_minutes} min\nPrice: {price:.2f}")

            if name in ("DAX","Nikkei","HangSeng") and abs(change) >= 2.0:
                alerts.append(f"📉 {name} {change:.2f}% in last {window_minutes} min\nPrice: {price:.2f}")

            if name == "VIX" and change >= 15.0:
                alerts.append(f"⚠️ VIX spike {change:.2f}% (volatility stress)")

            if name == "DXY" and change >= 0.8:
                alerts.append(f"💵 DXY up {change:.2f}% (Dollar spike)")

            if name == "Crude" and change >= 4.0:
                alerts.append(f"🛢️ Crude +{change:.2f}% (energy shock)")

            if name == "Gold" and change >= 2.5:
                alerts.append(f"🥇 Gold +{change:.2f}% (risk-off bid)")

        time.sleep(0.2)

    if alerts:
        alerts = [f"🚨 MARKET MOVE ALERT ({now_ist_str()})"] + alerts
    return alerts
