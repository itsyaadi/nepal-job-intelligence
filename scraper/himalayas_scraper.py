import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.queries import get_engine
from sqlalchemy import text

BASE_URL = "https://himalayas.app/jobs/api?limit=50&offset={}"

def scrape_jobs(max_pages=5):
    all_jobs = []

    for page in range(max_pages):
        offset = page * 50
        url = BASE_URL.format(offset)
        print(f"🔍 Fetching page {page + 1}: offset={offset}")

        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            jobs_data = data.get('jobs', [])

            if not jobs_data:
                print("⚠️ No more jobs, stopping.")
                break

            for j in jobs_data:
                try:
                    # Check if open to Nepal or worldwide
                    locations = j.get('locations', [])
                    location_names = [l.get('name', '') for l in locations] if locations else []
                    location_str = ', '.join(location_names) if location_names else 'Worldwide'

                    job = {
                        "title": j.get('title'),
                        "company": j.get('companyName'),
                        "location": location_str,
                        "job_type": "Remote",
                        "salary_min": j.get('minSalary'),
                        "salary_max": j.get('maxSalary'),
                        "description": j.get('excerpt'),
                        "source": "himalayas",
                        "source_url": f"https://himalayas.app/jobs/{j.get('companySlug')}/{j.get('slug')}",
                        "posted_at": datetime.now(),
                        "scraped_at": datetime.now(),
                        "is_remote": True
                    }

                    if job["title"]:
                        all_jobs.append(job)

                except Exception as e:
                    print(f"⚠️ Error parsing job: {e}")
                    continue

            print(f"✅ Page {page + 1}: {len(jobs_data)} jobs fetched")

        except Exception as e:
            print(f"❌ Failed page {page + 1}: {e}")
            continue

    print(f"\n🎉 Total remote jobs scraped: {len(all_jobs)}")
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

    print(f"✅ Saved {saved} new remote jobs to database!")


if __name__ == "__main__":
    jobs = scrape_jobs(max_pages=5)
    save_to_db(jobs)