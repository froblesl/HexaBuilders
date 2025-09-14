-- Campaign Management Service Database Initialization
-- Separate database instance for production

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Campaigns table
CREATE TABLE IF NOT EXISTS campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('MARKETING', 'VENTAS', 'PROMOCIONAL', 'BRAND', 'DIGITAL', 'TRADICIONAL')),
    status VARCHAR(50) NOT NULL DEFAULT 'BORRADOR' CHECK (status IN ('BORRADOR', 'ACTIVA', 'PAUSADA', 'COMPLETADA', 'CANCELADA', 'ARCHIVADA')),
    fecha_inicio TIMESTAMP NOT NULL,
    fecha_fin TIMESTAMP NOT NULL,
    presupuesto_total DECIMAL(15,2) NOT NULL DEFAULT 0.0,
    presupuesto_usado DECIMAL(15,2) DEFAULT 0.0,
    moneda VARCHAR(3) DEFAULT 'COP',
    objetivo_principal VARCHAR(100),
    metricas_objetivo_json JSONB,
    audiencia_objetivo_json JSONB,
    canales_json JSONB, -- Social media, email, ads, etc.
    partner_id UUID, -- Reference to partner (from partner-management service)
    manager_id UUID, -- Campaign manager
    created_by UUID NOT NULL,
    approved_by UUID,
    fecha_aprobacion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Budget allocations table
CREATE TABLE IF NOT EXISTS budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    categoria VARCHAR(100) NOT NULL, -- 'ADVERTISING', 'CONTENT', 'EVENTS', 'TOOLS', etc.
    subcategoria VARCHAR(100),
    monto_asignado DECIMAL(12,2) NOT NULL,
    monto_gastado DECIMAL(12,2) DEFAULT 0.0,
    descripcion TEXT,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ACTIVO' CHECK (status IN ('ACTIVO', 'AGOTADO', 'CANCELADO')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaign targeting configuration
CREATE TABLE IF NOT EXISTS targeting_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    tipo_targeting VARCHAR(50) NOT NULL CHECK (tipo_targeting IN ('DEMOGRAFICO', 'GEOGRAFICO', 'PSICOGRAFICO', 'BEHAVIORAL', 'LOOKALIKE')),
    parametros_json JSONB NOT NULL,
    prioridad INTEGER DEFAULT 1 CHECK (prioridad >= 1 AND prioridad <= 10),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    fecha_reporte DATE NOT NULL,
    impresiones INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversiones INTEGER DEFAULT 0,
    costo_total DECIMAL(12,2) DEFAULT 0.0,
    ctr DECIMAL(5,4) DEFAULT 0.0, -- Click-through rate
    cpc DECIMAL(8,2) DEFAULT 0.0, -- Cost per click
    cpa DECIMAL(8,2) DEFAULT 0.0, -- Cost per acquisition
    roi DECIMAL(8,2) DEFAULT 0.0, -- Return on investment
    reach INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4) DEFAULT 0.0,
    metricas_adicionales_json JSONB,
    fuente_datos VARCHAR(100), -- 'GOOGLE_ADS', 'FACEBOOK_ADS', 'INTERNAL', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, fecha_reporte, fuente_datos)
);

-- Campaign assets table (creatives, videos, images, etc.)
CREATE TABLE IF NOT EXISTS campaign_assets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    nombre VARCHAR(255) NOT NULL,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('IMAGEN', 'VIDEO', 'AUDIO', 'TEXTO', 'BANNER', 'LANDING_PAGE', 'EMAIL_TEMPLATE')),
    formato VARCHAR(50), -- 'JPG', 'MP4', 'HTML', etc.
    tamaño_bytes BIGINT,
    url_archivo VARCHAR(1000),
    url_preview VARCHAR(1000),
    dimensiones VARCHAR(50), -- '1920x1080', '300x250', etc.
    duracion_segundos INTEGER, -- For videos/audio
    descripcion TEXT,
    tags_json JSONB,
    status VARCHAR(50) DEFAULT 'ACTIVO' CHECK (status IN ('ACTIVO', 'ARCHIVADO', 'ELIMINADO')),
    uso_count INTEGER DEFAULT 0,
    created_by UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Campaign schedules table
CREATE TABLE IF NOT EXISTS campaign_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id),
    tipo_schedule VARCHAR(50) NOT NULL CHECK (tipo_schedule IN ('DIARIO', 'SEMANAL', 'MENSUAL', 'PERSONALIZADO')),
    dias_semana INTEGER[], -- Array of days (1=Monday, 7=Sunday)
    hora_inicio TIME,
    hora_fin TIME,
    timezone VARCHAR(50) DEFAULT 'America/Bogota',
    fechas_especiales_json JSONB, -- Holidays, special events, etc.
    activo BOOLEAN DEFAULT TRUE,
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
CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status);
CREATE INDEX IF NOT EXISTS idx_campaigns_tipo ON campaigns(tipo);
CREATE INDEX IF NOT EXISTS idx_campaigns_partner_id ON campaigns(partner_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_fecha_inicio ON campaigns(fecha_inicio);
CREATE INDEX IF NOT EXISTS idx_campaigns_fecha_fin ON campaigns(fecha_fin);
CREATE INDEX IF NOT EXISTS idx_budget_allocations_campaign_id ON budget_allocations(campaign_id);
CREATE INDEX IF NOT EXISTS idx_budget_allocations_categoria ON budget_allocations(categoria);
CREATE INDEX IF NOT EXISTS idx_targeting_configs_campaign_id ON targeting_configs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_targeting_configs_tipo ON targeting_configs(tipo_targeting);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_campaign_id ON performance_metrics(campaign_id);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_fecha ON performance_metrics(fecha_reporte);
CREATE INDEX IF NOT EXISTS idx_campaign_assets_campaign_id ON campaign_assets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_campaign_assets_tipo ON campaign_assets(tipo);
CREATE INDEX IF NOT EXISTS idx_campaign_schedules_campaign_id ON campaign_schedules(campaign_id);
CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate_id ON domain_events(aggregate_id);
CREATE INDEX IF NOT EXISTS idx_domain_events_aggregate_type ON domain_events(aggregate_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_event_type ON domain_events(event_type);
CREATE INDEX IF NOT EXISTS idx_domain_events_occurred_on ON domain_events(occurred_on);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_campaigns_updated_at BEFORE UPDATE ON campaigns
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_budget_allocations_updated_at BEFORE UPDATE ON budget_allocations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_targeting_configs_updated_at BEFORE UPDATE ON targeting_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_metrics_updated_at BEFORE UPDATE ON performance_metrics
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_assets_updated_at BEFORE UPDATE ON campaign_assets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_campaign_schedules_updated_at BEFORE UPDATE ON campaign_schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO campaign_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO campaign_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Campaign Management database initialized successfully!';
END $$;
