import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.skill_extractor import extract_skills

# ✅ TEST 1: Basic skill detection
def test_detects_python():
    result = extract_skills("We need a Python developer")
    skill_names = [s[0] for s in result]
    assert "python" in skill_names

# ✅ TEST 2: Multiple skills detected
def test_detects_multiple_skills():
    result = extract_skills("Looking for Django and PostgreSQL experience with AWS")
    skill_names = [s[0] for s in result]
    assert "django" in skill_names
    assert "postgresql" in skill_names
    assert "aws" in skill_names

# ✅ TEST 3: Case insensitive
def test_case_insensitive():
    result = extract_skills("Must know PYTHON and SQL")
    skill_names = [s[0] for s in result]
    assert "python" in skill_names
    assert "sql" in skill_names

# ✅ TEST 4: Empty input returns empty list
def test_empty_input():
    result = extract_skills("")
    assert result == []

# ✅ TEST 5: None input returns empty list
def test_none_input():
    result = extract_skills(None)
    assert result == []

# ✅ TEST 6: No false match for "r" inside words
def test_no_false_match_r():
    result = extract_skills("We are looking for a coordinator and manager")
    skill_names = [s[0] for s in result]
    assert "r" not in skill_names

# ✅ TEST 7: Skills return correct category
def test_skill_category():
    result = extract_skills("Need strong communication and leadership skills")
    categories = {s[0]: s[1] for s in result}
    assert categories.get("communication") == "soft"
    assert categories.get("leadership") == "soft"

# ✅ TEST 8: Domain skills detected
def test_domain_skills():
    result = extract_skills("Experience in sales and marketing required")
    skill_names = [s[0] for s in result]
    assert "sales" in skill_names
    assert "marketing" in skill_names