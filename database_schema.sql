-- Neon Database Schema for Flow of Funds Analysis System
-- PostgreSQL compatible schema with advanced features

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create enum types
CREATE TYPE document_category AS ENUM (
    'bank_statements',
    'property_docs',
    'wire_transfers',
    'corporate_governance',
    'litigation',
    'tax_documents',
    'supporting_docs',
    'other'
);

CREATE TYPE event_type AS ENUM (
    'wire_transfer',
    'property_purchase',
    'bank_transaction',
    'legal_filing',
    'tax_event',
    'corporate_event',
    'other'
);

CREATE TYPE exhibit_status AS ENUM (
    'draft',
    'ready',
    'filed',
    'admitted',
    'rejected'
);

CREATE TYPE analysis_status AS ENUM (
    'pending',
    'in_progress',
    'completed',
    'failed'
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_path TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size BIGINT NOT NULL,
    file_hash VARCHAR(64) UNIQUE NOT NULL,
    category document_category NOT NULL,
    content TEXT,
    content_vector vector(384), -- For semantic search using embeddings
    extracted_data JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP WITH TIME ZONE,
    indexed_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    INDEX idx_documents_category (category),
    INDEX idx_documents_file_type (file_type),
    INDEX idx_documents_created_at (created_at),
    INDEX idx_documents_content_gin USING gin(to_tsvector('english', content)),
    INDEX idx_documents_metadata_gin USING gin(metadata),
    INDEX idx_documents_vector USING ivfflat (content_vector vector_cosine_ops)
);

-- Timeline events table
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_date DATE NOT NULL,
    event_time TIME,
    event_type event_type NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(15, 2),
    currency VARCHAR(3) DEFAULT 'USD',
    source_account VARCHAR(255),
    destination_account VARCHAR(255),
    source_institution VARCHAR(255),
    destination_institution VARCHAR(255),
    reference_number VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_events_date (event_date),
    INDEX idx_events_type (event_type),
    INDEX idx_events_amount (amount),
    INDEX idx_events_accounts (source_account, destination_account)
);

-- Document-Event relationship table
CREATE TABLE document_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    event_id UUID NOT NULL REFERENCES timeline_events(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    extracted_by VARCHAR(50), -- 'manual', 'claude', 'system'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(document_id, event_id),
    INDEX idx_doc_events_document (document_id),
    INDEX idx_doc_events_event (event_id)
);

-- Analysis queries table
CREATE TABLE analysis_queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_text TEXT NOT NULL,
    query_vector vector(384),
    response TEXT,
    status analysis_status DEFAULT 'pending',
    model_used VARCHAR(50),
    tokens_used INTEGER,
    cost DECIMAL(10, 4),
    user_id VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    INDEX idx_queries_user (user_id),
    INDEX idx_queries_created (created_at),
    INDEX idx_queries_status (status)
);

-- Query-Document relationship table
CREATE TABLE query_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES analysis_queries(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    relevance_score FLOAT,
    
    UNIQUE(query_id, document_id),
    INDEX idx_query_docs_query (query_id),
    INDEX idx_query_docs_document (document_id)
);

-- Court exhibits table
CREATE TABLE court_exhibits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exhibit_number VARCHAR(50) NOT NULL,
    case_number VARCHAR(100) NOT NULL,
    case_caption TEXT NOT NULL,
    exhibit_description TEXT,
    status exhibit_status DEFAULT 'draft',
    date_marked DATE,
    admitted_date DATE,
    objections TEXT,
    ruling TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(case_number, exhibit_number),
    INDEX idx_exhibits_case (case_number),
    INDEX idx_exhibits_status (status)
);

-- Exhibit-Document relationship table
CREATE TABLE exhibit_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exhibit_id UUID NOT NULL REFERENCES court_exhibits(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_start INTEGER,
    page_end INTEGER,
    highlight_sections JSONB,
    
    UNIQUE(exhibit_id, document_id),
    INDEX idx_exhibit_docs_exhibit (exhibit_id),
    INDEX idx_exhibit_docs_document (document_id)
);

