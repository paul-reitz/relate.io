#!/bin/bash

# Relate.io Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting Relate.io Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on specific ports
kill_port() {
    if check_port $1; then
        echo -e "${YELLOW}Killing existing process on port $1...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Change to the relate-io directory
cd "$(dirname "$0")"

echo -e "${BLUE}📍 Working directory: $(pwd)${NC}"

# Check if Ollama is running
echo -e "${BLUE}🔍 Checking Ollama service...${NC}"
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo -e "${RED}❌ Ollama is not running. Please start Ollama first:${NC}"
    echo -e "${YELLOW}   ollama serve${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Ollama is running${NC}"
fi

# Check if TinyLlama model is available
echo -e "${BLUE}🔍 Checking TinyLlama model...${NC}"
if ! ollama list | grep -q "tinyllama"; then
    echo -e "${YELLOW}⚠️  TinyLlama model not found. Pulling it now...${NC}"
    ollama pull tinyllama:latest
fi
echo -e "${GREEN}✅ TinyLlama model is available${NC}"

# Kill existing processes on our ports
kill_port 8000
kill_port 3001

# Start PostgreSQL if not running
echo -e "${BLUE}🔍 Checking PostgreSQL...${NC}"
if ! pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL not running. Attempting to start...${NC}"
    # Try different ways to start PostgreSQL
    if command -v brew >/dev/null 2>&1; then
        brew services start postgresql@14 2>/dev/null || brew services start postgresql 2>/dev/null || true
    elif command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start postgresql 2>/dev/null || true
    fi
    sleep 3
fi

# Start Redis if not running
echo -e "${BLUE}🔍 Checking Redis...${NC}"
if ! redis-cli ping >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis not running. Attempting to start...${NC}"
    if command -v brew >/dev/null 2>&1; then
        brew services start redis 2>/dev/null || true
    elif command -v systemctl >/dev/null 2>&1; then
        sudo systemctl start redis 2>/dev/null || true
    else
        redis-server --daemonize yes 2>/dev/null || true
    fi
    sleep 2
fi

# Initialize database
echo -e "${BLUE}🗄️  Initializing database...${NC}"
cd backend
source relate_venv/bin/activate
python enhanced_database.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Database initialized${NC}"
else
    echo -e "${RED}❌ Database initialization failed${NC}"
fi

# Start backend server in background
echo -e "${BLUE}🔧 Starting backend server...${NC}"
uvicorn simple_app:app --reload --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"

# Wait for backend to be ready
echo -e "${BLUE}⏳ Waiting for backend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Backend failed to start${NC}"
        exit 1
    fi
done

# Start frontend server in background
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
cd ../frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"

# Wait for frontend to be ready
echo -e "${BLUE}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:3001 >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Frontend failed to start${NC}"
        exit 1
    fi
done

# Create logs directory if it doesn't exist
mkdir -p ../logs

# Save PIDs for cleanup
echo $BACKEND_PID > ../logs/backend.pid
echo $FRONTEND_PID > ../logs/frontend.pid

echo ""
echo -e "${GREEN}🎉 Relate.io is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Dashboard:${NC} http://localhost:3001"
echo -e "${BLUE}🔧 API:${NC}       http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  tail -f logs/backend.log"
echo -e "   Frontend: tail -f logs/frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop services:${NC}"
echo -e "   ./stop_relate_io.sh"
echo ""

# Keep script running and monitor services
trap 'echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0' INT

echo -e "${BLUE}🔍 Monitoring services... (Press Ctrl+C to stop)${NC}"
while true; do
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Backend process died${NC}"
        break
    fi
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}❌ Frontend process died${NC}"
        break
    fi
    sleep 5
done
