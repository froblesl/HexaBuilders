-- HexaBuilders PostgreSQL Database Initialization
-- Enterprise Partner Management Platform

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

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

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hexabuilders_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hexabuilders_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'HexaBuilders PostgreSQL database initialized successfully!';
    RAISE NOTICE 'Tables created: partners, campaigns, commissions, analytics_reports, domain_events';
    RAISE NOTICE 'Sample data inserted and ready for enterprise operations.';
END $$;