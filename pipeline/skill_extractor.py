import re
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.queries import get_engine

# Master skills list
SKILLS = {
    "technical": [
        "python", "java", "javascript", "typescript", "php", "ruby",
        "swift", "kotlin", "scala", "matlab",
        "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
        "spring", "laravel", "express", "fastapi",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux",
        "machine learning", "deep learning", "nlp", "computer vision",
        "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy",
        "power bi", "tableau", "excel", "git", "rest api", "graphql",
        "data analysis", "data science", "business intelligence",
        "selenium", "postman", "jira", "confluence", "figma"
    ],
    "soft": [
        "communication", "teamwork", "leadership", "problem solving",
        "critical thinking", "time management", "project management",
        "agile", "scrum"
    ],
    "domain": [
        "accounting", "finance", "marketing", "sales", "operations",
        "supply chain", "logistics", "healthcare", "education", "legal",
        "customer service", "business analysis", "human resources"
    ]
}


def extract_skills(text):
    if not text:
        return []

    text_lower = text.lower()
    found = []

    # Skills that need strict whole-word matching
    strict_match = [
        "r", "go", "c#", "c++", "java", "scala", "ruby", "rust",
        "hr", "sql", "css", "git", "aws", "gcp"
    ]

    for category, skill_list in SKILLS.items():
        for skill in skill_list:
            if skill in strict_match:
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, text_lower):
                    found.append((skill, category))
            else:
                if skill in text_lower:
                    found.append((skill, category))

    return found

def process_all_jobs():
    engine = get_engine()
    processed = 0
    total_skills = 0

    with engine.connect() as conn:
        # Get all jobs
        jobs = conn.execute(text(
            "SELECT id, title, description FROM jobs"
        )).fetchall()

        print(f"📋 Processing {len(jobs)} jobs...")

        for job in jobs:
            job_id, title, description = job

            # Combine title + description for skill search
            combined = f"{title or ''} {description or ''}"
            skills = extract_skills(combined)

            # Delete old skills for this job (in case of rerun)
            conn.execute(text(
                "DELETE FROM skills WHERE job_id = :job_id"
            ), {"job_id": job_id})

            # Insert new skills
            for skill_name, category in skills:
                conn.execute(text("""
                    INSERT INTO skills (job_id, skill_name, category)
                    VALUES (:job_id, :skill_name, :category)
                """), {
                    "job_id": job_id,
                    "skill_name": skill_name,
                    "category": category
                })
                total_skills += 1

            processed += 1

        conn.commit()

    print(f"✅ Processed {processed} jobs")
    print(f"🧠 Total skills extracted: {total_skills}")


def print_top_skills(limit=20):
    engine = get_engine()
    with engine.connect() as conn:
        results = conn.execute(text("""
            SELECT skill_name, COUNT(*) as count
            FROM skills
            GROUP BY skill_name
            ORDER BY count DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()

    print(f"\n🏆 Top {limit} In-Demand Skills in Nepal Job Market:")
    print("-" * 40)
    for i, (skill, count) in enumerate(results, 1):
        bar = "█" * count
        print(f"{i:2}. {skill:<25} {count:3} jobs  {bar}")


if __name__ == "__main__":
    process_all_jobs()
    print_top_skills()