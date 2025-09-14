#!/bin/bash

# Migration script to separate databases from schema separation
# This script migrates from single database with schemas to separate database instances

set -e

echo "🔄 Starting migration from schema separation to separate databases..."

# Configuration
SOURCE_DB="postgresql://hexabuilders_user:hexabuilders_password@localhost:5432/hexabuilders"
TARGET_DBS=(
    "postgresql://partner_user:partner_secure_password@localhost:5433/partner_management"
    "postgresql://onboarding_user:onboarding_secure_password@localhost:5434/onboarding"
    "postgresql://recruitment_user:recruitment_secure_password@localhost:5435/recruitment"
    "postgresql://campaign_user:campaign_secure_password@localhost:5436/campaign_management"
)

# Create target databases
echo "📦 Creating target databases..."

# Partner Management
psql -c "CREATE DATABASE partner_management;" postgresql://postgres@localhost:5432/postgres || echo "Database already exists"
psql -c "CREATE USER partner_user WITH ENCRYPTED PASSWORD 'partner_secure_password';" postgresql://postgres@localhost:5432/postgres || echo "User already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE partner_management TO partner_user;" postgresql://postgres@localhost:5432/postgres

# Onboarding
psql -c "CREATE DATABASE onboarding;" postgresql://postgres@localhost:5432/postgres || echo "Database already exists"
psql -c "CREATE USER onboarding_user WITH ENCRYPTED PASSWORD 'onboarding_secure_password';" postgresql://postgres@localhost:5432/postgres || echo "User already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE onboarding TO onboarding_user;" postgresql://postgres@localhost:5432/postgres

# Recruitment
psql -c "CREATE DATABASE recruitment;" postgresql://postgres@localhost:5432/postgres || echo "Database already exists"
psql -c "CREATE USER recruitment_user WITH ENCRYPTED PASSWORD 'recruitment_secure_password';" postgresql://postgres@localhost:5432/postgres || echo "User already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE recruitment TO recruitment_user;" postgresql://postgres@localhost:5432/postgres

# Campaign Management
psql -c "CREATE DATABASE campaign_management;" postgresql://postgres@localhost:5432/postgres || echo "Database already exists"
psql -c "CREATE USER campaign_user WITH ENCRYPTED PASSWORD 'campaign_secure_password';" postgresql://postgres@localhost:5432/postgres || echo "User already exists"
psql -c "GRANT ALL PRIVILEGES ON DATABASE campaign_management TO campaign_user;" postgresql://postgres@localhost:5432/postgres

# Initialize target databases
echo "🏗️ Initializing target databases..."

psql -f sql/partner_management_init.sql $SOURCE_DB
psql -f sql/onboarding_init.sql $SOURCE_DB
psql -f sql/recruitment_init.sql $SOURCE_DB
psql -f sql/campaign_management_init.sql $SOURCE_DB

# Migrate data
echo "📊 Migrating data..."

# Partner Management data (public schema)
echo "Migrating Partner Management data..."
psql -c "INSERT INTO partners SELECT * FROM $SOURCE_DB.partners;" postgresql://partner_user:partner_secure_password@localhost:5432/partner_management
psql -c "INSERT INTO campaigns SELECT * FROM $SOURCE_DB.campaigns;" postgresql://partner_user:partner_secure_password@localhost:5432/partner_management
psql -c "INSERT INTO commissions SELECT * FROM $SOURCE_DB.commissions;" postgresql://partner_user:partner_secure_password@localhost:5432/partner_management
psql -c "INSERT INTO analytics_reports SELECT * FROM $SOURCE_DB.analytics_reports;" postgresql://partner_user:partner_secure_password@localhost:5432/partner_management
psql -c "INSERT INTO domain_events SELECT * FROM $SOURCE_DB.domain_events;" postgresql://partner_user:partner_secure_password@localhost:5432/partner_management

# Onboarding data
echo "Migrating Onboarding data..."
psql -c "INSERT INTO contracts SELECT * FROM $SOURCE_DB.onboarding.contracts;" postgresql://onboarding_user:onboarding_secure_password@localhost:5432/onboarding
psql -c "INSERT INTO contract_events SELECT * FROM $SOURCE_DB.onboarding.contract_events;" postgresql://onboarding_user:onboarding_secure_password@localhost:5432/onboarding

# Recruitment data
echo "Migrating Recruitment data..."
psql -c "INSERT INTO candidates SELECT * FROM $SOURCE_DB.recruitment.candidates;" postgresql://recruitment_user:recruitment_secure_password@localhost:5432/recruitment
psql -c "INSERT INTO jobs SELECT * FROM $SOURCE_DB.recruitment.jobs;" postgresql://recruitment_user:recruitment_secure_password@localhost:5432/recruitment
psql -c "INSERT INTO applications SELECT * FROM $SOURCE_DB.recruitment.applications;" postgresql://recruitment_user:recruitment_secure_password@localhost:5432/recruitment

# Campaign Management data
echo "Migrating Campaign Management data..."
psql -c "INSERT INTO campaigns SELECT * FROM $SOURCE_DB.campaign_management.campaigns;" postgresql://campaign_user:campaign_secure_password@localhost:5432/campaign_management
psql -c "INSERT INTO campaign_events SELECT * FROM $SOURCE_DB.campaign_management.campaign_events;" postgresql://campaign_user:campaign_secure_password@localhost:5432/campaign_management
psql -c "INSERT INTO ad_groups SELECT * FROM $SOURCE_DB.campaign_management.ad_groups;" postgresql://campaign_user:campaign_secure_password@localhost:5432/campaign_management

echo "✅ Migration completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update service configurations to use new database URLs"
echo "2. Test each service with its new database"
echo "3. Update Kubernetes deployments with new secrets"
echo "4. Deploy to production with separate database instances"
