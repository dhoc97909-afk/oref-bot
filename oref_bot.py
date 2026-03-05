"""
🚨 בוט התראות פיקוד העורף → Google Chat
=========================================
"""
import requests, json, time, logging, os
from datetime import datetime

GOOGLE_CHAT_WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
POLL_INTERVAL_SECONDS   = 3
FILTER_AREAS            = []

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
            if text: return json.loads(text)
    except Exception as e:
        log.warning(f"שגיאה ב-API: {e}")
    return None

def format_message(alert):
    icon  = ALERT_ICONS.get(str(alert.get("cat","20")),"⚠️")
    title = alert.get("title","התראת חירום")
    areas = alert.get("data",[])
    desc  = alert.get("desc","היכנסו למרחב המוגן!")
    now   = datetime.now().strftime("%H:%M:%S")
    areas_text = "\n".join(f"• {a}" for a in areas) or "אזור לא ידוע"
    return {"cards":[{"header":{"title":f"{icon} {title}","subtitle":f"פיקוד העורף | {now}","imageUrl":"https://www.oref.org.il/Shared/images/Oref-logo.png","imageStyle":"IMAGE"},"sections":[{"widgets":[{"textParagraph":{"text":f"<b>🗺️ אזורים מוזהרים:</b>\n{areas_text}"}}]},{"widgets":[{"textParagraph":{"text":f"<b>ℹ️ הנחיות:</b> {desc}"}}]},{"widgets":[{"buttons":[{"textButton":{"text":"🔗 אתר פיקוד העורף","onClick":{"openLink":{"url":"https://www.oref.org.il/"}}}}]}]}]}]}

def send(message):
    try:
        r = requests.post(GOOGLE_CHAT_WEBHOOK_URL, json=message, timeout=10)
        log.info("✅ נשלח" if r.status_code==200 else f"❌ {r.status_code}: {r.text}")
    except Exception as e:
        log.error(f"❌ {e}")

def main():
    if not GOOGLE_CHAT_WEBHOOK_URL:
        log.error("❌ חסר WEBHOOK_URL!"); return
    log.info("🚀 בוט פיקוד העורף מופעל...")
    send({"text":"🟢 *בוט התראות פיקוד העורף הופעל*\nמאזין לעדכונים בזמן אמת..."})
    last_id = None
    while True:
        alert = get_current_alerts()
        if alert:
            cid = alert.get("id")
            if cid != last_id:
                areas = alert.get("data",[])
                if not FILTER_AREAS or any(f in a for f in FILTER_AREAS for a in areas):
                    log.info(f"🚨 התראה: {', '.join(areas)}")
                    send(format_message(alert))
                last_id = cid
        else:
            if last_id: log.info("✅ ההתראה הסתיימה"); last_id = None
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
