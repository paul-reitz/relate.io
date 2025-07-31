# 🚀 Quick Start Guide - Running Relate.io

## Prerequisites Check

Before starting, make sure you have:
- Docker and Docker Compose installed
- Python 3.9+ 
- Node.js 18+
- Git

## Option 1: Automated Deployment (Recommended)

### Step 1: Navigate to the project directory
```bash
cd relate-io
```

### Step 2: Run the automated deployment script
```bash
./deploy.sh
```

This will:
- Set up environment variables
- Install all dependencies
- Build Docker images
- Start all services
- Create database tables
- Optionally create sample data

### Step 3: Access the application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Option 2: Manual Setup (Development)

### Step 1: Set up the Backend

```bash
cd relate-io/backend

# Create and activate virtual environment
python3 -m venv relate_venv
source relate_venv/bin/activate  # On Windows: relate_venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env  # If .env.example exists, or create manually
```

Create `.env` file with:
```env
DATABASE_URL=postgresql://relate_user:relate_password@localhost:5432/relate_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your_openai_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
JWT_SECRET=your_jwt_secret_here
```

### Step 2: Start Database Services

```bash
# From relate-io directory
docker-compose up postgres redis -d
```

### Step 3: Initialize Database

```bash
cd backend
python enhanced_database.py
```

### Step 4: Start Backend Server

```bash
# Make sure you're in backend directory with venv activated
uvicorn enhanced_app:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Set up Frontend

Open a new terminal:
```bash
cd relate-io/frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

## 🧪 Testing the Application

### 1. Access the Dashboard
- Open http://localhost:3000 in your browser
- You should see the Enhanced Dashboard

### 2. Test API Endpoints
- Visit http://localhost:8000/docs for interactive API documentation
- Try the following endpoints:

#### Create a Client
```bash
curl -X POST "http://localhost:8000/api/v1/clients" \
  -H "Authorization: Bearer mock-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Client",
    "email": "test@example.com",
    "phone": "+1234567890",
    "risk_tolerance": "moderate",
    "investment_goals": ["retirement"],
    "communication_preferences": {"frequency": "monthly"}
  }'
```

#### Get Clients List
```bash
curl -X GET "http://localhost:8000/api/v1/clients" \
  -H "Authorization: Bearer mock-token"
```

#### Submit Feedback
```bash
curl -X POST "http://localhost:8000/api/v1/feedback/advanced" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "text": "I am concerned about market volatility"
  }'
```

### 3. Test Real-time Features
- Open the dashboard in two browser windows
- Submit feedback in one window
- Watch for real-time updates in the other window

### 4. Test AI Features
- Generate personalized content:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/personalized-content" \
  -H "Authorization: Bearer mock-token" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "content_type": "portfolio_update"
  }'
```

## 🔧 Troubleshooting

### Common Issues:

1. **Port already in use**
   ```bash
   # Kill processes on ports
   sudo lsof -ti:3000 | xargs kill -9
   sudo lsof -ti:8000 | xargs kill -9
   ```

2. **Database connection issues**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Frontend build issues**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python dependency issues**
   ```bash
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

## 📊 Monitoring

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Check Service Status
```bash
docker-compose ps
```

### Access Database
```bash
docker-compose exec postgres psql -U relate_user -d relate_db
```

## 🎯 What to Test

1. **Dashboard Features**:
   - Client cards display
   - Sentiment charts
   - Portfolio modals
   - Real-time updates

2. **API Functionality**:
   - Client CRUD operations
   - AI content generation
   - Feedback submission
   - Analytics endpoints

3. **Integration Features**:
   - Portfolio sync
   - Market data updates
   - Bulk operations

4. **Real-time Features**:
   - WebSocket connections
   - Live notifications
   - Dashboard updates

## 🚨 Important Notes

- The system uses mock authentication (`Bearer mock-token`)
- OpenAI API key is required for AI features
- Sample data can be created via the deployment script
- All services run in Docker containers for consistency

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Frontend loads at http://localhost:3000
- ✅ API docs accessible at http://localhost:8000/docs
- ✅ Dashboard shows client data
- ✅ Charts render properly
- ✅ API endpoints respond correctly
- ✅ Real-time updates work
- ✅ No errors in browser console or server logs
