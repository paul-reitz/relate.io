#!/usr/bin/env python3
"""
Populate the database with dummy data for testing Relate.io
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from faker import Faker
import requests
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

fake = Faker()

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="relate_io",
        user="postgres",
        password="password",
        cursor_factory=RealDictCursor
    )

# Sample data generators
def generate_client_data() -> List[Dict[str, Any]]:
    """Generate realistic client data"""
    clients = []
    
    # High-net-worth individuals
    high_net_worth_names = [
        "James Wellington", "Sarah Montgomery", "Robert Blackstone", 
        "Elizabeth Hartwell", "Michael Rothschild", "Catherine Pemberton",
        "David Ashworth", "Victoria Sterling", "Alexander Fairfax", "Isabella Whitmore"
    ]
    
    # Business owners
    business_owners = [
        "John Mitchell", "Lisa Chen", "Mark Thompson", "Rachel Green",
        "Steven Rodriguez", "Amanda Foster", "Kevin Park", "Nicole Davis"
    ]
    
    # Young professionals
    young_professionals = [
        "Tyler Johnson", "Emma Wilson", "Brandon Lee", "Sophia Martinez",
        "Jordan Taylor", "Olivia Brown", "Austin Clark", "Maya Patel"
    ]
    
    all_names = high_net_worth_names + business_owners + young_professionals
    
    for i, name in enumerate(all_names):
        # Determine client type and generate appropriate data
        if name in high_net_worth_names:
            portfolio_value = random.randint(2000000, 10000000)
            risk_tolerance = random.choice(["conservative", "moderate"])
            goals = ["wealth_preservation", "tax_optimization", "estate_planning"]
        elif name in business_owners:
            portfolio_value = random.randint(500000, 3000000)
            risk_tolerance = random.choice(["moderate", "aggressive"])
            goals = ["business_growth", "retirement_planning", "tax_optimization"]
        else:  # young professionals
            portfolio_value = random.randint(50000, 500000)
            risk_tolerance = random.choice(["moderate", "aggressive"])
            goals = ["wealth_building", "retirement_planning", "home_purchase"]
        
        email = f"{name.lower().replace(' ', '.')}@{random.choice(['gmail.com', 'outlook.com', 'yahoo.com', 'company.com'])}"
        
        client = {
            "name": name,
            "email": email,
            "phone": fake.phone_number(),
            "risk_tolerance": risk_tolerance,
            "investment_goals": goals,
            "communication_preferences": {
                "email_frequency": random.choice(["weekly", "monthly", "quarterly"]),
                "preferred_contact": random.choice(["email", "phone", "both"]),
                "newsletter": random.choice([True, False])
            },
            "portfolio_value": portfolio_value,
            "created_at": fake.date_time_between(start_date="-2y", end_date="now")
        }
        clients.append(client)
    
    return clients

def generate_feedback_data(client_ids: List[int]) -> List[Dict[str, Any]]:
    """Generate realistic feedback data"""
    feedback_templates = {
        "positive": [
            "Very happy with the portfolio performance this quarter. The diversification strategy is working well.",
            "Excellent communication and transparency. I feel well-informed about my investments.",
            "The recent rebalancing has improved my returns significantly. Thank you for the proactive management.",
            "I appreciate the detailed monthly reports and the clear explanations of market conditions.",
            "Great job on the tax-loss harvesting strategy. It saved me a considerable amount this year."
        ],
        "neutral": [
            "Could you provide more information about the ESG investment options available?",
            "I'd like to discuss increasing my allocation to international markets.",
            "When would be a good time to review my retirement planning strategy?",
            "I'm interested in learning more about the new investment products you mentioned.",
            "Can we schedule a meeting to discuss my portfolio's performance relative to benchmarks?"
        ],
        "negative": [
            "I'm concerned about the recent volatility in my portfolio. Can we discuss risk management?",
            "The fees seem higher than expected. Could you provide a breakdown of all charges?",
            "I'm worried about the current market conditions and their impact on my retirement plans.",
            "The performance has been disappointing compared to the market indices. What's the strategy?",
            "I need to access some funds urgently. What are my options without significant penalties?"
        ],
        "urgent": [
            "URGENT: I need to liquidate 20% of my portfolio immediately due to a family emergency.",
            "Please call me ASAP regarding the recent market crash and its impact on my investments.",
            "URGENT: There's been a significant change in my financial situation. We need to meet this week.",
            "I'm very concerned about the recent losses. This is urgent - please contact me today."
        ]
    }
    
    feedback_list = []
    
    for client_id in client_ids:
        # Generate 0-5 feedback items per client
        num_feedback = random.randint(0, 5)
        
        for _ in range(num_feedback):
            sentiment_type = random.choices(
                ["positive", "neutral", "negative", "urgent"],
                weights=[40, 35, 20, 5]
            )[0]
            
            text = random.choice(feedback_templates[sentiment_type])
            
            # Determine urgency and topics based on content
            if sentiment_type == "urgent":
                urgency = "high"
                topics = ["urgent", "portfolio", "meeting"]
            elif "tax" in text.lower():
                urgency = "medium"
                topics = ["tax", "strategy"]
            elif "fee" in text.lower() or "charge" in text.lower():
                urgency = "medium"
                topics = ["fees", "costs"]
            elif "performance" in text.lower():
                urgency = "medium" if sentiment_type == "negative" else "low"
                topics = ["performance", "portfolio"]
            elif "retirement" in text.lower():
                urgency = "medium"
                topics = ["retirement", "planning"]
            else:
                urgency = "high" if sentiment_type == "urgent" else "low"
                topics = ["general", "portfolio"]
            
            feedback = {
                "client_id": client_id,
                "text": text,
                "sentiment": "positive" if sentiment_type == "positive" else 
                           "negative" if sentiment_type in ["negative", "urgent"] else "neutral",
                "topics": topics,
                "urgency": urgency,
                "created_at": fake.date_time_between(start_date="-6m", end_date="now")
            }
            feedback_list.append(feedback)
    
    return feedback_list

def generate_portfolio_data(client_ids: List[int]) -> List[Dict[str, Any]]:
    """Generate realistic portfolio data"""
    portfolios = []
    
    # Common holdings with realistic allocations
    stock_holdings = [
        {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
        {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
        {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
        {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services"},
        {"symbol": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Staples"},
        {"symbol": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare"}
    ]
    
    etf_holdings = [
        {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust", "sector": "Broad Market"},
        {"symbol": "QQQ", "name": "Invesco QQQ Trust", "sector": "Technology"},
        {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF", "sector": "Broad Market"},
        {"symbol": "BND", "name": "Vanguard Total Bond Market ETF", "sector": "Fixed Income"},
        {"symbol": "VEA", "name": "Vanguard FTSE Developed Markets ETF", "sector": "International"},
        {"symbol": "VWO", "name": "Vanguard FTSE Emerging Markets ETF", "sector": "Emerging Markets"}
    ]
    
    for client_id in client_ids:
        # Get client info to determine portfolio size
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client = cur.fetchone()
        cur.close()
        conn.close()
        
        if not client:
            continue
            
        total_value = random.randint(50000, 5000000)  # Will be updated based on holdings
        
        # Generate holdings based on risk tolerance
        holdings = []
        remaining_allocation = 100.0
        
        # Conservative: More bonds and ETFs
        # Moderate: Balanced mix
        # Aggressive: More individual stocks
        
        risk_tolerance = client.get('risk_tolerance', 'moderate')
        
        if risk_tolerance == 'conservative':
            # 60% ETFs, 30% bonds, 10% individual stocks
            num_etfs = random.randint(3, 5)
            num_stocks = random.randint(1, 3)
            bond_allocation = 30.0
        elif risk_tolerance == 'aggressive':
            # 30% ETFs, 10% bonds, 60% individual stocks
            num_etfs = random.randint(2, 3)
            num_stocks = random.randint(5, 8)
            bond_allocation = 10.0
        else:  # moderate
            # 50% ETFs, 20% bonds, 30% individual stocks
            num_etfs = random.randint(3, 4)
            num_stocks = random.randint(3, 5)
            bond_allocation = 20.0
        
        # Add bond allocation
        if bond_allocation > 0:
            holdings.append({
                "symbol": "BND",
                "name": "Vanguard Total Bond Market ETF",
                "shares": 100,
                "market_value": total_value * (bond_allocation / 100),
                "weight_percentage": bond_allocation,
                "change_percent": random.uniform(-2.0, 2.0),
                "sector": "Fixed Income"
            })
            remaining_allocation -= bond_allocation
        
        # Add ETF holdings
        selected_etfs = random.sample(etf_holdings, min(num_etfs, len(etf_holdings)))
        etf_allocation = remaining_allocation * 0.6  # 60% of remaining for ETFs
        
        for i, etf in enumerate(selected_etfs):
            allocation = etf_allocation / len(selected_etfs)
            if i == len(selected_etfs) - 1:  # Last ETF gets remaining
                allocation = remaining_allocation - sum(h['weight_percentage'] for h in holdings if h['symbol'] != 'BND')
            
            holdings.append({
                "symbol": etf["symbol"],
                "name": etf["name"],
                "shares": random.randint(50, 500),
                "market_value": total_value * (allocation / 100),
                "weight_percentage": allocation,
                "change_percent": random.uniform(-5.0, 8.0),
                "sector": etf["sector"]
            })
            remaining_allocation -= allocation
        
        # Add individual stock holdings
        selected_stocks = random.sample(stock_holdings, min(num_stocks, len(stock_holdings)))
        
        for i, stock in enumerate(selected_stocks):
            allocation = remaining_allocation / len(selected_stocks)
            
            holdings.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "shares": random.randint(10, 200),
                "market_value": total_value * (allocation / 100),
                "weight_percentage": allocation,
                "change_percent": random.uniform(-10.0, 15.0),
                "sector": stock["sector"]
            })
        
        # Calculate performance metrics
        ytd_return = random.uniform(-15.0, 25.0)
        monthly_return = random.uniform(-5.0, 8.0)
        total_return = random.uniform(-10.0, 30.0)
        
        # Calculate risk score based on holdings and performance
        risk_score = random.uniform(3.0, 8.0)
        if risk_tolerance == 'conservative':
            risk_score = random.uniform(2.0, 5.0)
        elif risk_tolerance == 'aggressive':
            risk_score = random.uniform(6.0, 9.0)
        
        portfolio = {
            "client_id": client_id,
            "total_value": total_value,
            "holdings": holdings,
            "performance": {
                "ytd_return": ytd_return,
                "monthly_return": monthly_return,
                "total_return": total_return
            },
            "risk_score": risk_score,
            "last_updated": datetime.now()
        }
        portfolios.append(portfolio)
    
    return portfolios

def send_welcome_email(client_email: str, client_name: str):
    """Send welcome email to new client"""
    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0066CC 0%, #3385D6 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to Relate.io</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">Your Financial Advisory Platform</p>
            </div>
            
            <div style="padding: 40px 20px; background: #FAFBFC;">
                <h2 style="color: #1E293B; margin-bottom: 20px;">Hello {client_name},</h2>
                
                <p style="color: #475569; line-height: 1.6; margin-bottom: 20px;">
                    Welcome to Relate.io! We're excited to have you as part of our financial advisory platform. 
                    Our AI-powered system will help your financial advisor provide you with personalized insights 
                    and regular updates about your portfolio.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0066CC;">
                    <h3 style="color: #1E293B; margin-top: 0;">What to Expect:</h3>
                    <ul style="color: #475569; line-height: 1.6;">
                        <li>Regular portfolio updates and performance reports</li>
                        <li>Personalized investment insights and recommendations</li>
                        <li>Market analysis and economic updates</li>
                        <li>Easy feedback system to communicate with your advisor</li>
                    </ul>
                </div>
                
                <p style="color: #475569; line-height: 1.6; margin-bottom: 30px;">
                    Your financial advisor will be in touch soon with your first personalized portfolio update. 
                    If you have any questions or concerns, please don't hesitate to reach out.
                </p>
                
                <div style="text-align: center;">
                    <a href="http://localhost:3001" 
                       style="background: #0066CC; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        Access Your Dashboard
                    </a>
                </div>
            </div>
            
            <div style="background: #1E293B; padding: 20px; text-align: center;">
                <p style="color: #94A3B8; margin: 0; font-size: 14px;">
                    © 2025 Relate.io - Your Trusted Financial Advisory Platform
                </p>
            </div>
        </div>
        """
        
        message = Mail(
            from_email='noreply@relate.io',
            to_emails=client_email,
            subject='Welcome to Relate.io - Your Financial Journey Begins',
            html_content=html_content
        )
        
        response = sg.send(message)
        print(f"Welcome email sent to {client_email}: {response.status_code}")
        
    except Exception as e:
        print(f"Error sending welcome email to {client_email}: {e}")

