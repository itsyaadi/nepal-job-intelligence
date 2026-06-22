-- Nepal Job Intelligence Database Schema

-- Drop tables if they exist (for clean resets)
DROP TABLE IF EXISTS skill_trends CASCADE;
DROP TABLE IF EXISTS skills CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

-- Companies table
CREATE TABLE companies (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(255) UNIQUE NOT NULL,
    industry        VARCHAR(100),
    total_postings  INTEGER DEFAULT 0,
    last_active     TIMESTAMP
);

-- Jobs table
CREATE TABLE jobs (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(255) NOT NULL,
    company         VARCHAR(255),
    location        VARCHAR(255),
    job_type        VARCHAR(50),
    salary_min      INTEGER,
    salary_max      INTEGER,
    description     TEXT,
    source          VARCHAR(100),
    source_url      VARCHAR(500) UNIQUE,
    posted_at       TIMESTAMP,
    scraped_at      TIMESTAMP DEFAULT NOW(),
    is_remote       BOOLEAN DEFAULT FALSE
);

-- Skills table
CREATE TABLE skills (
    id          SERIAL PRIMARY KEY,
    job_id      INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_name  VARCHAR(100),
    category    VARCHAR(50)
);

-- Skill trends table
CREATE TABLE skill_trends (
    id          SERIAL PRIMARY KEY,
    skill_name  VARCHAR(100),
    week        DATE,
    count       INTEGER,
    growth_pct  FLOAT
);