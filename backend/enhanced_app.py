from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Import enhanced modules
from enhanced_models import *
from enhanced_database import create_enhanced_tables, migrate_existing_data, get_db_connection
from enhanced_ai import ai_engine, generate_narrative, analyze_feedback
from integration_manager import integration_manager, sync_momentum_portfolios, bulk_portfolio_sync
from ingestion import import_clients_from_csv
from messaging import send_email_update
from tasks import app as celery_app

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Relate.io API",
    description="Enhanced Financial Advisor Relationship Management System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://relate.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.advisor_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, advisor_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        if advisor_id not in self.advisor_connections:
            self.advisor_connections[advisor_id] = []
        self.advisor_connections[advisor_id].append(websocket)

    def disconnect(self, websocket: WebSocket, advisor_id: int):
        self.active_connections.remove(websocket)
        if advisor_id in self.advisor_connections:
            self.advisor_connections[advisor_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_advisor(self, message: str, advisor_id: int):
        if advisor_id in self.advisor_connections:
            for connection in self.advisor_connections[advisor_id]:
                await connection.send_text(message)

manager = ConnectionManager()

# Create enhanced tables on startup
@app.on_event("startup")
async def startup_event():
    create_enhanced_tables()
    migrate_existing_data()
    logger.info("Enhanced Relate.io API started successfully")

# Authentication dependency (simplified - implement proper JWT in production)
async def get_current_advisor(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    # In production, validate JWT token and return advisor info
    # For now, return mock advisor
    return {
        "id": 1,
        "email": "advisor@relate.io",
        "name": "Default Advisor",
        "organization_id": 1
    }

# ============================================================================
# ORGANIZATION & ADVISOR MANAGEMENT
# ============================================================================

@app.post("/api/v1/organizations", response_model=dict)
async def create_organization(org: Organization):
    """Create a new organization"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO organizations (name, domain, branding_config, ai_tone_settings, compliance_rules)
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (org.name, org.domain, json.dumps(org.branding_config), 
                      json.dumps(org.ai_tone_settings), json.dumps(org.compliance_rules)))
                org_id = cur.fetchone()['id']
        return {"id": org_id, "message": "Organization created successfully"}
    except Exception as e:
        logger.error(f"Error creating organization: {e}")
        raise HTTPException(500, "Failed to create organization")
    finally:
        conn.close()

@app.post("/api/v1/advisors", response_model=dict)
async def create_advisor(advisor: Advisor):
    """Create a new advisor"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO advisors (organization_id, email, name, role, client_capacity, specializations)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """, (advisor.organization_id, advisor.email, advisor.name, advisor.role,
                      advisor.client_capacity, json.dumps(advisor.specializations)))
                advisor_id = cur.fetchone()['id']
        return {"id": advisor_id, "message": "Advisor created successfully"}
    except Exception as e:
        logger.error(f"Error creating advisor: {e}")
        raise HTTPException(500, "Failed to create advisor")
    finally:
        conn.close()

# ============================================================================
# ENHANCED CLIENT MANAGEMENT
# ============================================================================

@app.get("/api/v1/clients", response_model=List[dict])
async def get_enhanced_clients(advisor: dict = Depends(get_current_advisor)):
    """Get all clients for the current advisor with enhanced data"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.*, p.total_value, p.risk_score, p.last_sync,
                           COUNT(f.id) as feedback_count,
                           AVG(CASE WHEN f.sentiment_score IS NOT NULL THEN f.sentiment_score ELSE 0 END) as avg_sentiment
                    FROM enhanced_clients c
                    LEFT JOIN portfolios p ON c.id = p.client_id
                    LEFT JOIN enhanced_feedback f ON c.id = f.client_id
                    WHERE c.advisor_id = %s
                    GROUP BY c.id, p.total_value, p.risk_score, p.last_sync
                    ORDER BY c.name
                """, (advisor['id'],))
                clients = cur.fetchall()
        
        return [dict(client) for client in clients]
    except Exception as e:
        logger.error(f"Error fetching enhanced clients: {e}")
        raise HTTPException(500, "Failed to fetch clients")
    finally:
        conn.close()

