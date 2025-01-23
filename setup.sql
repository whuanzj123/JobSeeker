-- Companies table to store information about employers
CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    website VARCHAR(255),
    glassdoor_rating DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Job posts table to store crawled job listings
CREATE TABLE job_posts (
    job_id SERIAL PRIMARY KEY,
    company_id INTEGER REFERENCES companies(company_id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    salary_min INTEGER,
    salary_max INTEGER,
    currency VARCHAR(3),
    employment_type VARCHAR(50),
    experience_level VARCHAR(50),
    remote_policy VARCHAR(50),
    original_posting_url TEXT,
    posting_date DATE,
    is_active BOOLEAN DEFAULT true,
    source_platform VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Skills table to track required and desired skills
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction table for job posts and required skills
CREATE TABLE job_skills (
    job_id INTEGER REFERENCES job_posts(job_id),
    skill_id INTEGER REFERENCES skills(skill_id),
    is_required BOOLEAN DEFAULT true,
    PRIMARY KEY (job_id, skill_id)
);

-- Table to store your applications and their status
CREATE TABLE applications (
    application_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_posts(job_id),
    status VARCHAR(50) NOT NULL,
    applied_date DATE,
    notes TEXT,
    next_steps TEXT,
    priority INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Interview preparation materials
CREATE TABLE interview_prep (
    prep_id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    topic VARCHAR(255) NOT NULL,
    content TEXT,
    difficulty_level VARCHAR(20),
    source VARCHAR(255),
    last_reviewed DATE,
    confidence_level INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table to store AI agent's analysis results
CREATE TABLE job_analysis (
    analysis_id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES job_posts(job_id),
    analysis_type VARCHAR(50),
    content TEXT,
    sentiment_score DECIMAL(3,2),
    keyword_matches JSON,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Triggers to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_posts_updated_at
    BEFORE UPDATE ON job_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interview_prep_updated_at
    BEFORE UPDATE ON interview_prep
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();