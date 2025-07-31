#!/bin/bash

# Relate.io Deployment Script
# This script sets up and deploys the complete Relate.io system

set -e

echo "🚀 Starting Relate.io Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p logs

# Set up environment variables
print_status "Setting up environment variables..."
if [ ! -f backend/.env ]; then
    print_warning ".env file not found. Creating from template..."
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://relate_user:relate_password@postgres:5432/relate_db
POSTGRES_DB=relate_db
POSTGRES_USER=relate_user
POSTGRES_PASSWORD=relate_password

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@relate.io

# JWT Configuration
JWT_SECRET=your_jwt_secret_here_change_in_production

# Application Configuration
DEBUG=false
ENVIRONMENT=production

# External Integrations
MOMENTUM_API_KEY=your_momentum_api_key_here
MOMENTUM_API_URL=https://api.momentum.co.za

# AI Configuration
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
MAX_TOKENS=2000

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
EOF
    print_warning "Please update the .env file with your actual API keys and configuration!"
fi

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend
if [ ! -d "relate_venv" ]; then
    python3 -m venv relate_venv
fi
source relate_venv/bin/activate
pip install -r requirements.txt
cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build Docker images
print_status "Building Docker images..."
docker-compose build

# Start the services
print_status "Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service health..."
if docker-compose ps | grep -q "Up"; then
    print_success "Services are running!"
else
    print_error "Some services failed to start. Check logs with: docker-compose logs"
    exit 1
fi

# Run database migrations
print_status "Running database migrations..."
docker-compose exec backend python -c "
from enhanced_database import create_enhanced_tables, migrate_existing_data
create_enhanced_tables()
migrate_existing_data()
print('Database setup complete!')
"

# Create sample data (optional)
read -p "Do you want to create sample data? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Creating sample data..."
    docker-compose exec backend python -c "
import json
from enhanced_database import get_db_connection
from datetime import datetime

conn = get_db_connection()
try:
    with conn:
        with conn.cursor() as cur:
            # Create sample organization
            cur.execute('''
                INSERT INTO organizations (name, domain, branding_config, ai_tone_settings, compliance_rules)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (
                'Demo Financial Advisors',
                'demo.relate.io',
                json.dumps({'primary_color': '#1f2937', 'logo_url': '/logo.png'}),
                json.dumps({'tone': 'professional', 'formality': 'formal'}),
                json.dumps({'require_compliance_review': True})
            ))
            org_id = cur.fetchone()['id']
            
            # Create sample advisor
            cur.execute('''
                INSERT INTO advisors (organization_id, email, name, role, client_capacity, specializations)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            ''', (
                org_id,
                'advisor@demo.relate.io',
                'Demo Advisor',
                'Senior Financial Advisor',
                100,
                json.dumps(['retirement_planning', 'investment_management'])
            ))
            advisor_id = cur.fetchone()['id']
            
            # Create sample clients
            sample_clients = [
                ('John Smith', 'john.smith@email.com', '+1234567890', 'moderate'),
                ('Jane Doe', 'jane.doe@email.com', '+1234567891', 'conservative'),
                ('Bob Johnson', 'bob.johnson@email.com', '+1234567892', 'aggressive')
            ]
            
            for name, email, phone, risk_tolerance in sample_clients:
                cur.execute('''
                    INSERT INTO enhanced_clients (
                        advisor_id, name, email, phone, risk_tolerance,
                        investment_goals, communication_preferences, onboarding_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (
                    advisor_id, name, email, phone, risk_tolerance,
                    json.dumps(['retirement', 'wealth_building']),
                    json.dumps({'frequency': 'monthly', 'channel': 'email'}),
                    datetime.now()
                ))
            
            print('Sample data created successfully!')
finally:
    conn.close()
"
fi

# Display service URLs
print_success "Deployment completed successfully!"
echo
echo "🌐 Service URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo
echo "📋 Useful Commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Access backend shell: docker-compose exec backend bash"
echo "   Access database: docker-compose exec postgres psql -U relate_user -d relate_db"
echo
echo "⚠️  Important Notes:"
echo "   1. Update backend/.env with your actual API keys"
echo "   2. Configure your domain and SSL certificates for production"
echo "   3. Set up proper backup procedures for the database"
echo "   4. Monitor logs regularly: docker-compose logs -f"
echo
print_success "Relate.io is now running! 🎉"
