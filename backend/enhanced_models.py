from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AssetClass(str, Enum):
    EQUITY = "equity"
    BOND = "bond"
    CASH = "cash"
    ALTERNATIVE = "alternative"
    COMMODITY = "commodity"
    REAL_ESTATE = "real_estate"

class RiskLevel(str, Enum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class SentimentLevel(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"

class Organization(BaseModel):
    id: Optional[int] = None
    name: str
    domain: str
    branding_config: Dict[str, Any] = Field(default_factory=dict)
    ai_tone_settings: Dict[str, Any] = Field(default_factory=dict)
    compliance_rules: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None

class Advisor(BaseModel):
    id: Optional[int] = None
    organization_id: int
    email: str
    name: str
    role: str = "advisor"
    client_capacity: int = 100
    specializations: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None

class EnhancedClient(BaseModel):
    id: Optional[int] = None
    advisor_id: int
    name: str
    email: str
    phone: Optional[str] = None
    risk_tolerance: RiskLevel = RiskLevel.MODERATE
    investment_goals: List[str] = Field(default_factory=list)
    communication_preferences: Dict[str, Any] = Field(default_factory=dict)
    onboarding_date: Optional[datetime] = None
    last_contact: Optional[datetime] = None
    created_at: Optional[datetime] = None

class Portfolio(BaseModel):
    id: Optional[int] = None
    client_id: int
    total_value: float
    cash_balance: float = 0.0
    invested_amount: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    risk_score: float = Field(ge=0.0, le=10.0)
    benchmark_return: Optional[float] = None
    last_sync: Optional[datetime] = None
    created_at: Optional[datetime] = None

class Holding(BaseModel):
    id: Optional[int] = None
    portfolio_id: int
    symbol: str
    company_name: Optional[str] = None
    quantity: float
    current_price: float
    cost_basis: float
    market_value: float
    weight_percentage: float
    sector: Optional[str] = None
    asset_class: AssetClass
    dividend_yield: Optional[float] = None
    last_updated: Optional[datetime] = None

class MarketData(BaseModel):
    symbol: str
    price: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    sector: Optional[str] = None
    last_updated: datetime

class EnhancedFeedback(BaseModel):
    id: Optional[int] = None
    client_id: int
    text: str
    sentiment: SentimentLevel
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    topics: List[str] = Field(default_factory=list)
    urgency_level: int = Field(ge=1, le=5, default=3)
    action_items: List[str] = Field(default_factory=list)
    is_resolved: bool = False
    created_at: Optional[datetime] = None

class CommunicationLog(BaseModel):
    id: Optional[int] = None
    client_id: int
    advisor_id: int
    channel: str  # email, sms, phone, in_person
    subject: Optional[str] = None
    content: str
    direction: str  # inbound, outbound
    status: str = "sent"  # sent, delivered, read, failed
    created_at: Optional[datetime] = None

class PortfolioInsight(BaseModel):
    id: Optional[int] = None
    portfolio_id: int
    insight_type: str  # risk_analysis, performance_attribution, rebalancing
    title: str
    description: str
    recommendations: List[str] = Field(default_factory=list)
    priority: int = Field(ge=1, le=5, default=3)
    is_actionable: bool = True
    created_at: Optional[datetime] = None

class ReferralRequest(BaseModel):
    id: Optional[int] = None
    referring_client_id: int
    advisor_id: int
    prospect_name: str
    prospect_email: str
    prospect_phone: Optional[str] = None
    referral_notes: Optional[str] = None
    status: str = "pending"  # pending, contacted, converted, declined
    created_at: Optional[datetime] = None

class AIGenerationRequest(BaseModel):
    client_id: int
    content_type: str  # portfolio_update, market_commentary, risk_alert
    personalization_level: str = "standard"  # basic, standard, premium
    include_insights: bool = True
    tone: str = "professional"  # professional, friendly, formal
    
class BulkUpdateRequest(BaseModel):
    advisor_id: int
    client_ids: List[int]
    content_type: str
    schedule_time: Optional[datetime] = None
    custom_message: Optional[str] = None
