# import requests
# import re
# from bs4 import BeautifulSoup
# from config import LIST_URL, HEADERS
# from datetime import datetime


# def clean_title(title):
#     return re.sub(r"[-–]\s*\d+\s+posts?", "", title, flags=re.IGNORECASE).strip()


# def normalize_education(text):
#     if not text:
#         return []
#     parts = re.split(r",|/", text.upper())
#     return [p.strip() for p in parts if p.strip()]


# def extract_vacancies_from_text(text):
#     if not text:
#         return None

#     patterns = [
#         r"(\d+)\s+posts",
#         r"total\s+posts[:\s]*(\d+)",
#         r"(\d+)\s+vacancies"
#     ]

#     for p in patterns:
#         m = re.search(p, text, re.IGNORECASE)
#         if m:
#             return int(m.group(1))

#     return None


# def detect_job_type(org, title):
#     text = (org + " " + title).upper()
#     if "BANK" in text or "RBI" in text:
#         return "BANK"
#     if "RAILWAY" in text or "RRB" in text:
#         return "RAILWAY"
#     if "SSC" in text:
#         return "SSC"
#     if "UPSC" in text:
#         return "UPSC"
#     return "GOVT"

# def normalize_date(date_str):
#     try:
#         return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d-%m-%Y")
#     except Exception:
#         return date_str  # fallback, never crash


# def detect_state(title):
#     title = title.upper()
#     states = ["WB", "WEST BENGAL", "BIHAR", "UP", "MAHARASHTRA", "DELHI"]
#     for s in states:
#         if s in title:
#             return s
#     return "ALL INDIA"


# def fetch_list_jobs():
#     res = requests.get(LIST_URL, headers=HEADERS, timeout=15)
#     soup = BeautifulSoup(res.text, "html.parser")

#     jobs = []

#     # ✅ TARGET CORRECT TABLE
#     table = soup.find("table", class_="lattbl")
#     if not table:
#         print("❌ Main job table not found")
#         return jobs

#     rows = table.find_all("tr", class_="lattrbord")
#     print("Total rows found:", len(rows))

#     for row in rows:
#         cols = row.find_all("td")
#         if len(cols) < 7:
#             continue

#         try:

#             post_date_raw = cols[0].get_text(strip=True)
#             post_date = normalize_date(post_date_raw)

#             organization = cols[1].get_text(strip=True)
#             raw_title = cols[2].get_text(" ", strip=True)
#             education_text = cols[3].get_text(strip=True)
#             last_date = cols[5].get_text(strip=True)

#             link_tag = cols[6].find("a", href=True)
#             if not link_tag:
#                 continue

#             posts = extract_vacancies_from_text(raw_title)
#             title = clean_title(raw_title)

#             jobs.append({
#                 "title": title,
#                 "organization": organization,
#                 "posts": posts,
#                 "education": normalize_education(education_text),
#                 "job_type": detect_job_type(organization, title),
#                 "state": detect_state(title),
#                 "source_type": "JOB",
#                 "last_date": last_date,
#                 "detail_page": link_tag["href"],
#                 "date_detected": post_date   # ✅ REAL POST DATE
#             })

#         except Exception as e:
#             print("Row parse error:", e)

#     print("Jobs parsed:", len(jobs))
#     return jobs


import requests
import re
from bs4 import BeautifulSoup
from config import LIST_URL, HEADERS
from datetime import datetime


# ---------------- CONSTANTS ----------------

INDIAN_STATES_UT = {
    "ANDAMAN AND NICOBAR",
    "ANDHRA PRADESH",
    "ARUNACHAL PRADESH",
    "ASSAM",
    "BIHAR",
    "CHANDIGARH",
    "CHHATTISGARH",
    "DADRA AND NAGAR HAVELI",
    "DAMAN AND DIU",
    "DELHI",
    "GOA",
    "GUJARAT",
    "HARYANA",
    "HIMACHAL PRADESH",
    "JAMMU AND KASHMIR",
    "JHARKHAND",
    "KARNATAKA",
    "KERALA",
    "LAKSHADWEEP",
    "MADHYA PRADESH",
    "MAHARASHTRA",
    "MANIPUR",
    "MEGHALAYA",
    "MIZORAM",
    "NAGALAND",
    "ODISHA",
    "PUDUCHERRY",
    "PUNJAB",
    "RAJASTHAN",
    "SIKKIM",
    "TAMIL NADU",
    "TELANGANA",
    "TRIPURA",
    "UTTAR PRADESH",
    "UTTARAKHAND",
    "WEST BENGAL"
}


# ---------------- HELPERS ----------------

def clean_title(title):
    return re.sub(r"[-–]\s*\d+\s+posts?", "", title, flags=re.IGNORECASE).strip()


def normalize_education(text):
    if not text:
        return []
    parts = re.split(r",|/", text.upper())
    return [p.strip() for p in parts if p.strip()]


