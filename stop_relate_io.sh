#!/bin/bash

# Relate.io Stop Script
# This script stops both the backend and frontend services

echo "🛑 Stopping Relate.io Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to the relate-io directory
cd "$(dirname "$0")"

# Function to kill processes on specific ports
kill_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Stopping process on port $1...${NC}"
        lsof -ti:$1 | xargs kill -9 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✅ Port $1 cleared${NC}"
    else
        echo -e "${BLUE}ℹ️  No process running on port $1${NC}"
    fi
}

# Kill processes by PID if available
if [ -f "logs/backend.pid" ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping backend process (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        sleep 2
        kill -9 $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    rm -f logs/backend.pid
fi

if [ -f "logs/frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend process (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2
        kill -9 $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    rm -f logs/frontend.pid
fi

# Kill any remaining processes on our ports
kill_port 8000
kill_port 3001

# Kill any remaining Node.js processes that might be Next.js
pkill -f "next dev" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true

echo -e "${GREEN}🎉 All Relate.io services stopped!${NC}"
