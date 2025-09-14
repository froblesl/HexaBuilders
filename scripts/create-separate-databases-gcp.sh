#!/bin/bash

# Script to create separate Cloud SQL instances for each microservice
# Usage: ./create-separate-databases-gcp.sh PROJECT_ID REGION

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 PROJECT_ID REGION"
    echo "Example: $0 my-hexabuilders-project us-central1"
    exit 1
fi

PROJECT_ID=$1
REGION=$2

echo "🚀 Creating separate Cloud SQL instances for HexaBuilders microservices..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable sqladmin.googleapis.com
gcloud services enable sql-component.googleapis.com

# Create Partner Management database
echo "📊 Creating Partner Management database instance..."
gcloud sql instances create partner-db-instance \
    --database-version=POSTGRES_15 \
    --tier=db-standard-1 \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --authorized-networks=0.0.0.0/0 \
    --labels=service=partner-management,environment=production

# Create Onboarding database
echo "📊 Creating Onboarding database instance..."
gcloud sql instances create onboarding-db-instance \
    --database-version=POSTGRES_15 \
    --tier=db-standard-1 \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --authorized-networks=0.0.0.0/0 \
    --labels=service=onboarding,environment=production

# Create Recruitment database
echo "📊 Creating Recruitment database instance..."
gcloud sql instances create recruitment-db-instance \
    --database-version=POSTGRES_15 \
    --tier=db-standard-1 \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --authorized-networks=0.0.0.0/0 \
    --labels=service=recruitment,environment=production

# Create Campaign Management database
echo "📊 Creating Campaign Management database instance..."
gcloud sql instances create campaign-db-instance \
    --database-version=POSTGRES_15 \
    --tier=db-standard-1 \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --authorized-networks=0.0.0.0/0 \
    --labels=service=campaign-management,environment=production

# Wait for instances to be ready
echo "⏳ Waiting for instances to be ready..."
gcloud sql instances list --filter="name~db-instance"

# Create databases and users
echo "👤 Creating databases and users..."

# Partner Management
echo "Setting up Partner Management database..."
gcloud sql databases create partner_management --instance=partner-db-instance
gcloud sql users create partner_user --instance=partner-db-instance --password=partner_secure_password

# Onboarding
echo "Setting up Onboarding database..."
gcloud sql databases create onboarding --instance=onboarding-db-instance
gcloud sql users create onboarding_user --instance=onboarding-db-instance --password=onboarding_secure_password

# Recruitment
echo "Setting up Recruitment database..."
gcloud sql databases create recruitment --instance=recruitment-db-instance
gcloud sql users create recruitment_user --instance=recruitment-db-instance --password=recruitment_secure_password

# Campaign Management
echo "Setting up Campaign Management database..."
gcloud sql databases create campaign_management --instance=campaign-db-instance
gcloud sql users create campaign_user --instance=campaign-db-instance --password=campaign_secure_password

# Get connection information
echo "📋 Database connection information:"
echo ""
echo "Partner Management:"
echo "  Host: $(gcloud sql instances describe partner-db-instance --format='value(ipAddresses[0].ipAddress)')"
echo "  Database: partner_management"
echo "  User: partner_user"
echo "  Connection String: postgresql://partner_user:partner_secure_password@$(gcloud sql instances describe partner-db-instance --format='value(ipAddresses[0].ipAddress)'):5432/partner_management"
echo ""
echo "Onboarding:"
echo "  Host: $(gcloud sql instances describe onboarding-db-instance --format='value(ipAddresses[0].ipAddress)')"
echo "  Database: onboarding"
echo "  User: onboarding_user"
echo "  Connection String: postgresql://onboarding_user:onboarding_secure_password@$(gcloud sql instances describe onboarding-db-instance --format='value(ipAddresses[0].ipAddress)'):5432/onboarding"
echo ""
echo "Recruitment:"
echo "  Host: $(gcloud sql instances describe recruitment-db-instance --format='value(ipAddresses[0].ipAddress)')"
echo "  Database: recruitment"
echo "  User: recruitment_user"
echo "  Connection String: postgresql://recruitment_user:recruitment_secure_password@$(gcloud sql instances describe recruitment-db-instance --format='value(ipAddresses[0].ipAddress)'):5432/recruitment"
echo ""
echo "Campaign Management:"
echo "  Host: $(gcloud sql instances describe campaign-db-instance --format='value(ipAddresses[0].ipAddress)')"
echo "  Database: campaign_management"
echo "  User: campaign_user"
echo "  Connection String: postgresql://campaign_user:campaign_secure_password@$(gcloud sql instances describe campaign-db-instance --format='value(ipAddresses[0].ipAddress)'):5432/campaign_management"

echo ""
echo "✅ Separate database instances created successfully!"
echo ""
echo "Next steps:"
echo "1. Update Kubernetes secrets with the connection strings above"
echo "2. Initialize each database with the appropriate schema"
echo "3. Update service configurations to use new database URLs"
echo "4. Deploy updated services to Kubernetes"
