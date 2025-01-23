-- Create companies table
CREATE TABLE companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    base_url VARCHAR(255) NOT NULL,
    crawler_type VARCHAR(50) NOT NULL,
    last_crawl_at TIMESTAMP,
    crawl_interval_days INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Create locations table
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    city VARCHAR(255) NOT NULL
);

-- Create job_posts table
CREATE TABLE job_posts (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    job_reference_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    department VARCHAR(255),
    level VARCHAR(100),
    job_type VARCHAR(100),
    job_link VARCHAR(2048) NOT NULL,
    description TEXT,
    requirements TEXT,
    raw_data JSONB,
    first_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT unique_job_per_company UNIQUE (company_id, job_reference_id)
);

-- Create post_locations table
CREATE TABLE post_locations (
    id SERIAL PRIMARY KEY,
    job_post_id INTEGER NOT NULL REFERENCES job_posts(id),
    location_id INTEGER NOT NULL REFERENCES locations(id),
    is_remote BOOLEAN NOT NULL DEFAULT FALSE,
    work_type VARCHAR(50) CHECK (work_type IN ('hybrid', 'onsite', 'remote')),
    CONSTRAINT unique_job_location UNIQUE (job_post_id, location_id)
);

-- Create job_salary_ranges table
CREATE TABLE job_salary_ranges (
    id SERIAL PRIMARY KEY,
    job_post_id INTEGER NOT NULL REFERENCES job_posts(id),
    min_salary DECIMAL(12,2),
    max_salary DECIMAL(12,2),
    currency CHAR(3) NOT NULL,
    is_estimated BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (min_salary <= max_salary),
    CHECK (min_salary >= 0),
    CHECK (max_salary >= 0)
);

-- Create crawl_logs table
CREATE TABLE crawl_logs (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id),
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    status VARCHAR(50) NOT NULL,
    jobs_found INTEGER DEFAULT 0,
    jobs_new INTEGER DEFAULT 0,
    jobs_updated INTEGER DEFAULT 0,
    jobs_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for foreign keys and commonly queried fields
CREATE INDEX idx_job_posts_company_id ON job_posts(company_id);
CREATE INDEX idx_post_locations_job_post_id ON post_locations(job_post_id);
CREATE INDEX idx_post_locations_location_id ON post_locations(location_id);
CREATE INDEX idx_job_salary_ranges_job_post_id ON job_salary_ranges(job_post_id);
CREATE INDEX idx_crawl_logs_company_id ON crawl_logs(company_id);
CREATE INDEX idx_job_posts_is_active ON job_posts(is_active);
CREATE INDEX idx_companies_is_active ON companies(is_active);