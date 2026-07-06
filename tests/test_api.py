import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

HIMALAYAS_API = "https://himalayas.app/jobs/api?limit=10"

# ✅ TEST 1: API returns status 200
def test_api_returns_200():
    r = requests.get(HIMALAYAS_API, timeout=10)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"

# ✅ TEST 2: Response is valid JSON
def test_api_returns_json():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    assert isinstance(data, dict), "Response is not a JSON object"

# ✅ TEST 3: Response contains jobs key
def test_api_has_jobs_key():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    assert "jobs" in data, "'jobs' key missing from response"

# ✅ TEST 4: Jobs list is not empty
def test_api_jobs_not_empty():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    assert len(data["jobs"]) > 0, "Jobs list is empty!"

# ✅ TEST 5: Each job has required fields
def test_api_jobs_have_required_fields():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    required_fields = ["title", "companyName", "companySlug"]
    for job in data["jobs"]:
        for field in required_fields:
            assert field in job, f"Missing field '{field}' in job: {job.get('title')}"

# ✅ TEST 6: totalCount is a positive number
def test_api_total_count_positive():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    assert data.get("totalCount", 0) > 0, "totalCount should be positive"

# ✅ TEST 7: limit in response matches requested limit
def test_api_limit_respected():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    assert len(data["jobs"]) <= 10, "API returned more jobs than requested limit"

# ✅ TEST 8: Job titles are non-empty strings
def test_api_job_titles_are_strings():
    r = requests.get(HIMALAYAS_API, timeout=10)
    data = r.json()
    for job in data["jobs"]:
        assert isinstance(job["title"], str), "Job title is not a string"
        assert len(job["title"]) > 0, "Job title is empty"