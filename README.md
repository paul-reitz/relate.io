# Relate.io - AI-Powered Financial Advisor Relationship Management System

Relate.io is a comprehensive relationship management platform designed specifically for financial advisors to better manage client relationships, automate personalized communications, and gain insights through advanced AI analytics.

## 🚀 Features

### Core Functionality
- **Client Relationship Management**: Comprehensive client profiles with investment goals, risk tolerance, and communication preferences
- **AI-Powered Personalization**: Generate personalized portfolio updates and communications using advanced AI
- **Portfolio Integration**: Seamless integration with portfolio management systems (Momentum, etc.)
- **Sentiment Analysis**: Advanced NLP analysis of client feedback with topic extraction and urgency detection
- **Real-time Analytics**: Live dashboard with sentiment trends, portfolio performance, and client insights
- **Automated Communications**: Scheduled email updates with personalized content
- **Multi-tenant Architecture**: Support for multiple financial advisory organizations

### Advanced Features
- **WebSocket Real-time Updates**: Live notifications for feedback, portfolio changes, and alerts
- **Advanced AI Insights**: Portfolio risk analysis, market context integration, and predictive analytics
- **Bulk Operations**: Generate updates for multiple clients simultaneously
- **Integration Management**: Extensible system for connecting with external financial platforms
- **Compliance & Branding**: Organization-specific branding and compliance rule enforcement
- **Scalable Architecture**: Microservices-based design with Docker containerization

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Robust relational database with JSON support
- **Redis**: In-memory data structure store for caching and message queuing
- **Celery**: Distributed task queue for background processing
- **LangChain**: AI framework for building language model applications
- **OpenAI GPT-4**: Advanced language model for content generation
- **FinBERT**: Financial sentiment analysis model
- **WebSockets**: Real-time bidirectional communication

**Frontend:**
- **Next.js 14**: React framework with server-side rendering
- **TypeScript**: Type-safe JavaScript development
- **Tailwind CSS**: Utility-first CSS framework
- **React Query**: Data fetching and state management
- **Chart.js**: Interactive data visualization
- **WebSocket Client**: Real-time updates

**Infrastructure:**
- **Docker**: Containerization platform
- **Docker Compose**: Multi-container application orchestration
- **Nginx**: Reverse proxy and load balancer (production)
- **SendGrid**: Email delivery service

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Engine     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (LangChain)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │   OpenAI API    │
         │              │   (Database)    │    │   (GPT-4)       │
         │              └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Redis         │
│   (Real-time)   │    │   (Cache/Queue) │
└─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         └─────────────►│   Celery        │
                        │   (Background)  │
                        └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Node.js 18+
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd relate-io
```

### 2. Run the Deployment Script

```bash
./deploy.sh
```

This script will:
- Set up environment variables
- Install dependencies
- Build Docker images
- Start all services
- Run database migrations
- Optionally create sample data

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Manual Setup

If you prefer to set up manually:

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv relate_venv
source relate_venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
uvicorn enhanced_app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up postgres redis -d

# Run migrations
python backend/enhanced_database.py
```

## 📋 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://relate_user:relate_password@localhost:5432/relate_db
POSTGRES_DB=relate_db
POSTGRES_USER=relate_user
POSTGRES_PASSWORD=relate_password

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=noreply@relate.io

# JWT Configuration
JWT_SECRET=your_jwt_secret_here

# External Integrations
MOMENTUM_API_KEY=your_momentum_api_key_here
MOMENTUM_API_URL=https://api.momentum.co.za

# AI Configuration
AI_MODEL=gpt-4
AI_TEMPERATURE=0.7
MAX_TOKENS=2000
```

## 🔌 API Documentation

### Key Endpoints

#### Client Management
- `GET /api/v1/clients` - List all clients with enhanced data
- `POST /api/v1/clients` - Create a new client
- `GET /api/v1/portfolios/{client_id}` - Get portfolio details

#### AI-Powered Features
- `POST /api/v1/ai/personalized-content` - Generate personalized content
- `POST /api/v1/ai/generate-insights/{portfolio_id}` - Generate portfolio insights

#### Analytics
- `GET /api/v1/analytics/sentiment-trends` - Get sentiment analysis trends
- `POST /api/v1/feedback/advanced` - Submit feedback with AI analysis

#### Integrations
- `POST /api/v1/integrations/momentum/sync` - Sync with Momentum
- `GET /api/v1/integrations/status` - Get integration status

#### Bulk Operations
- `POST /api/v1/bulk/generate-updates` - Generate bulk client updates

### WebSocket Endpoints

- `ws://localhost:8000/ws/{advisor_id}` - Real-time updates for advisors