-- Exhibit packages table
CREATE TABLE exhibit_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_name VARCHAR(255) NOT NULL,
    case_number VARCHAR(100) NOT NULL,
    purpose TEXT,
    cover_letter TEXT,
    table_of_contents TEXT,
    certificate_of_service TEXT,
    filing_date DATE,
    filed_by VARCHAR(255),
    court_name VARCHAR(255),
    department VARCHAR(50),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_packages_case (case_number),
    INDEX idx_packages_created (created_at)
);

-- Package-Exhibit relationship table
CREATE TABLE package_exhibits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    package_id UUID NOT NULL REFERENCES exhibit_packages(id) ON DELETE CASCADE,
    exhibit_id UUID NOT NULL REFERENCES court_exhibits(id) ON DELETE CASCADE,
    order_number INTEGER NOT NULL,
    
    UNIQUE(package_id, exhibit_id),
    INDEX idx_package_exhibits_package (package_id),
    INDEX idx_package_exhibits_exhibit (exhibit_id)
);

-- Generated forms table
CREATE TABLE generated_forms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    form_type VARCHAR(100) NOT NULL,
    form_template TEXT,
    filled_content TEXT NOT NULL,
    form_data JSONB NOT NULL,
    generated_by VARCHAR(50),
    purpose TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_forms_type (form_type),
    INDEX idx_forms_created (created_at)
);

-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(50) NOT NULL,
    table_name VARCHAR(50) NOT NULL,
    record_id UUID,
    old_values JSONB,
    new_values JSONB,
    user_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_audit_created (created_at),
    INDEX idx_audit_table_record (table_name, record_id),
    INDEX idx_audit_user (user_id)
);

-- Create update trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers
CREATE TRIGGER update_timeline_events_updated_at BEFORE UPDATE ON timeline_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_court_exhibits_updated_at BEFORE UPDATE ON court_exhibits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exhibit_packages_updated_at BEFORE UPDATE ON exhibit_packages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(action, table_name, record_id, new_values, user_id)
        VALUES ('INSERT', TG_TABLE_NAME, NEW.id, to_jsonb(NEW), current_setting('app.current_user', true));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log(action, table_name, record_id, old_values, new_values, user_id)
        VALUES ('UPDATE', TG_TABLE_NAME, NEW.id, to_jsonb(OLD), to_jsonb(NEW), current_setting('app.current_user', true));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(action, table_name, record_id, old_values, user_id)
        VALUES ('DELETE', TG_TABLE_NAME, OLD.id, to_jsonb(OLD), current_setting('app.current_user', true));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Add audit triggers to critical tables
CREATE TRIGGER audit_documents AFTER INSERT OR UPDATE OR DELETE ON documents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_timeline_events AFTER INSERT OR UPDATE OR DELETE ON timeline_events
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_court_exhibits AFTER INSERT OR UPDATE OR DELETE ON court_exhibits
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create materialized views for performance
CREATE MATERIALIZED VIEW fund_flow_summary AS
SELECT 
    e.event_date,
    e.event_type,
    e.source_institution,
    e.destination_institution,
    SUM(e.amount) as total_amount,
    COUNT(*) as transaction_count,
    array_agg(DISTINCT d.file_name) as supporting_documents
FROM timeline_events e
LEFT JOIN document_events de ON e.id = de.event_id
LEFT JOIN documents d ON de.document_id = d.id
WHERE e.event_type IN ('wire_transfer', 'bank_transaction')
GROUP BY e.event_date, e.event_type, e.source_institution, e.destination_institution;

-- Create index on materialized view
CREATE INDEX idx_fund_flow_date ON fund_flow_summary(event_date);

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY fund_flow_summary;
END;
$$ language 'plpgsql';

-- Sample queries for common operations
COMMENT ON TABLE documents IS 'Stores all scanned documents with content and metadata';
COMMENT ON TABLE timeline_events IS 'Stores extracted timeline events from documents';
COMMENT ON TABLE court_exhibits IS 'Manages court exhibit preparation and tracking';
COMMENT ON TABLE analysis_queries IS 'Tracks all Claude/AI analysis queries and responses';

-- Grant permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO flow_analyzer_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO flow_analyzer_app;