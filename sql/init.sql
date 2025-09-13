-- HexaBuilders PostgreSQL Database Initialization
-- Enterprise Microservices Partner Management Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create separate databases for each microservice
-- Note: In production, these would be separate database instances
-- For development, we use schemas to simulate separate databases

-- Onboarding Service Schema
CREATE SCHEMA IF NOT EXISTS onboarding;

-- Recruitment Service Schema  
CREATE SCHEMA IF NOT EXISTS recruitment;

-- Campaign Management Service Schema
CREATE SCHEMA IF NOT EXISTS campaign_management;

-- Partner Management Service uses public schema

-- Partners table
CREATE TABLE IF NOT EXISTS partners (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    telefono VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('INDIVIDUAL', 'EMPRESA', 'STARTUP')),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE' CHECK (status IN ('ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'ELIMINADO', 'VALIDADO', 'PENDIENTE')),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    codigo_postal VARCHAR(20),
    email_validated BOOLEAN DEFAULT FALSE,
    phone_validated BOOLEAN DEFAULT FALSE,
    identity_validated BOOLEAN DEFAULT FALSE,
    business_validated BOOLEAN DEFAULT FALSE,
    total_campaigns INTEGER DEFAULT 0,
    completed_campaigns INTEGER DEFAULT 0,
    success_rate DECIMAL(3,2) DEFAULT 0.0,
    total_commissions DECIMAL(12,2) DEFAULT 0.0,
    average_rating DECIMAL(2,1) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    presupuesto DECIMAL(12,2) DEFAULT 0.0,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('MARKETING', 'VENTAS', 'PROMOCIONAL', 'BRAND')),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE' CHECK (status IN ('ACTIVA', 'INACTIVA', 'COMPLETADA', 'CANCELADA', 'PENDIENTE')),
    partner_id UUID REFERENCES partners(id),
    total_conversions INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    conversion_rate DECIMAL(3,2) DEFAULT 0.0,
    roi DECIMAL(8,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Commissions table
CREATE TABLE IF NOT EXISTS commissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID NOT NULL REFERENCES partners(id),
    campaign_id UUID REFERENCES campaigns(id),
    monto DECIMAL(12,2) NOT NULL,
    porcentaje DECIMAL(3,2) DEFAULT 0.0,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('FIJO', 'PORCENTUAL', 'HIBRIDO')),
    status VARCHAR(50) NOT NULL DEFAULT 'PENDIENTE' CHECK (status IN ('PENDIENTE', 'APROBADA', 'PAGADA', 'CANCELADA', 'RECHAZADA')),
    fecha_calculo TIMESTAMP NOT NULL,
    fecha_pago TIMESTAMP,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics reports table
