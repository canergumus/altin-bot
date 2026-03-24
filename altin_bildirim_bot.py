"""
Günlük Altın Fiyatı Telegram Botu — Render Edition
Saat 09:00 (Istanbul) otomatik bildirim gönderir.

Render env vars:
  TELEGRAM_TOKEN  → BotFather token
  CHAT_ID         → Telegram chat id
"""

import os
import re
import requests
import schedule
import time
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
BILDIRIM_SAATI = "09:00"


def altin_fiyati_getir() -> dict:
    url     = "https://bigpara.hurriyet.com.tr/altin/gram-altin-fiyati/"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        html = resp.text

        gram_match = re.search(r'"price"[^>]*>([\d.,]+)', html)
        ons_match  = re.search(r'ONS[^0-9]*([\d.,]+)\s*USD', html, re.IGNORECASE)

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
        f"🪙 *Gram Altın:*  `{veri['gram_tl']} TL`\n"
        f"🌍 *Ons Altın:*   `{veri['ons_usd']} USD`\n"
        f"──────────────────\n"
        f"_Bigpara serbest piyasa verisi_"
    )


def telegram_gonder(mesaj: str) -> bool:
    url     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logging.info("Mesaj gönderildi.")
        return True
    except Exception as e:
        logging.error(f"Telegram hatası: {e}")
        return False


def gunluk_bildirim():
    logging.info("Bildirim tetiklendi.")
    veri  = altin_fiyati_getir()
    mesaj = mesaj_olustur(veri)
    telegram_gonder(mesaj)


schedule.every().day.at(BILDIRIM_SAATI, "Europe/Istanbul").do(gunluk_bildirim)

logging.info(f"Bot ayakta. Her gün {BILDIRIM_SAATI} Istanbul saatiyle bildirim gönderilecek.")

while True:
    schedule.run_pending()
    time.sleep(30)
