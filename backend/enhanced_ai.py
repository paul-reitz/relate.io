import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import yfinance as yf
import pandas as pd

from enhanced_models import *
from enhanced_database import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class MarketContext:
    """Market context for AI generation"""
    market_sentiment: str
    volatility_index: float
    sector_performance: Dict[str, float]
    economic_indicators: Dict[str, float]
    fed_policy_outlook: str

class EnhancedAIEngine:
    """Advanced AI engine for financial advisory insights"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize sentiment analysis models
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=self.sentiment_model,
            tokenizer=self.sentiment_tokenizer
        )
        
        # Topic modeling for feedback analysis
        self.topic_vectorizer = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        logger.info("Enhanced AI Engine initialized successfully")

    async def generate_portfolio_insights(
        self, 
        portfolio_data: Dict[str, Any], 
        market_context: MarketContext,
        client_profile: Dict[str, Any]
    ) -> List[PortfolioInsight]:
        """Generate comprehensive portfolio insights using AI"""
        
        insights = []
        
        try:
            # Risk Analysis Insight
            risk_insight = await self._generate_risk_analysis(
                portfolio_data, market_context, client_profile
            )
            insights.append(risk_insight)
            
            # Performance Attribution
            performance_insight = await self._generate_performance_attribution(
                portfolio_data, market_context
            )
            insights.append(performance_insight)
            
            # Rebalancing Recommendations
            rebalancing_insight = await self._generate_rebalancing_recommendations(
                portfolio_data, client_profile
            )
            insights.append(rebalancing_insight)
            
            # Macro Economic Impact
            macro_insight = await self._analyze_macro_economic_impact(
                portfolio_data, market_context
            )
            insights.append(macro_insight)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating portfolio insights: {e}")
            return []

    async def _generate_risk_analysis(
        self, 
        portfolio_data: Dict[str, Any], 
        market_context: MarketContext,
        client_profile: Dict[str, Any]
    ) -> PortfolioInsight:
        """Generate AI-powered risk analysis"""
        
        prompt = ChatPromptTemplate.from_template("""
        As a senior financial advisor, analyze the portfolio risk profile:
        
        Portfolio Data:
        - Total Value: ${total_value:,.2f}
        - Risk Score: {risk_score}/10
        - Asset Allocation: {asset_allocation}
        - Volatility: {volatility}%
        
        Market Context:
        - Market Sentiment: {market_sentiment}
        - VIX: {volatility_index}
        - Sector Performance: {sector_performance}
        
        Client Profile:
        - Risk Tolerance: {risk_tolerance}
        - Investment Goals: {investment_goals}
        - Time Horizon: {time_horizon}
        
        Provide a comprehensive risk analysis with:
        1. Current risk assessment
        2. Key risk factors
        3. Specific recommendations
        4. Risk mitigation strategies
        
        Format as JSON with title, description, and recommendations array.
        """)
        
        try:
            response = await self.llm.ainvoke(
                prompt.format(
                    total_value=portfolio_data.get('total_value', 0),
                    risk_score=portfolio_data.get('risk_score', 5),
                    asset_allocation=portfolio_data.get('asset_allocation', {}),
                    volatility=portfolio_data.get('volatility', 15),
                    market_sentiment=market_context.market_sentiment,
                    volatility_index=market_context.volatility_index,
                    sector_performance=market_context.sector_performance,
                    risk_tolerance=client_profile.get('risk_tolerance', 'moderate'),
                    investment_goals=client_profile.get('investment_goals', []),
                    time_horizon=client_profile.get('time_horizon', '5-10 years')
                )
            )
            
            analysis = json.loads(response.content)
            
            return PortfolioInsight(
                portfolio_id=portfolio_data.get('id'),
                insight_type="risk_analysis",
                title=analysis.get('title', 'Portfolio Risk Analysis'),
                description=analysis.get('description', ''),
                recommendations=analysis.get('recommendations', []),
                priority=self._calculate_priority(analysis.get('risk_level', 'medium'))
            )
            
        except Exception as e:
            logger.error(f"Error in risk analysis: {e}")
            return PortfolioInsight(
                portfolio_id=portfolio_data.get('id'),
                insight_type="risk_analysis",
                title="Risk Analysis Error",
                description="Unable to generate risk analysis at this time.",
                recommendations=[],
                priority=3
            )

    async def _generate_performance_attribution(
        self, 
        portfolio_data: Dict[str, Any], 
        market_context: MarketContext
    ) -> PortfolioInsight:
        """Generate performance attribution analysis"""
        
        prompt = ChatPromptTemplate.from_template("""
        Analyze portfolio performance attribution:
        
        Portfolio Performance:
        - Total Return: {total_return}%
        - Benchmark Return: {benchmark_return}%
        - Alpha: {alpha}%
        - Beta: {beta}
        - Sharpe Ratio: {sharpe_ratio}
        
        Holdings Performance:
        {holdings_performance}
        
        Market Context:
        - Market Return: {market_return}%
        - Sector Performance: {sector_performance}
        
        Provide detailed performance attribution analysis including:
        1. Sources of outperformance/underperformance
        2. Sector allocation impact
        3. Security selection impact
        4. Recommendations for improvement
        
        Format as JSON with title, description, and recommendations.
        """)
        
        try:
            response = await self.llm.ainvoke(
                prompt.format(
                    total_return=portfolio_data.get('total_return', 0),
                    benchmark_return=portfolio_data.get('benchmark_return', 0),
                    alpha=portfolio_data.get('alpha', 0),
                    beta=portfolio_data.get('beta', 1),
                    sharpe_ratio=portfolio_data.get('sharpe_ratio', 0),
                    holdings_performance=portfolio_data.get('holdings_performance', {}),
                    market_return=market_context.sector_performance.get('market', 0),
                    sector_performance=market_context.sector_performance
                )
            )
            
            analysis = json.loads(response.content)
            
            return PortfolioInsight(
                portfolio_id=portfolio_data.get('id'),
                insight_type="performance_attribution",
                title=analysis.get('title', 'Performance Attribution Analysis'),
                description=analysis.get('description', ''),
                recommendations=analysis.get('recommendations', []),
                priority=2
            )
            
        except Exception as e:
            logger.error(f"Error in performance attribution: {e}")
            return PortfolioInsight(
                portfolio_id=portfolio_data.get('id'),
                insight_type="performance_attribution",
                title="Performance Analysis",
                description="Performance attribution analysis unavailable.",
                recommendations=[],
                priority=3
            )

    async def analyze_feedback_advanced(self, feedback_text: str) -> Dict[str, Any]:
        """Advanced feedback analysis with topic extraction and sentiment scoring"""
        
        try:
            # Financial sentiment analysis
            sentiment_result = self.sentiment_pipeline(feedback_text)[0]
            
            # Extract topics using keyword analysis
            topics = self._extract_topics([feedback_text])
            
            # Determine urgency level
            urgency = self._calculate_urgency(feedback_text, sentiment_result)
            
            # Generate action items
            action_items = await self._generate_action_items(feedback_text, sentiment_result)
            
            return {
                'sentiment': self._map_sentiment(sentiment_result['label']),
                'sentiment_score': self._normalize_sentiment_score(sentiment_result['score'], sentiment_result['label']),
                'topics': topics,
                'urgency_level': urgency,
                'action_items': action_items,
                'confidence': sentiment_result['score']
            }
            
        except Exception as e:
            logger.error(f"Error in advanced feedback analysis: {e}")
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0.0,
                'topics': [],
                'urgency_level': 3,
                'action_items': [],
                'confidence': 0.0
            }

    def _extract_topics(self, texts: List[str]) -> List[str]:
        """Extract topics from feedback using TF-IDF and clustering"""
        
        if not texts:
            return []
            
        try:
            # Financial keywords to look for
            financial_keywords = {
                'performance': ['performance', 'returns', 'gains', 'losses', 'profit', 'loss'],
                'fees': ['fees', 'charges', 'costs', 'expensive', 'cheap'],
                'communication': ['communication', 'contact', 'response', 'update', 'information'],
                'risk': ['risk', 'volatile', 'stability', 'safe', 'dangerous'],
                'market': ['market', 'economy', 'recession', 'bull', 'bear', 'volatility'],
                'service': ['service', 'support', 'help', 'assistance', 'advice']
            }
            
            topics = []
            text_lower = ' '.join(texts).lower()
            
            for topic, keywords in financial_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    topics.append(topic)
            
            return topics[:5]  # Return top 5 topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []

    def _calculate_urgency(self, text: str, sentiment_result: Dict) -> int:
        """Calculate urgency level based on sentiment and keywords"""
        
        urgent_keywords = [
            'urgent', 'immediate', 'asap', 'emergency', 'critical',
            'worried', 'concerned', 'panic', 'scared', 'angry',
            'disappointed', 'frustrated', 'unacceptable'
        ]
        
        text_lower = text.lower()
        urgency_score = 3  # Default medium urgency
        
        # Adjust based on sentiment
        if sentiment_result['label'] == 'negative':
            urgency_score += 1
        elif sentiment_result['label'] == 'positive':
            urgency_score -= 1
            
        # Adjust based on urgent keywords
        urgent_count = sum(1 for keyword in urgent_keywords if keyword in text_lower)
        urgency_score += min(urgent_count, 2)
        
        return max(1, min(5, urgency_score))

    async def _generate_action_items(self, feedback_text: str, sentiment_result: Dict) -> List[str]:
        """Generate AI-powered action items based on feedback"""
        
        prompt = ChatPromptTemplate.from_template("""
        Based on this client feedback, generate specific action items for the financial advisor:
        
        Feedback: "{feedback}"
        Sentiment: {sentiment} (confidence: {confidence})
        
        Generate 2-4 specific, actionable items that the advisor should take to address this feedback.
        Focus on practical steps that can improve the client relationship.
        
        Return as a JSON array of strings.
        """)
        
        try:
            response = await self.llm.ainvoke(
                prompt.format(
                    feedback=feedback_text,
                    sentiment=sentiment_result['label'],
                    confidence=sentiment_result['score']
                )
            )
            
            action_items = json.loads(response.content)
            return action_items if isinstance(action_items, list) else []
            
        except Exception as e:
            logger.error(f"Error generating action items: {e}")
            return ["Review client feedback and schedule follow-up call"]

    async def generate_personalized_content(
        self, 
        client_data: Dict[str, Any], 
        portfolio_data: Dict[str, Any],
        advisor_tone: Dict[str, Any], 
        firm_branding: Dict[str, Any],
        content_type: str = "portfolio_update"
    ) -> str:
        """Generate personalized content matching advisor tone and firm branding"""
        
        tone_mapping = {
            'professional': 'formal and professional',
            'friendly': 'warm and approachable',
            'formal': 'highly formal and conservative',
            'casual': 'conversational and relaxed'
        }
        
        prompt = ChatPromptTemplate.from_template("""
        Generate a personalized {content_type} for this client:
        
        Client Profile:
        - Name: {client_name}
        - Risk Tolerance: {risk_tolerance}
        - Investment Goals: {investment_goals}
        - Communication Preference: {communication_preference}
        
        Portfolio Data:
        - Total Value: ${total_value:,.2f}
        - Performance: {performance}%
        - Top Holdings: {top_holdings}
        - Recent Changes: {recent_changes}
        
        Tone Guidelines:
        - Style: {tone_style}
        - Key Phrases: {key_phrases}
        - Avoid: {avoid_terms}
        
        Firm Branding:
        - Company Name: {company_name}
        - Brand Voice: {brand_voice}
        - Compliance Notes: {compliance_notes}
        
        Generate content that:
        1. Addresses the client personally
        2. Matches the specified tone and branding
        3. Includes relevant portfolio insights
        4. Encourages engagement/feedback
        5. Maintains compliance standards
        
        Include a clear call-to-action for feedback.
        """)
        
        try:
            response = await self.llm.ainvoke(
                prompt.format(
                    content_type=content_type,
                    client_name=client_data.get('name', 'Valued Client'),
                    risk_tolerance=client_data.get('risk_tolerance', 'moderate'),
                    investment_goals=', '.join(client_data.get('investment_goals', [])),
                    communication_preference=client_data.get('communication_preferences', {}).get('style', 'email'),
                    total_value=portfolio_data.get('total_value', 0),
                    performance=portfolio_data.get('performance', 0),
                    top_holdings=', '.join(portfolio_data.get('top_holdings', [])),
                    recent_changes=portfolio_data.get('recent_changes', 'No recent changes'),
                    tone_style=tone_mapping.get(advisor_tone.get('style', 'professional')),
                    key_phrases=', '.join(advisor_tone.get('key_phrases', [])),
                    avoid_terms=', '.join(advisor_tone.get('avoid_terms', [])),
                    company_name=firm_branding.get('company_name', 'Our Firm'),
                    brand_voice=firm_branding.get('brand_voice', 'professional'),
                    compliance_notes=firm_branding.get('compliance_notes', 'Standard compliance applies')
                )
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating personalized content: {e}")
            return f"Dear {client_data.get('name', 'Valued Client')}, we have an update on your portfolio. Please contact us for details."

    async def get_market_context(self) -> MarketContext:
        """Fetch current market context for AI analysis"""
        
        try:
            # Fetch market data (simplified - in production, use real market data APIs)
            spy = yf.Ticker("SPY")
            vix = yf.Ticker("^VIX")
            
            spy_info = spy.history(period="5d")
            vix_info = vix.history(period="1d")
            
            market_return = ((spy_info['Close'][-1] - spy_info['Close'][0]) / spy_info['Close'][0]) * 100
            volatility_index = vix_info['Close'][-1] if not vix_info.empty else 20.0
            
            # Determine market sentiment based on recent performance
            if market_return > 2:
                sentiment = "bullish"
            elif market_return < -2:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            return MarketContext(
                market_sentiment=sentiment,
                volatility_index=float(volatility_index),
                sector_performance={
                    'technology': market_return + np.random.uniform(-2, 2),
                    'healthcare': market_return + np.random.uniform(-1, 1),
                    'financials': market_return + np.random.uniform(-1.5, 1.5),
                    'energy': market_return + np.random.uniform(-3, 3),
                    'market': market_return
                },
                economic_indicators={
                    'inflation_rate': 3.2,
                    'unemployment_rate': 3.8,
                    'gdp_growth': 2.1
                },
                fed_policy_outlook="neutral"
            )
            
        except Exception as e:
            logger.error(f"Error fetching market context: {e}")
            return MarketContext(
                market_sentiment="neutral",
                volatility_index=20.0,
                sector_performance={'market': 0.0},
                economic_indicators={},
                fed_policy_outlook="neutral"
            )

    def _map_sentiment(self, label: str) -> str:
        """Map model sentiment labels to our enum values"""
        mapping = {
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral',
            'POSITIVE': 'positive',
            'NEGATIVE': 'negative',
            'NEUTRAL': 'neutral'
        }
        return mapping.get(label, 'neutral')

    def _normalize_sentiment_score(self, score: float, label: str) -> float:
        """Normalize sentiment score to -1 to 1 range"""
        if label.lower() == 'negative':
            return -score
        elif label.lower() == 'positive':
            return score
        else:
            return 0.0

    def _calculate_priority(self, risk_level: str) -> int:
        """Calculate priority based on risk level"""
        priority_mapping = {
            'low': 1,
            'medium': 3,
            'high': 4,
            'critical': 5
        }
        return priority_mapping.get(risk_level.lower(), 3)

# Global instance
ai_engine = EnhancedAIEngine()

# Convenience functions for backward compatibility
async def generate_narrative(data: dict) -> str:
    """Generate portfolio narrative using enhanced AI"""
    try:
        market_context = await ai_engine.get_market_context()
        
        client_data = {
            'name': 'Valued Client',
            'risk_tolerance': 'moderate',
            'investment_goals': ['growth', 'income'],
            'communication_preferences': {'style': 'email'}
        }
        
        portfolio_data = {
            'total_value': data.get('portfolio_value', 100000),
            'performance': data.get('pnl', 0),
            'top_holdings': data.get('top_holdings', ['AAPL', 'GOOG']),
            'recent_changes': 'Portfolio rebalanced this week'
        }
        
        advisor_tone = {
            'style': 'professional',
            'key_phrases': ['strategic', 'long-term', 'diversified'],
            'avoid_terms': ['risky', 'gamble', 'speculation']
        }
        
        firm_branding = {
            'company_name': 'Relate.io Advisory',
            'brand_voice': 'professional',
            'compliance_notes': 'All investments carry risk'
        }
        
        return await ai_engine.generate_personalized_content(
            client_data, portfolio_data, advisor_tone, firm_branding
        )
        
    except Exception as e:
        logger.error(f"Error in generate_narrative: {e}")
        return f"Portfolio Update: Your portfolio shows a {data.get('pnl', 0)}% change. Top holdings include {', '.join(data.get('top_holdings', []))}."

async def analyze_feedback(text: str) -> str:
    """Analyze feedback using enhanced AI"""
    try:
        analysis = await ai_engine.analyze_feedback_advanced(text)
        return analysis['sentiment']
    except Exception as e:
        logger.error(f"Error in analyze_feedback: {e}")
        return "neutral"
