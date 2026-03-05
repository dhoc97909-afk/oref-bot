"""
🚨 בוט התראות פיקוד העורף → Google Chat
עיצוב זהה למערכת המבזקים הקיימת — פרופיל "צבע אדום"
"""
import requests, json, time, logging, os
from datetime import datetime

WEBHOOK_URLS = [
    "https://chat.googleapis.com/v1/spaces/AAQAgdDJy_E/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=Vh0L5WfIwKGBgkjw8_IahWLnZpJPBx433T4KKtA6E44",
    "https://chat.googleapis.com/v1/spaces/AAQAGhxWZZM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=IZg6yXQqGqRyXvBE26DX6t_E6IGJnKZoDokjzyjmY2E",
]

PROFILE_TITLE = "צבע אדום"
PROFILE_LOGO  = "https://i.postimg.cc/ncKKRgq9/image.png"

POLL_INTERVAL_SECONDS = 3
FILTER_AREAS = []  # ריק = כל הארץ

OREF_ALERTS_URL = "https://www.oref.org.il/WarningMessages/alert/alerts.json"
OREF_HEADERS = {
    "Referer": "https://www.oref.org.il/",
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest",
}

ALERT_ICONS = {"1":"🚀","2":"✈️","3":"💣","4":"🌊","5":"☢️","6":"🔫","7":"💥","13":"🛸","20":"🚨"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("oref-bot")


def get_current_alerts():
    try:
        resp = requests.get(OREF_ALERTS_URL, headers=OREF_HEADERS, timeout=5)
        if resp.status_code == 200 and resp.content.strip():
            text = resp.content.decode("utf-8-sig").strip()
            if text:
                return json.loads(text)
    except Exception as e:
        log.warning(f"שגיאה ב-API: {e}")
    return None


def format_message(alert):
    icon       = ALERT_ICONS.get(str(alert.get("cat", "20")), "⚠️")
    alert_type = alert.get("title", "התראת חירום")
    areas      = alert.get("data", [])
    desc       = alert.get("desc", "היכנסו למרחב המוגן מיד!")
    now        = datetime.now().strftime("%H:%M")

    areas_text = "\n".join(f"• {a}" for a in areas) if areas else "אזור לא ידוע"

    body_text = (
        f"<b>{icon} {alert_type}</b>\n\n"
        f"<b>🗺️ אזורים מוזהרים:</b>\n{areas_text}\n\n"
        f"<b>ℹ️ הנחיות:</b> {desc}"
    )

    return {
        "cardsV2": [{
            "card": {
                "header": {
                    "title":    PROFILE_TITLE,
                    "subtitle": f"נשלח ב: {now}",
                    "imageUrl": PROFILE_LOGO,
                    "imageType": "CIRCLE"
                },
                "sections": [{
                    "widgets": [
                        {"textParagraph": {"text": body_text}},
                        {"buttonList": {"buttons": [{
                            "text": "🔗 אתר פיקוד העורף",
                            "onClick": {"openLink": {"url": "https://www.oref.org.il/"}}
                        }]}}
                    ]
                }]
            }
        }]
    }


def send(message):
    for url in WEBHOOK_URLS:
        try:
            r = requests.post(url, json=message, timeout=10)
            log.info("✅ נשלח" if r.status_code == 200 else f"❌ {r.status_code}: {r.text}")
        except Exception as e:
            log.error(f"❌ {e}")


def main():
    log.info(f"🚀 בוט פיקוד העורף מופעל — {len(WEBHOOK_URLS)} קבוצות")
    send({"text": f"🟢 *בוט התראות פיקוד העורף הופעל*\nמאזין לעדכונים בזמן אמת..."})

    last_id = None
    while True:
        alert = get_current_alerts()
        if alert:
            cid = alert.get("id")
            if cid != last_id:
                areas = alert.get("data", [])
                if not FILTER_AREAS or any(f in a for f in FILTER_AREAS for a in areas):
                    log.info(f"🚨 התראה: {', '.join(areas)}")
                    send(format_message(alert))
                last_id = cid
        else:
            if last_id:
                log.info("✅ ההתראה הסתיימה")
                last_id = None
        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
