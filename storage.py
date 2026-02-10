# storage.py

import os
import json
from datetime import datetime
from config import JSON_FILE

def load_jobs():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("jobs", [])

def save_jobs(jobs):
    data = {
        "last_checked": datetime.now().isoformat(timespec="seconds"),
        "source": "freejobalert",
        "jobs": jobs
    }
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def job_exists(old_jobs, detail_page):
    return any(j["detail_page"] == detail_page for j in old_jobs)
