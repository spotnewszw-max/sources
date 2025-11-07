-- Create database user and database
CREATE USER newsuser WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE news_aggregator OWNER newsuser;
GRANT ALL PRIVILEGES ON DATABASE news_aggregator TO newsuser;