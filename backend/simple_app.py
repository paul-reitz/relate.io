from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import redis
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Relate.io API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="relate_io",
        user="postgres",
        password="password",
        cursor_factory=RealDictCursor
    )

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Pydantic models
class Client(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: Optional[str] = None
    risk_tolerance: str = "moderate"
    investment_goals: List[str] = []
    communication_preferences: Dict[str, Any] = {}
    created_at: Optional[datetime] = None

class Feedback(BaseModel):
    id: Optional[int] = None
    client_id: int
    text: str
    sentiment: Optional[str] = None
    topics: List[str] = []
    urgency: str = "low"
    created_at: Optional[datetime] = None

class Portfolio(BaseModel):
    id: Optional[int] = None
    client_id: int
    total_value: float
    holdings: List[Dict[str, Any]] = []
    performance: Dict[str, Any] = {}
    risk_score: float = 0.0

# Ollama TinyLlama integration
OLLAMA_BASE_URL = "http://localhost:11434"

def call_ollama(prompt: str, model: str = "tinyllama:latest") -> str:
    """Call Ollama API with TinyLlama model"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 500
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"Ollama API error: {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return ""

def analyze_sentiment_with_llama(text: str) -> Dict[str, Any]:
    """Analyze sentiment using TinyLlama"""
    prompt = f"""Analyze the sentiment and extract information from this client feedback:

"{text}"

Please respond in this exact JSON format:
{{
    "sentiment": "positive/negative/neutral",
    "topics": ["topic1", "topic2"],
    "urgency": "high/medium/low",
    "confidence": 0.8
}}

Focus on financial topics like investment, risk, portfolio, retirement, market concerns."""

    try:
        llama_response = call_ollama(prompt)
        
        # Try to extract JSON from the response
        if llama_response:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*\}', llama_response, re.DOTALL)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                    # Validate the structure
                    if all(key in result for key in ["sentiment", "topics", "urgency"]):
                        return result
                except json.JSONDecodeError:
                    pass
        
        # Fallback to keyword-based analysis if LLM fails
        return fallback_sentiment_analysis(text)
        
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return fallback_sentiment_analysis(text)

def fallback_sentiment_analysis(text: str) -> Dict[str, Any]:
    """Fallback sentiment analysis using keywords"""
    positive_words = ["good", "great", "excellent", "happy", "satisfied", "pleased"]
    negative_words = ["bad", "terrible", "awful", "unhappy", "concerned", "worried", "anxious"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
    elif negative_count > positive_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    topics = []
    if any(word in text_lower for word in ["market", "portfolio", "investment"]):
        topics.append("investment")
    if any(word in text_lower for word in ["risk", "volatility", "loss"]):
        topics.append("risk")
    if any(word in text_lower for word in ["retirement", "pension"]):
        topics.append("retirement")
    
    urgency = "high" if any(word in text_lower for word in ["urgent", "immediately", "asap", "worried", "concerned"]) else "low"
    
    return {
        "sentiment": sentiment,
        "topics": topics,
        "urgency": urgency,
        "confidence": 0.6
    }

def generate_content_with_llama(client_data: Dict[str, Any], content_type: str) -> str:
    """Generate personalized content using TinyLlama"""
    client_name = client_data.get("name", "Valued Client")
    risk_tolerance = client_data.get("risk_tolerance", "moderate")
    investment_goals = client_data.get("investment_goals", [])
    
    if content_type == "portfolio_update":
        prompt = f"""Write a professional, personalized portfolio update email for a financial advisor to send to their client.

Client Details:
- Name: {client_name}
- Risk Tolerance: {risk_tolerance}
- Investment Goals: {', '.join(investment_goals) if investment_goals else 'general wealth building'}

The email should:
- Be professional and reassuring
- Reference their specific risk tolerance
- Mention their investment goals
- Include general portfolio performance comments
- Invite them to schedule a meeting
- Be signed by "Your Financial Advisor"

Keep it concise and professional (200-300 words)."""

        llama_response = call_ollama(prompt)
        
        if llama_response and len(llama_response) > 50:
            return llama_response
        else:
            # Fallback to template
            return f"""Dear {client_name},

I hope this message finds you well. I wanted to provide you with a brief update on your investment portfolio.

Your portfolio has been performing steadily, and we continue to monitor market conditions closely. Based on your {risk_tolerance} risk tolerance, your current allocation remains well-positioned for your investment goals of {', '.join(investment_goals) if investment_goals else 'wealth building'}.

Key highlights:
- Portfolio remains aligned with your investment objectives
- Risk management strategies are in place
- Regular rebalancing ensures optimal allocation

Please don't hesitate to reach out if you have any questions or would like to schedule a review meeting.

Best regards,
Your Financial Advisor"""
    
    return f"Personalized content for {client_name}"

# API Routes
@app.get("/")
async def root():
    return {"message": "Relate.io API is running", "version": "1.0.0"}

@app.get("/api/v1/clients", response_model=List[Client])
async def get_clients():
    """Get all clients"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients ORDER BY created_at DESC")
        clients = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(client) for client in clients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/clients", response_model=Client)