def send_demo_email():
    """Send a demo email to the specified address"""
    try:
        sg = SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        
        html_content = """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #0066CC 0%, #3385D6 100%); padding: 40px 20px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 28px;">Relate.io Demo</h1>
                <p style="color: white; margin: 10px 0 0 0; font-size: 16px;">AI-Powered Financial Advisory Platform</p>
            </div>
            
            <div style="padding: 40px 20px; background: #FAFBFC;">
                <h2 style="color: #1E293B; margin-bottom: 20px;">Demo System Ready!</h2>
                
                <p style="color: #475569; line-height: 1.6; margin-bottom: 20px;">
                    Your Relate.io demo system has been successfully set up with sample data. The platform includes:
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #00A651;">
                    <h3 style="color: #1E293B; margin-top: 0;">System Features:</h3>
                    <ul style="color: #475569; line-height: 1.6;">
                        <li><strong>26 Sample Clients</strong> - High-net-worth individuals, business owners, and young professionals</li>
                        <li><strong>Realistic Portfolio Data</strong> - Diversified holdings with performance metrics</li>
                        <li><strong>AI-Powered Feedback Analysis</strong> - Sentiment analysis and topic extraction</li>
                        <li><strong>Beautiful Dashboard</strong> - Momentum-inspired design with charts and analytics</li>
                        <li><strong>Email Automation</strong> - Personalized client communications</li>
                    </ul>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FF6B35;">
                    <h3 style="color: #1E293B; margin-top: 0;">Access Information:</h3>
                    <p style="color: #475569; margin: 0;"><strong>Dashboard:</strong> <a href="http://localhost:3001">http://localhost:3001</a></p>
                    <p style="color: #475569; margin: 5px 0 0 0;"><strong>API:</strong> <a href="http://localhost:8000">http://localhost:8000</a></p>
                    <p style="color: #475569; margin: 5px 0 0 0;"><strong>API Docs:</strong> <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></p>
                </div>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #FFB800;">
                    <h3 style="color: #1E293B; margin-top: 0;">Quick Start:</h3>
                    <p style="color: #475569; margin: 0;">Run the system with: <code>./start_relate_io.sh</code></p>
                    <p style="color: #475569; margin: 5px 0 0 0;">Stop the system with: <code>./stop_relate_io.sh</code></p>
                </div>
                
                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://localhost:3001" 
                       style="background: #0066CC; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold; margin-right: 10px;">
                        View Dashboard
                    </a>
                    <a href="http://localhost:8000/docs" 
                       style="background: #00A651; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        API Documentation
                    </a>
                </div>
            </div>
            
            <div style="background: #1E293B; padding: 20px; text-align: center;">
                <p style="color: #94A3B8; margin: 0; font-size: 14px;">
                    © 2025 Relate.io - Built with AI for Financial Advisors
                </p>
            </div>
        </div>
        """
        
        message = Mail(
            from_email='demo@relate.io',
            to_emails='paulreitz.pr@gmail.com',
            subject='🚀 Relate.io Demo System Ready - AI-Powered Financial Advisory Platform',
            html_content=html_content
        )
        
        response = sg.send(message)
        print(f"Demo email sent to paulreitz.pr@gmail.com: {response.status_code}")
        
    except Exception as e:
        print(f"Error sending demo email: {e}")

