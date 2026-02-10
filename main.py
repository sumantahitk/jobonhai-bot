# main.py

from scraper_list import fetch_list_jobs
from scraper_detail import fetch_detail_data
from storage import load_jobs, save_jobs, job_exists
from notifier import send_telegram
from datetime import date
import time

MAX_ALERTS = 5   # 🔒 prevent Telegram spam


def main():
    old_jobs = load_jobs()
    new_jobs = old_jobs.copy()

    scraped_jobs = fetch_list_jobs()
    sent_count = 0
    total_new = 0

    for job in scraped_jobs:
        if job_exists(old_jobs, job["detail_page"]):
            continue

        total_new += 1

        # Fetch detail page only for NEW jobs
        details = fetch_detail_data(job["detail_page"])
        job.update(details)

        if not job.get("date_detected"):
            job["date_detected"] = date.today().strftime("%d-%m-%Y")

        # 🔒 LIMIT TELEGRAM MESSAGES
        if sent_count < MAX_ALERTS:
            send_telegram(job)
            sent_count += 1
            time.sleep(1.5)  # Telegram safety

        new_jobs.append(job)

    # ✅ Summary message (SAFE)
    extra = total_new - sent_count
    if extra > 0:
        send_telegram({
            "title": f"{extra} more new jobs found",
            "organization": "Jobonhai",
            "last_date": "Visit website",
            "date_detected": date.today().strftime("%d-%m-%Y"),
            "category": "Multiple",
            "state": "India",
            "qualification": "Various",
            "posts": "",
            "important_links": {},
            "apply_mode": "",
            "notification_pdf": "",
            "education": [],
        })

    save_jobs(new_jobs)


if __name__ == "__main__":
    main()
