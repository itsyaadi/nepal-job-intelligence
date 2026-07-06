import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.queries import get_engine
from sqlalchemy import text

def get_conn():
    return get_engine().connect()

# ✅ TEST 1: Database connects successfully
def test_db_connection():
    with get_conn() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1

# ✅ TEST 2: Jobs table exists and has data
def test_jobs_table_has_data():
    with get_conn() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM jobs")).scalar()
        assert count > 0, "Jobs table is empty!"

# ✅ TEST 3: No duplicate URLs in jobs table
def test_no_duplicate_urls():
    with get_conn() as conn:
        result = conn.execute(text("""
            SELECT source_url, COUNT(*) as count
            FROM jobs
            GROUP BY source_url
            HAVING COUNT(*) > 1
        """)).fetchall()
        assert len(result) == 0, f"Found duplicate URLs: {result}"

# ✅ TEST 4: All jobs have a title
def test_all_jobs_have_title():
    with get_conn() as conn:
        count = conn.execute(text("""
            SELECT COUNT(*) FROM jobs WHERE title IS NULL OR title = ''
        """)).scalar()
        assert count == 0, f"{count} jobs have no title!"

# ✅ TEST 5: All jobs have a valid source
def test_jobs_have_valid_source():
    valid_sources = ['merojob', 'himalayas']
    with get_conn() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT source FROM jobs
        """)).fetchall()
        sources = [r[0] for r in result]
        for source in sources:
            assert source in valid_sources, f"Unknown source: {source}"

# ✅ TEST 6: Skills table has data
def test_skills_table_has_data():
    with get_conn() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM skills")).scalar()
        assert count > 0, "Skills table is empty!"

# ✅ TEST 7: All skills reference a valid job
def test_skills_reference_valid_jobs():
    with get_conn() as conn:
        orphans = conn.execute(text("""
            SELECT COUNT(*) FROM skills s
            LEFT JOIN jobs j ON s.job_id = j.id
            WHERE j.id IS NULL
        """)).scalar()
        assert orphans == 0, f"{orphans} skills have no matching job!"

# ✅ TEST 8: is_remote column is boolean only
def test_is_remote_is_boolean():
    with get_conn() as conn:
        invalid = conn.execute(text("""
            SELECT COUNT(*) FROM jobs
            WHERE is_remote IS NULL
        """)).scalar()
        assert invalid == 0, f"{invalid} jobs have NULL is_remote!"