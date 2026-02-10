# main.py

from scraper_list import fetch_list_jobs
from scraper_detail import fetch_detail_data
from storage import load_jobs, save_jobs, job_exists
from notifier import send_telegram
from datetime import date

MAX_ALERTS = 5   # 🔒 prevent Telegram spam


def main():
    old_jobs = load_jobs()
    new_jobs = old_jobs.copy()

    scraped_jobs = fetch_list_jobs()
    sent_count = 0

    for job in scraped_jobs:
        if job_exists(old_jobs, job["detail_page"]):
            continue

        # Fetch detail page only for NEW jobs
        details = fetch_detail_data(job["detail_page"])
        job.update(details)

        # Optional: ensure post date exists
        if not job.get("date_detected"):
            job["date_detected"] = date.today().strftime("%d-%m-%Y")

        # 🔒 LIMIT TELEGRAM MESSAGES
        if sent_count < MAX_ALERTS:
            send_telegram(job)
            sent_count += 1

        new_jobs.append(job)

    # Summary message if many jobs found
    extra = len(new_jobs) - len(old_jobs) - MAX_ALERTS
    if extra > 0:
        send_telegram({
            "title": "More Jobs Available",
            "organization": "Jobonhai",
            "last_date": "Check Website",
            "date_detected": date.today().strftime("%d-%m-%Y"),
            "category": "Multiple",
            "state": "Various",
            "qualification": "",
            "posts": "",
            "important_links": {},
            "apply_mode": "",
            "notification_pdf": "",
            "education": [],
        })

    save_jobs(new_jobs)


if __name__ == "__main__":
    main()
