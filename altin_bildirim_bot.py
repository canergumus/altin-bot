import os
import re
import requests
import logging
from datetime import datetime
import pytz

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID        = os.environ["CHAT_ID"]
ISTANBUL_TZ    = pytz.timezone("Europe/Istanbul")

def altin_fiyati_getir() -> dict:
    url     = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text
        gram_match = re.search(r'altin.*?(\d{4,5}[.,]\d{2})', html, re.IGNORECASE)
        ons_match  = re.search(r'(\d{4,5}[.,]\d{2,3}).*?USD', html, re.IGNORECASE)
        now_ist = datetime.now(ISTANBUL_TZ)
        return {
            "gram_tl" : gram_match.group(1) if gram_match else "—",
            "ons_usd" : ons_match.group(1)  if ons_match  else "—",
            "tarih"   : now_ist.strftime("%d.%m.%Y %H:%M"),
        }
    except Exception as e:
        logging.error(f"Fiyat çekilemedi: {e}")
        return {
            "gram_tl" : "—",
            "ons_usd" : "—",
            "tarih"   : datetime.now(ISTANBUL_TZ).strftime("%d.%m.%Y %H:%M"),
        }

def mesaj_olustur(veri: dict) -> str:
    return (
        f"📊 *Günlük Altın Raporu*\n"
        f"🗓 {veri['tarih']}\n"
        f"──────────────────\n"
        f"🪙 *Gram Altın:*  `{veri['
