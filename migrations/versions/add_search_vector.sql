-- Enable the required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Add search vector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

-- Create GIN index
CREATE INDEX articles_search_idx ON articles USING gin(search_vector);

-- Update existing records
UPDATE articles SET search_vector = 
    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- Create trigger to keep search_vector updated
CREATE TRIGGER articles_search_vector_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION
        tsvector_update_trigger(search_vector, 'pg_catalog.english', title, content);