import os, time, logging
from datetime import datetime
from dateutil import tz

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# IST timezone
IST = tz.gettz("Asia/Kolkata")

def now_ist():
    return datetime.now(tz=IST).strftime("%d-%m-%Y %H:%M:%S IST")

def main():
    while True:
        logging.info(f"Bot heartbeat — running at {now_ist()}")
        time.sleep(60)

if __name__ == "__main__":
    main()