def populate_database():
    """Main function to populate the database with dummy data"""
    print("🚀 Starting database population...")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Clear existing data
        print("🧹 Clearing existing data...")
        cur.execute("DELETE FROM feedback")
        cur.execute("DELETE FROM portfolios")
        cur.execute("DELETE FROM clients")
        conn.commit()
        
        # Generate and insert clients
        print("👥 Generating client data...")
        clients_data = generate_client_data()
        client_ids = []
        
        for client in clients_data:
            cur.execute("""
                INSERT INTO clients (name, email, phone, risk_tolerance, investment_goals, communication_preferences, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                client["name"],
                client["email"],
                client["phone"],
                client["risk_tolerance"],
                json.dumps(client["investment_goals"]),
                json.dumps(client["communication_preferences"]),
                client["created_at"]
            ))
            client_id = cur.fetchone()['id']
            client_ids.append(client_id)
            
            # Send welcome email (if SendGrid is configured)
            if os.environ.get('SENDGRID_API_KEY'):
                send_welcome_email(client["email"], client["name"])
        
        conn.commit()
        print(f"✅ Created {len(client_ids)} clients")
        
        # Generate and insert feedback
        print("💬 Generating feedback data...")
        feedback_data = generate_feedback_data(client_ids)
        
        for feedback in feedback_data:
            cur.execute("""
                INSERT INTO feedback (client_id, text, sentiment, topics, urgency, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                feedback["client_id"],
                feedback["text"],
                feedback["sentiment"],
                json.dumps(feedback["topics"]),
                feedback["urgency"],
                feedback["created_at"]
            ))
        
        conn.commit()
        print(f"✅ Created {len(feedback_data)} feedback items")
        
        # Generate and insert portfolios
        print("📊 Generating portfolio data...")
        portfolio_data = generate_portfolio_data(client_ids)
        
        for portfolio in portfolio_data:
            cur.execute("""
                INSERT INTO portfolios (client_id, total_value, holdings, performance, risk_score, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                portfolio["client_id"],
                portfolio["total_value"],
                json.dumps(portfolio["holdings"]),
                json.dumps(portfolio["performance"]),
                portfolio["risk_score"],
                portfolio["last_updated"]
            ))
        
        conn.commit()
        print(f"✅ Created {len(portfolio_data)} portfolios")
        
        cur.close()
        conn.close()
        
        # Send demo email
        print("📧 Sending demo notification email...")
        send_demo_email()
        
        print("🎉 Database population completed successfully!")
        print(f"📊 Summary:")
        print(f"   - Clients: {len(client_ids)}")
        print(f"   - Feedback items: {len(feedback_data)}")
        print(f"   - Portfolios: {len(portfolio_data)}")
        print(f"   - Demo email sent to: paulreitz.pr@gmail.com")
        
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        if conn:
            conn.rollback()
        raise

if __name__ == "__main__":
    # Install faker if not already installed
    try:
        import faker
    except ImportError:
        print("Installing faker...")
        import subprocess
        subprocess.check_call(["pip", "install", "faker"])
        from faker import Faker
        fake = Faker()
    
    populate_database()
