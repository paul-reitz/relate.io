import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

def get_db_connection():
    """Get database connection with enhanced configuration"""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "relate_io"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            port=os.getenv("DB_PORT", "5432"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def create_enhanced_tables():
    """Create all enhanced database tables"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Organizations table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        domain VARCHAR(255) UNIQUE,
                        branding_config JSONB DEFAULT '{}',
                        ai_tone_settings JSONB DEFAULT '{}',
                        compliance_rules JSONB DEFAULT '{}',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Advisors table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS advisors (
                        id SERIAL PRIMARY KEY,
                        organization_id INTEGER REFERENCES organizations(id),
                        email VARCHAR(255) UNIQUE NOT NULL,
                        name VARCHAR(255) NOT NULL,
                        role VARCHAR(50) DEFAULT 'advisor',
                        client_capacity INTEGER DEFAULT 100,
                        specializations JSONB DEFAULT '[]',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Enhanced clients table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS enhanced_clients (
                        id SERIAL PRIMARY KEY,
                        advisor_id INTEGER REFERENCES advisors(id),
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL,
                        phone VARCHAR(20),
                        risk_tolerance VARCHAR(20) DEFAULT 'moderate',
                        investment_goals JSONB DEFAULT '[]',
                        communication_preferences JSONB DEFAULT '{}',
                        onboarding_date TIMESTAMP,
                        last_contact TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Portfolios table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS portfolios (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER REFERENCES enhanced_clients(id),
                        total_value DECIMAL(15,2) NOT NULL,
                        cash_balance DECIMAL(15,2) DEFAULT 0.00,
                        invested_amount DECIMAL(15,2) DEFAULT 0.00,
                        unrealized_pnl DECIMAL(15,2) DEFAULT 0.00,
                        realized_pnl DECIMAL(15,2) DEFAULT 0.00,
                        risk_score DECIMAL(3,2) CHECK (risk_score >= 0 AND risk_score <= 10),
                        benchmark_return DECIMAL(5,2),
                        last_sync TIMESTAMP,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Holdings table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS holdings (
                        id SERIAL PRIMARY KEY,
                        portfolio_id INTEGER REFERENCES portfolios(id),
                        symbol VARCHAR(10) NOT NULL,
                        company_name VARCHAR(255),
                        quantity DECIMAL(15,4) NOT NULL,
                        current_price DECIMAL(10,2) NOT NULL,
                        cost_basis DECIMAL(10,2) NOT NULL,
                        market_value DECIMAL(15,2) NOT NULL,
                        weight_percentage DECIMAL(5,2),
                        sector VARCHAR(100),
                        asset_class VARCHAR(50) NOT NULL,
                        dividend_yield DECIMAL(5,2),
                        last_updated TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Market data table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS market_data (
                        symbol VARCHAR(10) PRIMARY KEY,
                        price DECIMAL(10,2) NOT NULL,
                        change_percent DECIMAL(5,2),
                        volume BIGINT,
                        market_cap BIGINT,
                        pe_ratio DECIMAL(6,2),
                        dividend_yield DECIMAL(5,2),
                        sector VARCHAR(100),
                        last_updated TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Enhanced feedback table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS enhanced_feedback (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER REFERENCES enhanced_clients(id),
                        text TEXT NOT NULL,
                        sentiment VARCHAR(20) NOT NULL,
                        sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
                        topics JSONB DEFAULT '[]',
                        urgency_level INTEGER CHECK (urgency_level >= 1 AND urgency_level <= 5) DEFAULT 3,
                        action_items JSONB DEFAULT '[]',
                        is_resolved BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Communication logs table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS communication_logs (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER REFERENCES enhanced_clients(id),
                        advisor_id INTEGER REFERENCES advisors(id),
                        channel VARCHAR(20) NOT NULL,
                        subject VARCHAR(255),
                        content TEXT NOT NULL,
                        direction VARCHAR(10) NOT NULL,
                        status VARCHAR(20) DEFAULT 'sent',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Portfolio insights table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS portfolio_insights (
                        id SERIAL PRIMARY KEY,
                        portfolio_id INTEGER REFERENCES portfolios(id),
                        insight_type VARCHAR(50) NOT NULL,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        recommendations JSONB DEFAULT '[]',
                        priority INTEGER CHECK (priority >= 1 AND priority <= 5) DEFAULT 3,
                        is_actionable BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Referral requests table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS referral_requests (
                        id SERIAL PRIMARY KEY,
                        referring_client_id INTEGER REFERENCES enhanced_clients(id),
                        advisor_id INTEGER REFERENCES advisors(id),
                        prospect_name VARCHAR(255) NOT NULL,
                        prospect_email VARCHAR(255) NOT NULL,
                        prospect_phone VARCHAR(20),
                        referral_notes TEXT,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # AI generation history table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS ai_generation_history (
                        id SERIAL PRIMARY KEY,
                        client_id INTEGER REFERENCES enhanced_clients(id),
                        content_type VARCHAR(50) NOT NULL,
                        generated_content TEXT NOT NULL,
                        personalization_level VARCHAR(20),
                        tone VARCHAR(20),
                        tokens_used INTEGER,
                        generation_time_ms INTEGER,
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)

                # Create indexes for better performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_clients_advisor ON enhanced_clients(advisor_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_portfolios_client ON portfolios(client_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_holdings_portfolio ON holdings(portfolio_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_feedback_client ON enhanced_feedback(client_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_feedback_sentiment ON enhanced_feedback(sentiment)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_feedback_urgency ON enhanced_feedback(urgency_level)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_communication_client ON communication_logs(client_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_communication_advisor ON communication_logs(advisor_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_insights_portfolio ON portfolio_insights(portfolio_id)")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_referrals_advisor ON referral_requests(advisor_id)")

                logger.info("Enhanced database tables created successfully")
                
    except Exception as e:
        logger.error(f"Error creating enhanced tables: {e}")
        raise
    finally:
        conn.close()

def migrate_existing_data():
    """Migrate data from old tables to new enhanced tables"""
    conn = get_db_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Create default organization if none exists
                cur.execute("""
                    INSERT INTO organizations (name, domain, branding_config)
                    SELECT 'Default Organization', 'default.com', '{}'
                    WHERE NOT EXISTS (SELECT 1 FROM organizations)
                """)
                
                # Create default advisor if none exists
                cur.execute("""
                    INSERT INTO advisors (organization_id, email, name)
                    SELECT 1, 'admin@relate.io', 'Default Advisor'
                    WHERE NOT EXISTS (SELECT 1 FROM advisors)
                """)
                
                # Migrate existing clients if they exist
                cur.execute("""
                    INSERT INTO enhanced_clients (advisor_id, name, email, created_at)
                    SELECT 1, name, email, NOW()
                    FROM clients
                    WHERE NOT EXISTS (
                        SELECT 1 FROM enhanced_clients 
                        WHERE enhanced_clients.email = clients.email
                    )
                """)
                
                # Migrate existing feedback if it exists
                cur.execute("""
                    INSERT INTO enhanced_feedback (client_id, text, sentiment, sentiment_score, created_at)
                    SELECT 
                        ec.id,
                        f.text,
                        CASE 
                            WHEN f.sentiment = 'POSITIVE' THEN 'positive'
                            WHEN f.sentiment = 'NEGATIVE' THEN 'negative'
                            ELSE 'neutral'
                        END,
                        CASE 
                            WHEN f.sentiment = 'POSITIVE' THEN 0.5
                            WHEN f.sentiment = 'NEGATIVE' THEN -0.5
                            ELSE 0.0
                        END,
                        NOW()
                    FROM feedback f
                    JOIN clients c ON f.client_id = c.id
                    JOIN enhanced_clients ec ON ec.email = c.email
                    WHERE NOT EXISTS (
                        SELECT 1 FROM enhanced_feedback ef 
                        WHERE ef.client_id = ec.id AND ef.text = f.text
                    )
                """)
                
                logger.info("Data migration completed successfully")
                
    except Exception as e:
        logger.error(f"Error during data migration: {e}")
        # Don't raise here as this might be expected if old tables don't exist
    finally:
        conn.close()

if __name__ == "__main__":
    create_enhanced_tables()
    migrate_existing_data()