@app.post("/api/v1/clients", response_model=dict)
async def create_enhanced_client(client: EnhancedClient, advisor: dict = Depends(get_current_advisor)):
    """Create a new enhanced client"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO enhanced_clients (
                        advisor_id, name, email, phone, risk_tolerance, 
                        investment_goals, communication_preferences, onboarding_date
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    advisor['id'], client.name, client.email, client.phone,
                    client.risk_tolerance, json.dumps(client.investment_goals),
                    json.dumps(client.communication_preferences), datetime.now()
                ))
                client_id = cur.fetchone()['id']
        
        # Broadcast to advisor's WebSocket connections
        await manager.broadcast_to_advisor(
            json.dumps({"type": "client_created", "client_id": client_id, "name": client.name}),
            advisor['id']
        )
        
        return {"id": client_id, "message": "Client created successfully"}
    except Exception as e:
        logger.error(f"Error creating client: {e}")
        raise HTTPException(500, "Failed to create client")
    finally:
        conn.close()

# ============================================================================
# PORTFOLIO MANAGEMENT
# ============================================================================

@app.get("/api/v1/portfolios/{client_id}", response_model=dict)
async def get_portfolio_details(client_id: int, advisor: dict = Depends(get_current_advisor)):
    """Get detailed portfolio information for a client"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Get portfolio data
                cur.execute("""
                    SELECT p.*, c.name as client_name, c.email as client_email
                    FROM portfolios p
                    JOIN enhanced_clients c ON p.client_id = c.id
                    WHERE p.client_id = %s AND c.advisor_id = %s
                """, (client_id, advisor['id']))
                portfolio = cur.fetchone()
                
                if not portfolio:
                    raise HTTPException(404, "Portfolio not found")
                
                # Get holdings
                cur.execute("""
                    SELECT h.*, m.change_percent, m.sector as market_sector
                    FROM holdings h
                    LEFT JOIN market_data m ON h.symbol = m.symbol
                    WHERE h.portfolio_id = %s
                    ORDER BY h.weight_percentage DESC
                """, (portfolio['id'],))
                holdings = cur.fetchall()
                
                # Get recent insights
                cur.execute("""
                    SELECT * FROM portfolio_insights
                    WHERE portfolio_id = %s
                    ORDER BY created_at DESC
                    LIMIT 5
                """, (portfolio['id'],))
                insights = cur.fetchall()
        
        return {
            "portfolio": dict(portfolio),
            "holdings": [dict(holding) for holding in holdings],
            "insights": [dict(insight) for insight in insights]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching portfolio details: {e}")
        raise HTTPException(500, "Failed to fetch portfolio details")
    finally:
        conn.close()

@app.post("/api/v1/portfolios/{client_id}/sync")
async def sync_client_portfolio(client_id: int, advisor: dict = Depends(get_current_advisor)):
    """Sync individual client portfolio with external systems"""
    try:
        # This would sync with the client's specific portfolio management system
        result = await bulk_portfolio_sync(advisor['id'], 'momentum')
        
        # Broadcast update to advisor
        await manager.broadcast_to_advisor(
            json.dumps({"type": "portfolio_synced", "client_id": client_id}),
            advisor['id']
        )
        
        return result
    except Exception as e:
        logger.error(f"Error syncing portfolio: {e}")
        raise HTTPException(500, "Failed to sync portfolio")

# ============================================================================
# AI-POWERED INSIGHTS
# ============================================================================

@app.post("/api/v1/ai/generate-insights/{portfolio_id}")
async def generate_portfolio_insights(portfolio_id: int, advisor: dict = Depends(get_current_advisor)):
    """Generate AI-powered portfolio insights"""
    try:
        # Get portfolio data
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.*, c.risk_tolerance, c.investment_goals
                    FROM portfolios p
                    JOIN enhanced_clients c ON p.client_id = c.id
                    WHERE p.id = %s AND c.advisor_id = %s
                """, (portfolio_id, advisor['id']))
                portfolio_data = cur.fetchone()
                
                if not portfolio_data:
                    raise HTTPException(404, "Portfolio not found")
        
        # Get market context
        market_context = await ai_engine.get_market_context()
        
        # Generate insights
        insights = await ai_engine.generate_portfolio_insights(
            dict(portfolio_data),
            market_context,
            {
                'risk_tolerance': portfolio_data['risk_tolerance'],
                'investment_goals': json.loads(portfolio_data.get('investment_goals', '[]')),
                'time_horizon': '5-10 years'  # This would come from client profile
            }
        )
        
        # Store insights in database
        with conn:
            with conn.cursor() as cur:
                for insight in insights:
                    cur.execute("""
                        INSERT INTO portfolio_insights (
                            portfolio_id, insight_type, title, description, 
                            recommendations, priority
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        portfolio_id, insight.insight_type, insight.title,
                        insight.description, json.dumps(insight.recommendations),
                        insight.priority
                    ))
        
        conn.close()
        return {"insights": [insight.dict() for insight in insights]}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(500, "Failed to generate insights")

