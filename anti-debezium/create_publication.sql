-- Create a publication for all tables
-- Run this on your PostgreSQL database
CREATE PUBLICATION cdc_publication FOR ALL TABLES;

-- Alternatively, for specific tables only:
-- CREATE PUBLICATION cdc_publication FOR TABLE users;

-- Check if publication was created
SELECT * FROM pg_publication;
