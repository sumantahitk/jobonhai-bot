# main.py

from scraper_list import fetch_list_jobs
from scraper_detail import fetch_detail_data
from storage import load_jobs, save_jobs, job_exists
from notifier import send_telegram
from datetime import date   # ✅ ADD THIS

def main():
    old_jobs = load_jobs()
    new_jobs = old_jobs.copy()

    scraped_jobs = fetch_list_jobs()

    for job in scraped_jobs:
        if job_exists(old_jobs, job["detail_page"]):
            continue

        # Fetch detail page only for NEW jobs
        details = fetch_detail_data(job["detail_page"])
        job.update(details)

        # # ✅ SET POST DATE CORRECTLY
        # job["date_detected"] = date.today().strftime("%d-%m-%Y")  


        send_telegram(job)
        new_jobs.append(job)

    save_jobs(new_jobs)

if __name__ == "__main__":
    main()