@app.post("/api/v1/ai/personalized-content")
async def generate_personalized_content(request: AIGenerationRequest, advisor: dict = Depends(get_current_advisor)):
    """Generate personalized content for a client"""
    try:
        # Get client and portfolio data
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT c.*, p.total_value, p.unrealized_pnl, p.realized_pnl
                    FROM enhanced_clients c
                    LEFT JOIN portfolios p ON c.id = p.client_id
                    WHERE c.id = %s AND c.advisor_id = %s
                """, (request.client_id, advisor['id']))
                client_data = cur.fetchone()
                
                if not client_data:
                    raise HTTPException(404, "Client not found")
                
                # Get top holdings
                cur.execute("""
                    SELECT symbol, company_name, weight_percentage
                    FROM holdings h
                    JOIN portfolios p ON h.portfolio_id = p.id
                    WHERE p.client_id = %s
                    ORDER BY weight_percentage DESC
                    LIMIT 5
                """, (request.client_id,))
                holdings = cur.fetchall()
        
        # Get organization branding
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT branding_config, ai_tone_settings
                    FROM organizations o
                    JOIN advisors a ON o.id = a.organization_id
                    WHERE a.id = %s
                """, (advisor['id'],))
                org_data = cur.fetchone()
        
        conn.close()
        
        # Prepare data for AI generation
        client_info = {
            'name': client_data['name'],
            'risk_tolerance': client_data['risk_tolerance'],
            'investment_goals': json.loads(client_data.get('investment_goals', '[]')),
            'communication_preferences': json.loads(client_data.get('communication_preferences', '{}'))
        }
        
        portfolio_info = {
            'total_value': float(client_data.get('total_value', 0)),
            'performance': float(client_data.get('unrealized_pnl', 0)),
            'top_holdings': [h['symbol'] for h in holdings],
            'recent_changes': 'Portfolio updated with latest market data'
        }
        
        advisor_tone = json.loads(org_data.get('ai_tone_settings', '{}')) if org_data else {}
        firm_branding = json.loads(org_data.get('branding_config', '{}')) if org_data else {}
        
        # Generate content
        content = await ai_engine.generate_personalized_content(
            client_info, portfolio_info, advisor_tone, firm_branding, request.content_type
        )
        
        return {"content": content, "client_name": client_data['name']}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating personalized content: {e}")
        raise HTTPException(500, "Failed to generate content")

# ============================================================================
# ENHANCED FEEDBACK & SENTIMENT ANALYSIS
# ============================================================================

