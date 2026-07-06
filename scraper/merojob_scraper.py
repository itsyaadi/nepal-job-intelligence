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
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def scrape_job_description(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try common description containers
        for selector in ['job-description', 'description', 'job-detail', 'job_description']:
            desc = soup.find('div', class_=lambda c: c and selector in c.lower())
            if desc:
                return desc.get_text(separator=' ', strip=True)[:2000]

        # Fallback — grab all paragraph text
        paragraphs = soup.find_all('p')
        text = ' '.join(p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30)
        return text[:2000] if text else None

    except Exception as e:
        print(f"⚠️ Could not fetch description: {e}")
        return None


def parse_jobs(soup):
    jobs = []
    all_links = soup.find_all('a', href=True)
    job_links = [a for a in all_links if re.match(r'^/[a-z0-9-]+-\d+$', a['href'])]

    for link in job_links:
        try:
            title_span = link.find('span', class_='text-blue-900')
            title = title_span.text.strip() if title_span else link.text.strip()

            card = link.find_parent('div', class_=re.compile('rounded-lg'))

            company = None
            company_link = card.find('a', href=re.compile('/employer/')) if card else None
            if company_link:
                company_span = company_link.find('span', class_='text-sm')
                company = company_span.text.strip() if company_span else company_link.text.strip()

            location = "Nepal"
            if card:
                all_text = card.get_text(separator='|')
                nepal_locations = ['Kathmandu', 'Lalitpur', 'Bhaktapur', 'Pokhara',
                                   'Chitwan', 'Biratnagar', 'Butwal', 'Hetauda']
                for loc in nepal_locations:
                    if loc.lower() in all_text.lower():
                        location = loc
                        break

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

    # Step 1: scrape all listing pages
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

    # Step 2: fetch full description for each job
    print(f"\n📄 Fetching descriptions for {len(all_jobs)} jobs...")
    for i, job in enumerate(all_jobs):
        print(f"  [{i+1}/{len(all_jobs)}] {job['title']}")
        job['description'] = scrape_job_description(driver, job['source_url'])
        time.sleep(2)

    driver.quit()
    print(f"\n🎉 Total jobs scraped: {len(all_jobs)}")
    return all_jobs


def save_to_db(jobs):
    if not jobs:
        print("No jobs to save.")
        return

    engine = get_engine()
    saved = 0
    updated = 0

    with engine.connect() as conn:
        for job in jobs:
            try:
                # Try insert first
                result = conn.execute(text("""
                    INSERT INTO jobs (title, company, location, job_type,
                        salary_min, salary_max, description, source,
                        source_url, posted_at, scraped_at, is_remote)
                    VALUES (:title, :company, :location, :job_type,
                        :salary_min, :salary_max, :description, :source,
                        :source_url, :posted_at, :scraped_at, :is_remote)
                    ON CONFLICT (source_url) DO UPDATE
                        SET description = EXCLUDED.description,
                            scraped_at = EXCLUDED.scraped_at
                    RETURNING id
                """), job)
                if result.fetchone():
                    saved += 1
            except Exception as e:
                print(f"⚠️ Skipping: {e}")
                continue
        conn.commit()

    print(f"✅ Saved/updated {saved} jobs in database!")


if __name__ == "__main__":
    jobs = scrape_jobs(max_pages=20)
    save_to_db(jobs)