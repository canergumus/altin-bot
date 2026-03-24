import os
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

def altin_fiyati_getir():
    try:
        # Ons altin USD (goldprice.org - ucretsiz, key gerektirmez)
        r1 = requests.get(
            "https://forex-data-feed.swissquote.com/public-quotes/bboquotes/instrument/XAU/USD",
            timeout=10
        )
        ons_usd = float(r1.json()[0]["spreadProfilePrices"][0]["bid"])
    except Exception:
        ons_usd = None

    try:
        # USD/TRY kuru (frankfurter.app - ucretsiz, key gerektirmez)
        r2 = requests.get(
            "https://api.frankfurter.app/latest?from=USD&to=TRY",
            timeout=10
        )
        usd_try = float(r2.json()["rates"]["TRY"])
    except Exception:
        usd_try = None

    now_ist = datetime.now(ISTANBUL_TZ)

    if ons_usd and usd_try:
        gram_tl = round((ons_usd / 31.1035) * usd_try, 2)
        return {
            "gram_tl" : str(gram_tl),
            "ons_usd" : str(round(ons_usd, 2)),
            "tarih"   : now_ist.strftime("%d.%m.%Y %H:%M"),
        }
    else:
        return {"gram_tl": "?", "ons_usd": "?", "tarih": now_ist.strftime("%d.%m.%Y %H:%M")}

def mesaj_olustur(veri):
    return "\n".join([
        "Gunluk Altin Raporu",
        "Tarih: " + veri["tarih"],
        "---",
        "Gram Altin: " + veri["gram_tl"] + " TL",
        "Ons Altin:  " + veri["ons_usd"] + " USD",
        "---",
        "Kaynak: Swissquote + Frankfurter"
    ])

def telegram_gonder(mesaj):
    url     = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logging.info("Mesaj gonderildi.")
    except Exception as e:
        logging.error("Telegram hatasi: " + str(e))

def gunluk_bildirim():
    veri  = altin_fiyati_getir()
    mesaj = mesaj_olustur(veri)
    logging.info(mesaj)
    telegram_gonder(mesaj)

gunluk_bildirim()