## 🎯 Usage Examples

### Creating a Client

```python
import requests

client_data = {
    "name": "John Smith",
    "email": "john.smith@email.com",
    "phone": "+1234567890",
    "risk_tolerance": "moderate",
    "investment_goals": ["retirement", "wealth_building"],
    "communication_preferences": {
        "frequency": "monthly",
        "channel": "email"
    }
}

response = requests.post(
    "http://localhost:8000/api/v1/clients",
    json=client_data,
    headers={"Authorization": "Bearer your_token"}
)
```

### Generating Personalized Content

```python
content_request = {
    "client_id": 1,
    "content_type": "portfolio_update"
}

response = requests.post(
    "http://localhost:8000/api/v1/ai/personalized-content",
    json=content_request,
    headers={"Authorization": "Bearer your_token"}
)
```

### Submitting Feedback

```python
feedback_data = {
    "client_id": 1,
    "text": "I'm concerned about the recent market volatility and how it affects my retirement portfolio."
}

response = requests.post(
    "http://localhost:8000/api/v1/feedback/advanced",
    json=feedback_data
)
```

## 🔄 Integration Guide

### Adding New Portfolio Management Systems

1. Create a new integration class in `integration_manager.py`:

```python
class NewPMSIntegration(BaseIntegration):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url
    
    async def fetch_portfolios(self, advisor_id: int):
        # Implementation here
        pass
```

2. Register the integration:

```python
integration_manager.register_integration('new_pms', NewPMSIntegration)
```

3. Add configuration to environment variables

### Custom AI Models

To use custom AI models, modify the `enhanced_ai.py` file:

```python
class CustomAIEngine(AIEngine):
    def __init__(self):
        # Initialize your custom model
        pass
    
    async def generate_content(self, prompt: str) -> str:
        # Custom implementation
        pass
```

## 📊 Monitoring and Logging

### Application Logs

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Monitoring

```bash
# Access PostgreSQL
docker-compose exec postgres psql -U relate_user -d relate_db

# View active connections
SELECT * FROM pg_stat_activity;

# View table sizes
SELECT schemaname,tablename,pg_size_pretty(size) as size
FROM (
    SELECT schemaname,tablename,pg_relation_size(schemaname||'.'||tablename) as size
    FROM pg_tables WHERE schemaname NOT IN ('information_schema','pg_catalog')
) s ORDER BY size DESC;
```

### Performance Monitoring

Key metrics to monitor:
- API response times
- Database query performance
- Redis memory usage
- Celery task queue length
- WebSocket connection count

## 🚀 Production Deployment

### Docker Production Setup

1. Update `docker-compose.prod.yml`:

```yaml
version: '3.8'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - backend
      - frontend

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - DEBUG=false
      - ENVIRONMENT=production
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
    environment:
      - NODE_ENV=production
```

2. Set up SSL certificates
3. Configure domain and DNS
4. Set up monitoring and alerting
5. Configure backup procedures

### Security Considerations

- Use strong JWT secrets
- Enable HTTPS in production
- Implement rate limiting
- Set up proper CORS policies
- Use environment-specific API keys
- Enable database encryption
- Implement audit logging

## 🧪 Testing

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### API Testing

Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs: `docker-compose logs -f`

## 🔄 Changelog

### Version 2.0.0
- Enhanced AI-powered insights
- Real-time WebSocket updates
- Advanced sentiment analysis
- Multi-tenant architecture
- Improved integration framework
- Comprehensive analytics dashboard

### Version 1.0.0
- Initial release
- Basic client management
- Portfolio integration
- Email automation
- Simple feedback system

---

**Relate.io** - Empowering Financial Advisors with AI-Driven Relationship Management