def extract_vacancies_from_text(text):
    if not text:
        return None

    patterns = [
        r"(\d+)\s+posts",
        r"total\s+posts[:\s]*(\d+)",
        r"(\d+)\s+vacancies"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return int(m.group(1))

    return None


def detect_job_type(org, title):
    text = (org + " " + title).upper()

    if any(k in text for k in ["BANK", "RBI", "IBPS", "SBI"]):
        return "BANK"
    if any(k in text for k in ["RAILWAY", "RRB"]):
        return "RAILWAY"
    if "SSC" in text:
        return "SSC"
    if "UPSC" in text:
        return "UPSC"
    if any(k in text for k in ["ARMY", "NAVY", "AIR FORCE", "IAF"]):
        return "DEFENCE"

    return "GOVT"


def normalize_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y").strftime("%d-%m-%Y")
    except Exception:
        return date_str


def normalize_heading(text):
    return re.sub(r"\s+", " ", text).strip()


def split_category_and_state(heading_text):
    clean = normalize_heading(heading_text)
    upper = clean.upper()

    # If heading is a state/UT
    if upper in INDIAN_STATES_UT:
        return "State Govt", clean

    # Otherwise it is a central category
    return clean, "All India"


# ---------------- MAIN SCRAPER ----------------

# def fetch_list_jobs():
#     res = requests.get(LIST_URL, headers=HEADERS, timeout=15)
#     soup = BeautifulSoup(res.text, "html.parser")

#     jobs = []

#     tables = soup.find_all("table", class_="lattbl")
#     if not tables:
#         print("❌ No job tables found")
#         return jobs

#     total_rows = 0

#     for table in tables:
#         heading = table.find_previous(["h2", "h3"])
#         raw_heading = heading.get_text(strip=True) if heading else "UNKNOWN"

#         category, state = split_category_and_state(raw_heading)

#         rows = table.find_all("tr", class_="lattrbord")
#         total_rows += len(rows)

#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) < 7:
#                 continue

#             try:
#                 post_date = normalize_date(cols[0].get_text(strip=True))
#                 organization = cols[1].get_text(strip=True)
#                 raw_title = cols[2].get_text(" ", strip=True)
#                 education_text = cols[3].get_text(strip=True)
#                 last_date = cols[5].get_text(strip=True)

#                 link_tag = cols[6].find("a", href=True)
#                 if not link_tag:
#                     continue

#                 jobs.append({
#                     "title": clean_title(raw_title),
#                     "organization": organization,
#                     "posts": extract_vacancies_from_text(raw_title),
#                     "education": normalize_education(education_text),
#                     "job_type": detect_job_type(organization, raw_title),
#                     "category": category,   # Banks / Railways / Defence / State Govt
#                     "state": state,         # West Bengal / Assam / All India
#                     "source_type": "JOB",
#                     "last_date": last_date,
#                     "detail_page": link_tag["href"],
#                     "date_detected": post_date
#                 })

#             except Exception as e:
#                 print("Row parse error:", e)

#     print("Total rows found:", total_rows)
#     print("Jobs parsed:", len(jobs))
#     return jobs
def find_section_heading(table):
    tag = table
    while True:
        tag = tag.find_previous()
        if not tag:
            return "UNKNOWN"

        # ✅ REAL FreeJobAlert section heading
        if tag.name == "h4" and "latsec" in tag.get("class", []):
            return tag.get_text(strip=True)


def fetch_list_jobs():
    res = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(res.text, "html.parser")

    jobs = []

    tables = soup.find_all("table", class_="lattbl")
    if not tables:
        print("❌ No job tables found")
        return jobs

    total_rows = 0

    for table in tables:
        # ✅ FIXED HEADING DETECTION
        raw_heading = find_section_heading(table)

        category, state = split_category_and_state(raw_heading)

        rows = table.find_all("tr", class_="lattrbord")
        total_rows += len(rows)

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 7:
                continue

            try:
                post_date = normalize_date(cols[0].get_text(strip=True))
                organization = cols[1].get_text(strip=True)
                raw_title = cols[2].get_text(" ", strip=True)
                education_text = cols[3].get_text(strip=True)
                last_date = cols[5].get_text(strip=True)

                link_tag = cols[6].find("a", href=True)
                if not link_tag:
                    continue

                jobs.append({
                    "title": clean_title(raw_title),
                    "organization": organization,
                    "posts": extract_vacancies_from_text(raw_title),
                    "education": normalize_education(education_text),
                    "job_type": detect_job_type(organization, raw_title),
                    "category": category,
                    "state": state,
                    "source_type": "JOB",
                    "last_date": last_date,
                    "detail_page": link_tag["href"],
                    "date_detected": post_date
                })

            except Exception as e:
                print("Row parse error:", e)

    print("Total rows found:", total_rows)
    print("Jobs parsed:", len(jobs))
    return jobs
