from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.queries import get_engine
from sqlalchemy import text

BASE_URL = "https://merojob.com/search/?q=&page={}"

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # runs in background
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def parse_jobs(soup):
    jobs = []
    all_links = soup.find_all('a', href=True)
    job_links = [a for a in all_links if re.match(r'^/[a-z0-9-]+-\d+$', a['href'])]

    for link in job_links:
        try:
            # Title
            title_span = link.find('span', class_='text-blue-900')
            title = title_span.text.strip() if title_span else link.text.strip()

            # Go up to card level
            card = link.find_parent('div', class_=re.compile('rounded-lg'))

            # Company
            company = None
            company_link = card.find('a', href=re.compile('/employer/')) if card else None
            if company_link:
                company_span = company_link.find('span', class_='text-sm')
                company = company_span.text.strip() if company_span else company_link.text.strip()

            # Location
            location = "Nepal"
            if card:
                all_text = card.get_text(separator='|')
                # look for common Nepal locations
                nepal_locations = ['Kathmandu', 'Lalitpur', 'Bhaktapur', 'Pokhara',
                                   'Chitwan', 'Biratnagar', 'Butwal', 'Hetauda']
                for loc in nepal_locations:
                    if loc.lower() in all_text.lower():
                        location = loc
                        break

            # Remote check
            is_remote = 'remote' in (title + (company or '')).lower()

            source_url = "https://merojob.com" + link['href']

            if title:
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "job_type": "Full-time",
                    "salary_min": None,
                    "salary_max": None,
                    "description": None,
                    "source": "merojob",
                    "source_url": source_url,
                    "posted_at": datetime.now(),
                    "scraped_at": datetime.now(),
                    "is_remote": is_remote
                })
        except Exception as e:
            print(f"⚠️ Error parsing job: {e}")
            continue

    return jobs


def scrape_jobs(max_pages=5):
    all_jobs = []
    driver = get_driver()

    for page in range(1, max_pages + 1):
        url = BASE_URL.format(page)
        print(f"🔍 Scraping page {page}: {url}")

        try:
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            jobs = parse_jobs(soup)

            if not jobs:
                print(f"⚠️ No jobs on page {page}, stopping.")
                break

            all_jobs.extend(jobs)
            print(f"✅ Page {page}: {len(jobs)} jobs found")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Error on page {page}: {e}")
            continue

    driver.quit()
    print(f"\n🎉 Total jobs scraped: {len(all_jobs)}")
    return all_jobs


def save_to_db(jobs):
    if not jobs:
        print("No jobs to save.")
        return

    engine = get_engine()
    saved = 0

    with engine.connect() as conn:
        for job in jobs:
            try:
                conn.execute(text("""
                    INSERT INTO jobs (title, company, location, job_type,
                        salary_min, salary_max, description, source,
                        source_url, posted_at, scraped_at, is_remote)
                    VALUES (:title, :company, :location, :job_type,
                        :salary_min, :salary_max, :description, :source,
                        :source_url, :posted_at, :scraped_at, :is_remote)
                    ON CONFLICT (source_url) DO NOTHING
                """), job)
                saved += 1
            except Exception as e:
                print(f"⚠️ Skipping: {e}")
                continue
        conn.commit()

    print(f"✅ Saved {saved} new jobs to database!")


if __name__ == "__main__":
    jobs = scrape_jobs(max_pages=5)
    save_to_db(jobs)