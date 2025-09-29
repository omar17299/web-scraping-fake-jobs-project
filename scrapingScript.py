from datetime import datetime
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# رابط الموقع
url = 'https://realpython.github.io/fake-jobs/'

# headers لتقليد المتصفح
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

# جلب الصفحة الرئيسية
page = requests.get(url, headers=headers)
page.raise_for_status()
time.sleep(1)
soup = BeautifulSoup(page.content, 'lxml')

# قائمة لتخزين الوظائف
jobs = []
cards = soup.find_all('div', class_='card')

for card in cards:
    title_tag = card.find("h2")
    title = title_tag.get_text(strip=True) if title_tag else None

    company_tag = card.find("h3")
    company = company_tag.get_text(strip=True) if company_tag else None

    location_tag = card.find("p", class_="location")
    location = location_tag.get_text(strip=True) if location_tag else None

    date_tag = card.find("time")
    date = date_tag.get_text(strip=True) if date_tag else None

    desc_tag = card.find("div", class_="description") or card.find("p")
    description = desc_tag.get_text(" ", strip=True) if desc_tag else ""

    link_tag = card.find('a', href=True)
    apply_link = link_tag['href'] if link_tag else None

    # جلب الوصف التفصيلي من صفحة Apply
    if apply_link:
        page_detail = requests.get(apply_link, headers=headers)
        page_detail.raise_for_status()
        time.sleep(1)
        soup_detail = BeautifulSoup(page_detail.text, "lxml")
        detail_desc_tag = soup_detail.find("div", class_="description") or soup_detail.find("p")
        if detail_desc_tag:
            description = detail_desc_tag.get_text(" ", strip=True)

    jobs.append({
        'title': title,
        'company': company,
        'location': location,
        'date': date,
        'description': description,
        'apply_link': apply_link
    })

# تحويل البيانات لـ DataFrame
df = pd.DataFrame(jobs, columns=['title','company','location','date','description','apply_link'])
df['scrape_date'] = datetime.utcnow().isoformat()

# تنظيف البيانات
df['title'] = df['title'].str.strip().str.lower()
df['company'] = df['company'].str.strip()
df['location'] = df['location'].str.strip()
df['description'] = df['description'].str.replace(r'\s+', ' ', regex=True).str.strip()

# فحص المهارات
skills = ["python","javascript","django","flask","sql","aws","docker"]
for skill in skills:
    df[f"skill_{skill}"] = df['description'].str.contains(
        rf"\b{re.escape(skill)}\b",
        case=False,
        na=False
    )

# حفظ CSV
df.to_csv("fake_jobs_scraped.csv", index=False)
print("Saved", len(df), "jobs -> fake_jobs_scraped.csv")
