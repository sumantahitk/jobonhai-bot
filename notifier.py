# import requests
# from config import BOT_TOKEN, CHAT_ID

# def send_telegram(job):
#     # Base message
#     msg = (
#         "🚨 NEW JOB ALERT 🚨\n\n"
#         f"📌 Title: {job['title']}\n"
#         f"🏢 Organization: {job['organization']}\n"
#         f"👥 Vacancies: {job.get('posts') or 'Not Mentioned'}\n"
#         f"⏰ Last Date: {job['last_date']}\n"
#     )

#     # Try apply link first
#     apply_link = job.get("important_links", {}).get("apply_online")
#     official_site = job.get("important_links", {}).get("official_website")

#     if apply_link:
#         msg += f"\n📝 Apply Online:\n{apply_link}\n"
#     elif official_site:
#         # Fallback to official website
#         msg += f"\n📝 Apply / Official Website:\n{official_site}\n"
#     else:
#         # No apply and no official website
#         msg += "\n📝 Apply Online:\nCheck Official Notification\n"

#     # Notification PDF
#     if job.get("notification_pdf"):
#         msg += f"\n📄 Official Notification PDF:\n{job['notification_pdf']}"

#     # Send to Telegram
#     url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
#     payload = {
#         "chat_id": CHAT_ID,
#         "text": msg,
#         "disable_web_page_preview": True
#     }
#     requests.post(url, json=payload)



# notifier.py

import requests
import time
from config import BOT_TOKEN, CHAT_ID


def send_telegram(job):
    # ===============================
    # QUALIFICATION PRIORITY LOGIC
    # ===============================
    qualification = "Not Mentioned"

    if job.get("education"):
        qualification = ", ".join(job["education"])
    elif job.get("qualification"):
        qualification = job["qualification"]

    # ===============================
    # CATEGORY & LOCATION
    # ===============================
    category = job.get("category", "N/A")
    state = job.get("state", "All India")

    # ===============================
    # MESSAGE BODY
    # ===============================
    msg = (
        "🚨 *NEW JOB ALERT* 🚨\n\n"
        f"📌 *Category:* {category}\n"
        f"📍 *Location:* {state}\n"
        f"📝 *Title:* {job['title']}\n"
        f"🏢 *Organization:* {job['organization']}\n"
        f"🎓 *Qualification:* {qualification}\n"
        f"👥 *Vacancies:* {job.get('posts') or 'Not Mentioned'}\n"
        f"🗓 *Post Date:* {job.get('date_detected')}\n"
        f"⏰ *Last Date:* {job['last_date']}\n"
    )

    apply_link = job.get("important_links", {}).get("apply_online")
    official_site = job.get("important_links", {}).get("official_website")
    apply_mode = job.get("apply_mode")

    if official_site:
        msg += f"\n🌐 *Official Website:* {official_site}"

    if apply_mode == "OFFLINE":
        msg += "\n📝 *Application Mode:* OFFLINE"
    else:
        if apply_link:
            msg += f"\n📝 *Apply Online:* {apply_link}"

    if job.get("notification_pdf"):
        msg += f"\n📄 *Official Notification PDF:*\n{job['notification_pdf']}"

    # ===============================
    # SEND MESSAGE (SAFE + RETRY)
    # ===============================
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    for attempt in range(3):  # retry max 3 times
        try:
            requests.post(url, json=payload, timeout=30)
            return
        except requests.exceptions.ReadTimeout:
            time.sleep(2)
        except Exception as e:
            print("Telegram error:", e)
            return
