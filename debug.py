from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import re

options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get('https://merojob.com/search/?q=&page=1')
time.sleep(6)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find parent container of each job link
all_links = soup.find_all('a', href=True)
job_links = [a for a in all_links if re.match(r'^/[a-z0-9-]+-\d+$', a['href'])]

print(f"Jobs found: {len(job_links)}\n")

# Print the parent HTML of first 2 job cards
for l in job_links[:2]:
    parent = l.find_parent('div')
    if parent:
        # Go up a few levels to get full card
        for _ in range(4):
            if parent.find_parent('div'):
                parent = parent.find_parent('div')
            else:
                break
        print("=== JOB CARD HTML ===")
        print(parent.prettify()[:1500])
        print()

driver.quit()