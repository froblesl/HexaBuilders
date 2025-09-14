-- Recruitment Service Database Initialization
-- Separate database instance for production

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Candidates table
CREATE TABLE IF NOT EXISTS candidates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    telefono VARCHAR(50),
    direccion TEXT,
    ciudad VARCHAR(100),
    pais VARCHAR(100),
    fecha_nacimiento DATE,
    genero VARCHAR(20) CHECK (genero IN ('MASCULINO', 'FEMENINO', 'OTRO', 'PREFIERO_NO_DECIR')),
    estado_civil VARCHAR(20) CHECK (estado_civil IN ('SOLTERO', 'CASADO', 'DIVORCIADO', 'VIUDO', 'OTRO')),
    nivel_educacion VARCHAR(50) CHECK (nivel_educacion IN ('SECUNDARIA', 'TECNICO', 'UNIVERSITARIO', 'POSGRADO', 'DOCTORADO')),
    experiencia_anos INTEGER DEFAULT 0,
    salario_esperado DECIMAL(12,2),
    disponibilidad VARCHAR(50) CHECK (disponibilidad IN ('INMEDIATA', 'DOS_SEMANAS', 'UN_MES', 'NEGOCIABLE')),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVO' CHECK (status IN ('ACTIVO', 'INACTIVO', 'CONTRATADO', 'DESCARTADO')),
    linkedin_url VARCHAR(500),
    github_url VARCHAR(500),
    portfolio_url VARCHAR(500),
    cv_file_path VARCHAR(500),
    skills_json JSONB,
    languages_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Jobs table
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT NOT NULL,
    empresa VARCHAR(255) NOT NULL,
    ubicacion VARCHAR(255),
    tipo_empleo VARCHAR(50) CHECK (tipo_empleo IN ('TIEMPO_COMPLETO', 'TIEMPO_PARCIAL', 'FREELANCE', 'CONTRATO', 'PRACTICAS')),
    modalidad VARCHAR(50) CHECK (modalidad IN ('PRESENCIAL', 'REMOTO', 'HIBRIDO')),
    salario_min DECIMAL(12,2),
    salario_max DECIMAL(12,2),
    moneda VARCHAR(3) DEFAULT 'COP',
    experiencia_requerida INTEGER DEFAULT 0,
    nivel_educacion_requerido VARCHAR(50),
    skills_requeridas_json JSONB,
    beneficios_json JSONB,
    fecha_publicacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cierre TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVO' CHECK (status IN ('ACTIVO', 'PAUSADO', 'CERRADO', 'CANCELADO')),
    vacantes_disponibles INTEGER DEFAULT 1,
    contacto_email VARCHAR(254),
    contacto_telefono VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id),
    job_id UUID NOT NULL REFERENCES jobs(id),
    status VARCHAR(50) NOT NULL DEFAULT 'POSTULADO' CHECK (status IN ('POSTULADO', 'EN_REVISION', 'ENTREVISTA', 'PRUEBA_TECNICA', 'OFERTA', 'CONTRATADO', 'RECHAZADO', 'RETIRADO')),
    fecha_postulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cover_letter TEXT,
    notas_reclutador TEXT,
    puntuacion INTEGER CHECK (puntuacion >= 0 AND puntuacion <= 100),
    salario_ofrecido DECIMAL(12,2),
    fecha_entrevista TIMESTAMP,
    resultado_entrevista TEXT,
    resultado_prueba_tecnica TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(candidate_id, job_id)
);

-- Interviews table
CREATE TABLE IF NOT EXISTS interviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    application_id UUID NOT NULL REFERENCES applications(id),
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('TELEFONICA', 'VIDEO', 'PRESENCIAL', 'TECNICA', 'PANEL')),
    fecha_programada TIMESTAMP NOT NULL,
    duracion_minutos INTEGER DEFAULT 60,
    entrevistador_nombre VARCHAR(255),
    entrevistador_email VARCHAR(254),
    modalidad VARCHAR(50) CHECK (modalidad IN ('PRESENCIAL', 'REMOTO')),
    ubicacion TEXT,
    link_reunion VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'PROGRAMADA' CHECK (status IN ('PROGRAMADA', 'CONFIRMADA', 'COMPLETADA', 'CANCELADA', 'REPROGRAMADA')),
    notas_previas TEXT,
    notas_entrevista TEXT,
    puntuacion INTEGER CHECK (puntuacion >= 0 AND puntuacion <= 100),
    recomendacion VARCHAR(50) CHECK (recomendacion IN ('CONTRATAR', 'SEGUNDA_ENTREVISTA', 'RECHAZAR', 'PENDIENTE')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Matching scores table (for AI-based matching)
CREATE TABLE IF NOT EXISTS matching_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    candidate_id UUID NOT NULL REFERENCES candidates(id),
    job_id UUID NOT NULL REFERENCES jobs(id),
    score DECIMAL(3,2) NOT NULL CHECK (score >= 0.0 AND score <= 1.0),
    factors_json JSONB, -- Skills match, experience, location, etc.
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    algorithm_version VARCHAR(50) DEFAULT '1.0',
    UNIQUE(candidate_id, job_id)
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
CREATE INDEX IF NOT EXISTS idx_candidates_email ON candidates(email);
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_skills ON candidates USING GIN(skills_json);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_tipo_empleo ON jobs(tipo_empleo);
CREATE INDEX IF NOT EXISTS idx_jobs_modalidad ON jobs(modalidad);
CREATE INDEX IF NOT EXISTS idx_jobs_skills ON jobs USING GIN(skills_requeridas_json);
CREATE INDEX IF NOT EXISTS idx_applications_candidate_id ON applications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_applications_job_id ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);
CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews(application_id);
CREATE INDEX IF NOT EXISTS idx_interviews_fecha_programada ON interviews(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_matching_scores_candidate_id ON matching_scores(candidate_id);
CREATE INDEX IF NOT EXISTS idx_matching_scores_job_id ON matching_scores(job_id);
CREATE INDEX IF NOT EXISTS idx_matching_scores_score ON matching_scores(score);
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
CREATE TRIGGER update_candidates_updated_at BEFORE UPDATE ON candidates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_applications_updated_at BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_interviews_updated_at BEFORE UPDATE ON interviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO recruitment_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO recruitment_user;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Recruitment database initialized successfully!';
END $$;
