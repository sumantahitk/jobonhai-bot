import requests
from bs4 import BeautifulSoup
from config import HEADERS


def fetch_detail_data(url):
    res = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    apply_link = None
    official_site = None
    pdf = None
    qualification = "Not Mentioned"

    # ===============================
    # APPLY MODE (CORRECT & SAFE)
    # ===============================
    apply_mode = "ONLINE"

    # Case A: URL explicitly says offline
    if "apply-offline" in url.lower():
        apply_mode = "OFFLINE"

    # Case B: Details table explicitly says offline
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) != 2:
                continue
            label = cols[0].get_text(" ", strip=True).lower()
            value = cols[1].get_text(" ", strip=True).lower()

            if "application mode" in label and "offline" in value:
                apply_mode = "OFFLINE"

    # ===============================
    # IMPORTANT LINKS SECTION
    # ===============================
    for h in soup.find_all(["h2", "h3"]):
        if "important links" in h.get_text(strip=True).lower():
            block = h.find_next(["table", "ul"])
            if not block:
                break

            # TABLE FORMAT
            if block.name == "table":
                for row in block.find_all("tr"):
                    cols = row.find_all("td")
                    if len(cols) != 2:
                        continue
                    label = cols[0].get_text(strip=True).lower()
                    value = cols[1]
                    link = value.find("a", href=True)

                    if "apply" in label and link:
                        apply_link = link["href"]

                    elif "official website" in label:
                        official_site = link["href"] if link else value.get_text(strip=True)

                    elif "notification" in label and link:
                        pdf = link["href"]

            # LIST FORMAT
            if block.name == "ul":
                for li in block.find_all("li"):
                    text = li.get_text(" ", strip=True).lower()
                    a = li.find("a", href=True)
                    if not a:
                        continue

                    if "apply" in text:
                        apply_link = a["href"]
                    elif "official website" in text:
                        official_site = a["href"]
                    elif "notification" in text:
                        pdf = a["href"]
            break

    # ===============================
    # HOW TO APPLY (FALLBACK)
    # ===============================
    if not apply_link:
        for h in soup.find_all(["h2", "h3"]):
            if "how to apply" in h.get_text(strip=True).lower():
                a = h.find_next("a", href=True)
                if a:
                    apply_link = a["href"]
                break

    # ===============================
    # DETAILS TABLE (QUALIFICATION + TEXT URL)
    # ===============================
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) != 2:
                continue

            label = cols[0].get_text(" ", strip=True).lower()
            value = cols[1].get_text(" ", strip=True)

            if "qualification" in label:
                qualification = value

            if "official website" in label and not official_site:
                official_site = value

    # ===============================
    # FINAL SAFETY NORMALIZATION
    # ===============================
    if apply_mode == "OFFLINE":
        apply_link = None

    if apply_link and not apply_link.startswith("http"):
        apply_link = None

    if official_site and not official_site.startswith("http"):
        official_site = None

    return {
        "important_links": {
            "apply_online": apply_link,
            "official_website": official_site
        },
        "notification_pdf": pdf,
        "qualification": qualification,
        "apply_mode": apply_mode
    }