async def create_client(client: Client):
    """Create a new client"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO clients (name, email, phone, risk_tolerance, investment_goals, communication_preferences)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            client.name,
            client.email,
            client.phone,
            client.risk_tolerance,
            json.dumps(client.investment_goals),
            json.dumps(client.communication_preferences)
        ))
        
        new_client = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return dict(new_client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/clients/{client_id}")
async def get_client(client_id: int):
    """Get a specific client"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client = cur.fetchone()
        cur.close()
        conn.close()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        return dict(client)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback/advanced")
async def submit_feedback(feedback: Feedback):
    """Submit feedback with AI analysis"""
    try:
        # Analyze feedback using TinyLlama
        analysis = analyze_sentiment_with_llama(feedback.text)
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO feedback (client_id, text, sentiment, topics, urgency)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """, (
            feedback.client_id,
            feedback.text,
            analysis["sentiment"],
            json.dumps(analysis["topics"]),
            analysis["urgency"]
        ))
        
        new_feedback = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "feedback": dict(new_feedback),
            "analysis": analysis
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/feedback")
async def get_feedback():
    """Get all feedback"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT f.*, c.name as client_name 
            FROM feedback f 
            JOIN clients c ON f.client_id = c.id 
            ORDER BY f.created_at DESC
        """)
        feedback_list = cur.fetchall()
        cur.close()
        conn.close()
        
        return [dict(feedback) for feedback in feedback_list]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai/personalized-content")
async def generate_personalized_content(request: Dict[str, Any]):
    """Generate personalized content"""
    try:
        client_id = request.get("client_id")
        content_type = request.get("content_type", "portfolio_update")
        
        # Get client data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client = cur.fetchone()
        cur.close()
        conn.close()
        
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Generate content using TinyLlama
        content = generate_content_with_llama(dict(client), content_type)
        
        return {
            "client_id": client_id,
            "content_type": content_type,
            "content": content,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/sentiment-trends")
async def get_sentiment_trends():
    """Get sentiment analysis trends"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get sentiment distribution
        cur.execute("""
            SELECT sentiment, COUNT(*) as count 
            FROM feedback 
            WHERE created_at >= NOW() - INTERVAL '30 days'
            GROUP BY sentiment
        """)
        sentiment_data = cur.fetchall()
        
        # Get recent feedback
        cur.execute("""
            SELECT f.*, c.name as client_name 
            FROM feedback f 
            JOIN clients c ON f.client_id = c.id 
            ORDER BY f.created_at DESC 
            LIMIT 10
        """)
        recent_feedback = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "sentiment_distribution": [dict(row) for row in sentiment_data],
            "recent_feedback": [dict(row) for row in recent_feedback],
            "total_clients": len(await get_clients()),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/portfolios/{client_id}")
async def get_portfolio(client_id: int):
    """Get portfolio for a client"""
    try:
        # Mock portfolio data
        portfolio_data = {
            "id": 1,
            "client_id": client_id,
            "total_value": 250000.00,
            "holdings": [
                {"symbol": "AAPL", "shares": 100, "value": 15000, "percentage": 6.0},
                {"symbol": "GOOGL", "shares": 50, "value": 12500, "percentage": 5.0},
                {"symbol": "MSFT", "shares": 75, "value": 22500, "percentage": 9.0},
                {"symbol": "TSLA", "shares": 25, "value": 5000, "percentage": 2.0},
                {"symbol": "SPY", "shares": 500, "value": 195000, "percentage": 78.0}
            ],
            "performance": {
                "ytd_return": 8.5,
                "monthly_return": 2.1,
                "total_return": 15.3
            },
            "risk_score": 6.5,
            "last_updated": datetime.now().isoformat()
        }
        
        return portfolio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        
        # Test Redis connection
        redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