@app.post("/api/v1/feedback/advanced")
async def submit_advanced_feedback(payload: dict):
    """Submit feedback with advanced AI analysis"""
    client_id = payload.get('client_id')
    text = payload.get('text')
    
    if not client_id or not text:
        raise HTTPException(400, "Missing client_id or text")
    
    try:
        # Advanced AI analysis
        analysis = await ai_engine.analyze_feedback_advanced(text)
        
        # Store in database
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO enhanced_feedback (
                        client_id, text, sentiment, sentiment_score, topics,
                        urgency_level, action_items, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (
                    client_id, text, analysis['sentiment'], analysis['sentiment_score'],
                    json.dumps(analysis['topics']), analysis['urgency_level'],
                    json.dumps(analysis['action_items']), datetime.now()
                ))
                feedback_id = cur.fetchone()['id']
                
                # Get advisor_id for WebSocket notification
                cur.execute("""
                    SELECT advisor_id FROM enhanced_clients WHERE id = %s
                """, (client_id,))
                advisor_id = cur.fetchone()['advisor_id']
        
        conn.close()
        
        # Send real-time notification to advisor
        await manager.broadcast_to_advisor(
            json.dumps({
                "type": "new_feedback",
                "feedback_id": feedback_id,
                "client_id": client_id,
                "sentiment": analysis['sentiment'],
                "urgency": analysis['urgency_level'],
                "topics": analysis['topics']
            }),
            advisor_id
        )
        
        return {
            "feedback_id": feedback_id,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error submitting advanced feedback: {e}")
        raise HTTPException(500, "Failed to submit feedback")

@app.get("/api/v1/analytics/sentiment-trends")
async def get_sentiment_trends(
    time_range: str = "30d",
    advisor: dict = Depends(get_current_advisor)
):
    """Get sentiment trends for advisor's clients"""
    conn = get_db_connection()
    try:
        # Calculate date range
        days = int(time_range.replace('d', ''))
        start_date = datetime.now() - timedelta(days=days)
        
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        DATE(f.created_at) as date,
                        AVG(f.sentiment_score) as avg_sentiment,
                        COUNT(*) as feedback_count,
                        COUNT(CASE WHEN f.sentiment = 'negative' THEN 1 END) as negative_count,
                        COUNT(CASE WHEN f.urgency_level >= 4 THEN 1 END) as urgent_count
                    FROM enhanced_feedback f
                    JOIN enhanced_clients c ON f.client_id = c.id
                    WHERE c.advisor_id = %s AND f.created_at >= %s
                    GROUP BY DATE(f.created_at)
                    ORDER BY date
                """, (advisor['id'], start_date))
                trends = cur.fetchall()
                
                # Get topic distribution
                cur.execute("""
                    SELECT 
                        jsonb_array_elements_text(f.topics) as topic,
                        COUNT(*) as count
                    FROM enhanced_feedback f
                    JOIN enhanced_clients c ON f.client_id = c.id
                    WHERE c.advisor_id = %s AND f.created_at >= %s
                    GROUP BY topic
                    ORDER BY count DESC
                    LIMIT 10
                """, (advisor['id'], start_date))
                topics = cur.fetchall()
        
        return {
            "trends": [dict(trend) for trend in trends],
            "top_topics": [dict(topic) for topic in topics]
        }
    except Exception as e:
        logger.error(f"Error fetching sentiment trends: {e}")
        raise HTTPException(500, "Failed to fetch sentiment trends")
    finally:
        conn.close()

# ============================================================================
# INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/v1/integrations/momentum/sync")
async def sync_momentum_integration(advisor: dict = Depends(get_current_advisor)):
    """Sync with Momentum portfolio management system"""
    try:
        result = await sync_momentum_portfolios(advisor['id'])
        return result
    except Exception as e:
        logger.error(f"Error syncing Momentum: {e}")
        raise HTTPException(500, "Failed to sync with Momentum")

@app.get("/api/v1/integrations/status")
async def get_integration_status():
    """Get status of all integrations"""
    return integration_manager.get_integration_status()

@app.post("/api/v1/integrations/market-data/update")
async def update_market_data_endpoint(symbols: List[str]):
    """Update market data for specified symbols"""
    try:
        async with integration_manager:
            result = await integration_manager.fetch_market_data(symbols)
        return {"updated_symbols": list(result.keys())}
    except Exception as e:
        logger.error(f"Error updating market data: {e}")
        raise HTTPException(500, "Failed to update market data")

# ============================================================================
# BULK OPERATIONS
# ============================================================================

@app.post("/api/v1/bulk/generate-updates")
async def bulk_generate_updates(request: BulkUpdateRequest, advisor: dict = Depends(get_current_advisor)):
    """Generate bulk updates for multiple clients"""
    try:
        results = []
        for client_id in request.client_ids:
            try:
                # Generate personalized content for each client
                ai_request = AIGenerationRequest(
                    client_id=client_id,
                    content_type=request.content_type
                )
                content_result = await generate_personalized_content(ai_request, advisor)
                results.append({
                    "client_id": client_id,
                    "success": True,
                    "content": content_result["content"]
                })
            except Exception as e:
                results.append({
                    "client_id": client_id,
                    "success": False,
                    "error": str(e)
                })
        
        return {"results": results}
    except Exception as e:
        logger.error(f"Error in bulk update generation: {e}")
        raise HTTPException(500, "Failed to generate bulk updates")

# ============================================================================
# WEBSOCKET ENDPOINTS
# ============================================================================

@app.websocket("/ws/{advisor_id}")
async def websocket_endpoint(websocket: WebSocket, advisor_id: int):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, advisor_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, advisor_id)

# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@app.post("/onboard-advisor")
def onboard_advisor():
    logger.info("Advisor onboarded")
    return {"message": "Advisor onboarded"}

@app.post("/import-clients")
async def import_clients(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Invalid file type")
    try:
        contents = await file.read()
        clients = import_clients_from_csv(contents)
        num_imported = len(clients)
        logger.info(f"Imported {num_imported} clients")
        return {"message": f"{num_imported} clients imported"}
    except Exception as e:
        logger.error(f"Error importing clients: {e}")
        raise HTTPException(500, "Failed to import clients")

@app.get("/clients")
def list_clients():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, email, portfolio_value FROM clients")
                clients = cur.fetchall()
        conn.close()
        return [{"id": c[0], "name": c[1], "email": c[2], "portfolio_value": c[3]} for c in clients]
    except Exception as e:
        logger.error(f"Error fetching clients: {e}")
        raise HTTPException(500, "Failed to fetch clients")

@app.post("/generate-update/{client_id}")
def generate_update(client_id: int):
    try:
        # Use legacy function for backward compatibility
        from services import generate_and_send_update
        generate_and_send_update(client_id)
        return {"message": "Update sent"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating update for client {client_id}: {e}")
        raise HTTPException(500, "Failed to send update")

@app.post("/feedback")
def feedback_endpoint(payload: dict):
    client_id = payload.get('client_id')
    text = payload.get('text')
    if not client_id or not text:
        raise HTTPException(400, "Missing client_id or text")
    try:
        from services import submit_feedback
        sentiment = submit_feedback(client_id, text)
        return {"sentiment": sentiment}
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(500, "Failed to submit feedback")

@app.get("/feedback")
def list_feedback():
    try:
        from services import get_feedback
        feedback = get_feedback()
        return feedback
    except Exception as e:
        logger.error(f"Error fetching feedback: {e}")
        raise HTTPException(500, "Failed to fetch feedback")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