CREATE TABLE IF NOT EXISTS analytics_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('PARTNER_PERFORMANCE', 'CAMPAIGN_ANALYSIS', 'COMMISSION_SUMMARY', 'REVENUE_REPORT', 'CONVERSION_ANALYSIS')),
    status VARCHAR(50) NOT NULL DEFAULT 'GENERANDO' CHECK (status IN ('GENERANDO', 'COMPLETADO', 'ERROR', 'ARCHIVADO')),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    datos_json JSONB,
    metricas_json JSONB,
    configuracion_json JSONB,
    archivo_path VARCHAR(500),
    partner_id UUID REFERENCES partners(id),
    campaign_id UUID REFERENCES campaigns(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Event store table for domain events
CREATE TABLE IF NOT EXISTS domain_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_version INTEGER DEFAULT 1,
    event_data JSONB NOT NULL,
    metadata JSONB,
    occurred_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_partners_email ON partners(email);
CREATE INDEX IF NOT EXISTS idx_partners_tipo ON partners(tipo);
CREATE INDEX IF NOT EXISTS idx_partners_status ON partners(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_partner_id ON campaigns(partner_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_fecha_inicio ON campaigns(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_campaigns_fecha_fin ON campaigns(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_commissions_partner_id ON commissions(partner_id);
CREATE INDEX IF NOT EXISTS idx_commissions_campaign_id ON commissions(campaign_id);
CREATE INDEX IF NOT EXISTS idx_commissions_status ON commissions(status);
CREATE INDEX IF NOT EXISTS idx_commissions_fecha_calculo ON commissions(fecha_calculo);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_partner_id ON analytics_reports(partner_id);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_campaign_id ON analytics_reports(campaign_id);
CREATE INDEX IF NOT EXISTS idx_analytics_reports_tipo ON analytics_reports(tipo);
CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate_id ON domain_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate_type ON domain_events(aggregate_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_event_type ON domain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_occurred_on ON domain_events(occurred_on);

-- Insert sample data
INSERT INTO partners (id, nombre, email, telefono, tipo, status, direccion, ciudad, pais, email_validated, phone_validated, identity_validated) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'TechCorp S.A.S.', 'admin@techcorp.com', '+57-1-2345678', 'EMPRESA', 'ACTIVO', 'Calle 93 #15-20', 'Bogotá', 'Colombia', true, true, true),
    ('550e8400-e29b-41d4-a716-446655440002', 'Innovate Partners Ltd.', 'contact@innovate.com', '+1-555-9876543', 'EMPRESA', 'ACTIVO', '123 Innovation Ave', 'San Francisco', 'USA', true, true, true),
    ('550e8400-e29b-41d4-a716-446655440003', 'StartupHub', 'hello@startuphub.co', '+57-300-1234567', 'STARTUP', 'ACTIVO', 'Zona Rosa #45-12', 'Medellín', 'Colombia', true, false, false),
    ('550e8400-e29b-41d4-a716-446655440004', 'Juan Pérez', 'juan.perez@email.com', '+57-312-8765432', 'INDIVIDUAL', 'PENDIENTE', 'Carrera 7 #80-15', 'Bogotá', 'Colombia', false, false, false)
ON CONFLICT (id) DO NOTHING;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_partners_updated_at BEFORE UPDATE ON partners
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_commissions_updated_at BEFORE UPDATE ON commissions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_analytics_reports_updated_at BEFORE UPDATE ON analytics_reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- ONBOARDING SERVICE TABLES (Event Sourcing)
-- ==============================================

-- Contracts table (CQRS Read Model)
CREATE TABLE IF NOT EXISTS onboarding.contracts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID NOT NULL,
    contract_type VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    version INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contract Events (Event Store)
CREATE TABLE IF NOT EXISTS onboarding.contract_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correlation_id UUID,
    causation_id UUID
);

-- Contract Snapshots (Performance optimization)
CREATE TABLE IF NOT EXISTS onboarding.contract_snapshots (
    aggregate_id UUID PRIMARY KEY,
    aggregate_data JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- RECRUITMENT SERVICE TABLES (CRUD + Search)
-- ==============================================

-- Candidates table
CREATE TABLE IF NOT EXISTS recruitment.candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    location VARCHAR(255),
    years_of_experience INTEGER DEFAULT 0,
    expected_salary DECIMAL(10,2),
    availability VARCHAR(50) DEFAULT 'AVAILABLE',
    skills JSONB DEFAULT '[]',
    education JSONB DEFAULT '[]',
    work_history JSONB DEFAULT '[]',
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS recruitment.jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    salary_min DECIMAL(10,2),
    salary_max DECIMAL(10,2),
    job_type VARCHAR(50) DEFAULT 'FULL_TIME',
    experience_level VARCHAR(50),
    required_skills JSONB DEFAULT '[]',
    preferred_skills JSONB DEFAULT '[]',
    benefits JSONB DEFAULT '[]',
    requirements JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'DRAFT',
    max_applications INTEGER DEFAULT 100,
    current_applications INTEGER DEFAULT 0,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS recruitment.applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES recruitment.jobs(id),
    candidate_id UUID NOT NULL REFERENCES recruitment.candidates(id),
    status VARCHAR(50) DEFAULT 'PENDING',
    match_score DECIMAL(5,2),
    cover_letter TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    notes JSONB DEFAULT '{}',
    UNIQUE(job_id, candidate_id)
);

-- ==============================================
-- CAMPAIGN MANAGEMENT TABLES (Hybrid CRUD + Events)
-- ==============================================

-- Campaigns table (Main aggregate)
CREATE TABLE IF NOT EXISTS campaign_management.campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    partner_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) DEFAULT 'DRAFT',
    budget DECIMAL(10,2) NOT NULL,
    budget_spent DECIMAL(10,2) DEFAULT 0,
    target_audience JSONB DEFAULT '{}',
    creative_assets JSONB DEFAULT '[]',
    schedule JSONB DEFAULT '{}',
    performance_metrics JSONB DEFAULT '{}',
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaign Events (Audit trail)
CREATE TABLE IF NOT EXISTS campaign_management.campaign_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    correlation_id UUID,
    causation_id UUID
);

-- Ad Groups table
CREATE TABLE IF NOT EXISTS campaign_management.ad_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaign_management.campaigns(id),
    name VARCHAR(255) NOT NULL,
    budget DECIMAL(10,2),
    budget_spent DECIMAL(10,2) DEFAULT 0,
    targeting_criteria JSONB DEFAULT '{}',
    ads JSONB DEFAULT '[]',
    performance_metrics JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- SHARED INTEGRATION TABLES
-- ==============================================

-- Integration Events Outbox Pattern
CREATE TABLE IF NOT EXISTS integration_events_outbox (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(255) NOT NULL,
    event_data JSONB NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    correlation_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PENDING'
);

-- ==============================================
-- INDEXES FOR PERFORMANCE
-- ==============================================

-- Onboarding indexes
CREATE INDEX IF NOT EXISTS idx_onboarding_contract_events_aggregate_id ON onboarding.contract_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_onboarding_contract_events_occurred_on ON onboarding.contract_events(occurred_on);

-- Recruitment indexes
CREATE INDEX IF NOT EXISTS idx_recruitment_candidates_skills ON recruitment.candidates USING GIN(skills);
CREATE INDEX IF NOT EXISTS idx_recruitment_jobs_required_skills ON recruitment.jobs USING GIN(required_skills);
CREATE INDEX IF NOT EXISTS idx_recruitment_jobs_partner_id ON recruitment.jobs(partner_id);
CREATE INDEX IF NOT EXISTS idx_recruitment_applications_job_id ON recruitment.applications(job_id);
CREATE INDEX IF NOT EXISTS idx_recruitment_applications_candidate_id ON recruitment.applications(candidate_id);

-- Campaign Management indexes
CREATE INDEX IF NOT EXISTS idx_campaign_mgmt_campaigns_partner_id ON campaign_management.campaigns(partner_id);
CREATE INDEX IF NOT EXISTS idx_campaign_mgmt_campaigns_status ON campaign_management.campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaign_mgmt_campaign_events_aggregate_id ON campaign_management.campaign_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_campaign_mgmt_ad_groups_campaign_id ON campaign_management.ad_groups(campaign_id);

-- Integration indexes
CREATE INDEX IF NOT EXISTS idx_integration_outbox_status ON integration_events_outbox(status);
CREATE INDEX IF NOT EXISTS idx_integration_outbox_created_at ON integration_events_outbox(created_at);

-- ==============================================
-- TRIGGERS FOR UPDATED_AT
-- ==============================================

-- Apply updated_at triggers to new tables
CREATE TRIGGER update_onboarding_contracts_updated_at BEFORE UPDATE ON onboarding.contracts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recruitment_candidates_updated_at BEFORE UPDATE ON recruitment.candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recruitment_jobs_updated_at BEFORE UPDATE ON recruitment.jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_mgmt_campaigns_updated_at BEFORE UPDATE ON campaign_management.campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_mgmt_ad_groups_updated_at BEFORE UPDATE ON campaign_management.ad_groups
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ==============================================
-- GRANT PERMISSIONS
-- ==============================================

-- Grant permissions for all schemas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA onboarding TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA onboarding TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA recruitment TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA recruitment TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA campaign_management TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA campaign_management TO hexabuilders_user;
GRANT USAGE ON SCHEMA onboarding TO hexabuilders_user;
GRANT USAGE ON SCHEMA recruitment TO hexabuilders_user;
GRANT USAGE ON SCHEMA campaign_management TO hexabuilders_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'HexaBuilders Microservices PostgreSQL database initialized successfully!';
    RAISE NOTICE 'Schemas created: public (Partner Management), onboarding, recruitment, campaign_management';
    RAISE NOTICE 'All tables, indexes, triggers, and permissions configured.';
    RAISE NOTICE 'Ready for microservices enterprise operations.';
END $$;