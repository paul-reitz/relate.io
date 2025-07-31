import os
import json
import logging
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from dataclasses import dataclass

from enhanced_models import *
from enhanced_database import get_db_connection

logger = logging.getLogger(__name__)

@dataclass
class IntegrationConfig:
    """Configuration for external integrations"""
    name: str
    api_url: str
    api_key: str
    auth_type: str  # 'api_key', 'oauth', 'basic'
    rate_limit: int = 100  # requests per minute
    timeout: int = 30

class IntegrationManager:
    """Manages integrations with external portfolio management systems"""
    
    def __init__(self):
        self.integrations = {
            'momentum': IntegrationConfig(
                name='Momentum',
                api_url=os.getenv('MOMENTUM_API_URL', 'https://api.momentum.co.za'),
                api_key=os.getenv('MOMENTUM_API_KEY', ''),
                auth_type='api_key'
            ),
            'schwab': IntegrationConfig(
                name='Charles Schwab',
                api_url=os.getenv('SCHWAB_API_URL', 'https://api.schwabapi.com'),
                api_key=os.getenv('SCHWAB_API_KEY', ''),
                auth_type='oauth'
            ),
            'fidelity': IntegrationConfig(
                name='Fidelity',
                api_url=os.getenv('FIDELITY_API_URL', 'https://api.fidelity.com'),
                api_key=os.getenv('FIDELITY_API_KEY', ''),
                auth_type='oauth'
            ),
            'alpha_vantage': IntegrationConfig(
                name='Alpha Vantage',
                api_url='https://www.alphavantage.co/query',
                api_key=os.getenv('ALPHA_VANTAGE_API_KEY', ''),
                auth_type='api_key'
            )
        }
        
        self.session = None
        logger.info("Integration Manager initialized")

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def sync_with_momentum(self, advisor_id: int) -> Dict[str, Any]:
        """Sync client portfolios from Momentum"""
        
        config = self.integrations['momentum']
        if not config.api_key:
            logger.warning("Momentum API key not configured")
            return {'success': False, 'error': 'API key not configured'}

        try:
            # Mock Momentum API integration (replace with actual API calls)
            mock_data = await self._mock_momentum_data(advisor_id)
            
            # Process and store the data
            results = await self._process_momentum_data(advisor_id, mock_data)
            
            logger.info(f"Momentum sync completed for advisor {advisor_id}")
            return {
                'success': True,
                'clients_synced': results['clients_synced'],
                'portfolios_updated': results['portfolios_updated'],
                'holdings_updated': results['holdings_updated']
            }
            
        except Exception as e:
            logger.error(f"Error syncing with Momentum: {e}")
            return {'success': False, 'error': str(e)}

    async def _mock_momentum_data(self, advisor_id: int) -> Dict[str, Any]:
        """Mock Momentum API data (replace with actual API integration)"""
        
        # This would be replaced with actual Momentum API calls
        return {
            'clients': [
                {
                    'external_id': 'MOM_001',
                    'name': 'John Smith',
                    'email': 'john.smith@email.com',
                    'phone': '+27123456789',
                    'risk_profile': 'moderate',
                    'portfolio': {
                        'total_value': 250000.00,
                        'cash_balance': 15000.00,
                        'invested_amount': 235000.00,
                        'unrealized_pnl': 12500.00,
                        'realized_pnl': 8750.00,
                        'risk_score': 6.5,
                        'holdings': [
                            {
                                'symbol': 'AAPL',
                                'company_name': 'Apple Inc.',
                                'quantity': 100,
                                'current_price': 175.50,
                                'cost_basis': 165.00,
                                'sector': 'Technology',
                                'asset_class': 'equity'
                            },
                            {
                                'symbol': 'GOOGL',
                                'company_name': 'Alphabet Inc.',
                                'quantity': 50,
                                'current_price': 142.30,
                                'cost_basis': 135.00,
                                'sector': 'Technology',
                                'asset_class': 'equity'
                            }
                        ]
                    }
                },
                {
                    'external_id': 'MOM_002',
                    'name': 'Sarah Johnson',
                    'email': 'sarah.johnson@email.com',
                    'phone': '+27987654321',
                    'risk_profile': 'conservative',
                    'portfolio': {
                        'total_value': 180000.00,
                        'cash_balance': 25000.00,
                        'invested_amount': 155000.00,
                        'unrealized_pnl': 5500.00,
                        'realized_pnl': 3200.00,
                        'risk_score': 4.2,
                        'holdings': [
                            {
                                'symbol': 'BND',
                                'company_name': 'Vanguard Total Bond Market ETF',
                                'quantity': 500,
                                'current_price': 78.45,
                                'cost_basis': 80.00,
                                'sector': 'Fixed Income',
                                'asset_class': 'bond'
                            }
                        ]
                    }
                }
            ]
        }

    async def _process_momentum_data(self, advisor_id: int, data: Dict[str, Any]) -> Dict[str, int]:
        """Process and store Momentum data in our database"""
        
        conn = get_db_connection()
        clients_synced = 0
        portfolios_updated = 0
        holdings_updated = 0
        
        try:
            with conn:
                with conn.cursor() as cur:
                    for client_data in data['clients']:
                        # Insert or update client
                        cur.execute("""
                            INSERT INTO enhanced_clients (
                                advisor_id, name, email, phone, risk_tolerance, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (email) DO UPDATE SET
                                name = EXCLUDED.name,
                                phone = EXCLUDED.phone,
                                risk_tolerance = EXCLUDED.risk_tolerance
                            RETURNING id
                        """, (
                            advisor_id,
                            client_data['name'],
                            client_data['email'],
                            client_data.get('phone'),
                            client_data.get('risk_profile', 'moderate'),
                            datetime.now()
                        ))
                        
                        client_id = cur.fetchone()['id']
                        clients_synced += 1
                        
                        # Insert or update portfolio
                        portfolio_data = client_data['portfolio']
                        cur.execute("""
                            INSERT INTO portfolios (
                                client_id, total_value, cash_balance, invested_amount,
                                unrealized_pnl, realized_pnl, risk_score, last_sync, created_at
                            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (client_id) DO UPDATE SET
                                total_value = EXCLUDED.total_value,
                                cash_balance = EXCLUDED.cash_balance,
                                invested_amount = EXCLUDED.invested_amount,
                                unrealized_pnl = EXCLUDED.unrealized_pnl,
                                realized_pnl = EXCLUDED.realized_pnl,
                                risk_score = EXCLUDED.risk_score,
                                last_sync = EXCLUDED.last_sync
                            RETURNING id
                        """, (
                            client_id,
                            portfolio_data['total_value'],
                            portfolio_data['cash_balance'],
                            portfolio_data['invested_amount'],
                            portfolio_data['unrealized_pnl'],
                            portfolio_data['realized_pnl'],
                            portfolio_data['risk_score'],
                            datetime.now(),
                            datetime.now()
                        ))
                        
                        portfolio_id = cur.fetchone()['id']
                        portfolios_updated += 1
                        
                        # Clear existing holdings and insert new ones
                        cur.execute("DELETE FROM holdings WHERE portfolio_id = %s", (portfolio_id,))
                        
                        for holding_data in portfolio_data['holdings']:
                            market_value = holding_data['quantity'] * holding_data['current_price']
                            weight_percentage = (market_value / portfolio_data['total_value']) * 100
                            
                            cur.execute("""
                                INSERT INTO holdings (
                                    portfolio_id, symbol, company_name, quantity,
                                    current_price, cost_basis, market_value,
                                    weight_percentage, sector, asset_class, last_updated
                                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                portfolio_id,
                                holding_data['symbol'],
                                holding_data.get('company_name'),
                                holding_data['quantity'],
                                holding_data['current_price'],
                                holding_data['cost_basis'],
                                market_value,
                                weight_percentage,
                                holding_data.get('sector'),
                                holding_data['asset_class'],
                                datetime.now()
                            ))
                            
                            holdings_updated += 1
                            
        except Exception as e:
            logger.error(f"Error processing Momentum data: {e}")
            raise
        finally:
            conn.close()
            
        return {
            'clients_synced': clients_synced,
            'portfolios_updated': portfolios_updated,
            'holdings_updated': holdings_updated
        }

    async def sync_with_custodian(self, custodian_type: str, advisor_id: int) -> Dict[str, Any]:
        """Sync with custodian APIs (Schwab, Fidelity, etc.)"""
        
        if custodian_type not in self.integrations:
            return {'success': False, 'error': f'Unsupported custodian: {custodian_type}'}
            
        config = self.integrations[custodian_type]
        
        try:
            # Mock custodian integration
            if custodian_type == 'schwab':
                return await self._sync_schwab(advisor_id, config)
            elif custodian_type == 'fidelity':
                return await self._sync_fidelity(advisor_id, config)
            else:
                return {'success': False, 'error': 'Integration not implemented'}
                
        except Exception as e:
            logger.error(f"Error syncing with {custodian_type}: {e}")
            return {'success': False, 'error': str(e)}

    async def _sync_schwab(self, advisor_id: int, config: IntegrationConfig) -> Dict[str, Any]:
        """Mock Schwab integration"""
        # This would implement actual Schwab API integration
        logger.info(f"Mock Schwab sync for advisor {advisor_id}")
        return {'success': True, 'message': 'Schwab sync completed (mock)'}

    async def _sync_fidelity(self, advisor_id: int, config: IntegrationConfig) -> Dict[str, Any]:
        """Mock Fidelity integration"""
        # This would implement actual Fidelity API integration
        logger.info(f"Mock Fidelity sync for advisor {advisor_id}")
        return {'success': True, 'message': 'Fidelity sync completed (mock)'}

    async def fetch_market_data(self, symbols: List[str]) -> Dict[str, MarketData]:
        """Fetch real-time market data for given symbols"""
        
        market_data = {}
        
        try:
            # Use yfinance for real market data
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                history = ticker.history(period="2d")
                
                if not history.empty:
                    current_price = history['Close'][-1]
                    prev_price = history['Close'][-2] if len(history) > 1 else current_price
                    change_percent = ((current_price - prev_price) / prev_price) * 100
                    
                    market_data[symbol] = MarketData(
                        symbol=symbol,
                        price=float(current_price),
                        change_percent=float(change_percent),
                        volume=int(history['Volume'][-1]) if 'Volume' in history else 0,
                        market_cap=info.get('marketCap'),
                        pe_ratio=info.get('trailingPE'),
                        dividend_yield=info.get('dividendYield'),
                        sector=info.get('sector'),
                        last_updated=datetime.now()
                    )
                    
                    # Store in database
                    await self._store_market_data(market_data[symbol])
                    
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            
        return market_data

    async def _store_market_data(self, data: MarketData):
        """Store market data in database"""
        
        conn = get_db_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO market_data (
                            symbol, price, change_percent, volume, market_cap,
                            pe_ratio, dividend_yield, sector, last_updated
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (symbol) DO UPDATE SET
                            price = EXCLUDED.price,
                            change_percent = EXCLUDED.change_percent,
                            volume = EXCLUDED.volume,
                            market_cap = EXCLUDED.market_cap,
                            pe_ratio = EXCLUDED.pe_ratio,
                            dividend_yield = EXCLUDED.dividend_yield,
                            sector = EXCLUDED.sector,
                            last_updated = EXCLUDED.last_updated
                    """, (
                        data.symbol, data.price, data.change_percent, data.volume,
                        data.market_cap, data.pe_ratio, data.dividend_yield,
                        data.sector, data.last_updated
                    ))
        finally:
            conn.close()

    async def fetch_alpha_vantage_data(self, symbol: str, data_type: str = 'DAILY') -> Dict[str, Any]:
        """Fetch data from Alpha Vantage API"""
        
        config = self.integrations['alpha_vantage']
        if not config.api_key:
            logger.warning("Alpha Vantage API key not configured")
            return {}

        params = {
            'function': f'TIME_SERIES_{data_type}',
            'symbol': symbol,
            'apikey': config.api_key,
            'outputsize': 'compact'
        }
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            async with self.session.get(config.api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Alpha Vantage API error: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage data: {e}")
            return {}

    async def bulk_sync_portfolios(self, advisor_id: int, integration_type: str = 'momentum') -> Dict[str, Any]:
        """Bulk sync all portfolios for an advisor"""
        
        try:
            if integration_type == 'momentum':
                result = await self.sync_with_momentum(advisor_id)
            else:
                result = await self.sync_with_custodian(integration_type, advisor_id)
                
            # Update market data for all holdings
            await self._update_all_market_data(advisor_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk sync: {e}")
            return {'success': False, 'error': str(e)}

    async def _update_all_market_data(self, advisor_id: int):
        """Update market data for all holdings of an advisor's clients"""
        
        conn = get_db_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Get all unique symbols for this advisor's clients
                    cur.execute("""
                        SELECT DISTINCT h.symbol
                        FROM holdings h
                        JOIN portfolios p ON h.portfolio_id = p.id
                        JOIN enhanced_clients c ON p.client_id = c.id
                        WHERE c.advisor_id = %s
                    """, (advisor_id,))
                    
                    symbols = [row['symbol'] for row in cur.fetchall()]
                    
            if symbols:
                await self.fetch_market_data(symbols)
                logger.info(f"Updated market data for {len(symbols)} symbols")
                
        except Exception as e:
            logger.error(f"Error updating market data: {e}")
        finally:
            conn.close()

    async def schedule_regular_sync(self, advisor_id: int, integration_type: str, frequency: str = 'daily'):
        """Schedule regular portfolio synchronization"""
        
        # This would integrate with Celery for scheduling
        # For now, just log the scheduling request
        logger.info(f"Scheduled {frequency} sync for advisor {advisor_id} with {integration_type}")
        
        # In production, this would create a Celery periodic task
        return {
            'success': True,
            'message': f'Scheduled {frequency} sync with {integration_type}',
            'advisor_id': advisor_id,
            'frequency': frequency
        }

    def get_integration_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations"""
        
        status = {}
        for name, config in self.integrations.items():
            status[name] = {
                'configured': bool(config.api_key),
                'api_url': config.api_url,
                'auth_type': config.auth_type,
                'rate_limit': config.rate_limit
            }
            
        return status

# Global instance
integration_manager = IntegrationManager()

# Convenience functions
async def sync_momentum_portfolios(advisor_id: int) -> Dict[str, Any]:
    """Convenience function to sync Momentum portfolios"""
    async with integration_manager:
        return await integration_manager.sync_with_momentum(advisor_id)

async def update_market_data(symbols: List[str]) -> Dict[str, MarketData]:
    """Convenience function to update market data"""
    async with integration_manager:
        return await integration_manager.fetch_market_data(symbols)

async def bulk_portfolio_sync(advisor_id: int, integration_type: str = 'momentum') -> Dict[str, Any]:
    """Convenience function for bulk portfolio sync"""
    async with integration_manager:
        return await integration_manager.bulk_sync_portfolios(advisor_id, integration_type)
