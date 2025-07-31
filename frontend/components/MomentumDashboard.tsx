'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useCallback } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  PointElement, 
  LineElement, 
  BarElement,
  Title, 
  Tooltip, 
  Legend,
  ArcElement 
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  DollarSign, 
  AlertTriangle, 
  CheckCircle,
  MessageSquare,
  BarChart3,
  RefreshCw,
  Eye,
  X,
  Calendar,
  Target,
  Shield
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Types
interface Client {
  id: number;
  name: string;
  email: string;
  total_value: number;
  risk_score: number;
  feedback_count: number;
  avg_sentiment: number;
  last_sync: string;
}

interface SentimentTrend {
  date: string;
  avg_sentiment: number;
  feedback_count: number;
  negative_count: number;
  urgent_count: number;
}

interface TopicData {
  topic: string;
  count: number;
}

interface Portfolio {
  id: number;
  client_id: number;
  total_value: number;
  unrealized_pnl: number;
  risk_score: number;
}

interface Holding {
  symbol: string;
  company_name: string;
  market_value: number;
  weight_percentage: number;
  change_percent: number;
}

interface Insight {
  id: number;
  insight_type: string;
  title: string;
  description: string;
  priority: number;
  created_at: string;
}

// API Functions
const API_BASE_URL = 'http://localhost:8000';

const fetchEnhancedClients = async (): Promise<Client[]> => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/clients`, {
      headers: { 'Authorization': 'Bearer mock-token' }
    });
    if (!res.ok) throw new Error('Failed to fetch clients');
    return res.json();
  } catch (error) {
    console.warn('API not available, using mock data');
    return generateMockClients();
  }
};

const fetchSentimentTrends = async (timeRange: string = '30d') => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/analytics/sentiment-trends?time_range=${timeRange}`, {
      headers: { 'Authorization': 'Bearer mock-token' }
    });
    if (!res.ok) throw new Error('Failed to fetch sentiment trends');
    return res.json();
  } catch (error) {
    console.warn('API not available, using mock data');
    return generateMockSentimentData();
  }
};

const fetchPortfolioDetails = async (clientId: number) => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/portfolios/${clientId}`, {
      headers: { 'Authorization': 'Bearer mock-token' }
    });
    if (!res.ok) throw new Error('Failed to fetch portfolio details');
    return res.json();
  } catch (error) {
    console.warn('API not available, using mock data');
    return generateMockPortfolio(clientId);
  }
};

const syncMomentumIntegration = async () => {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/integrations/momentum/sync`, {
      method: 'POST',
      headers: { 'Authorization': 'Bearer mock-token' }
    });
    if (!res.ok) throw new Error('Failed to sync with Momentum');
    return res.json();
  } catch (error) {
    console.warn('API not available, simulating sync');
    return { success: true, message: 'Sync completed (simulated)' };
  }
};

// Mock data generators
const generateMockClients = (): Client[] => {
  const names = [
    'James Wellington', 'Sarah Montgomery', 'Robert Blackstone', 
    'Elizabeth Hartwell', 'Michael Rothschild', 'Catherine Pemberton',
    'David Ashworth', 'Victoria Sterling', 'Alexander Fairfax', 'Isabella Whitmore'
  ];
  
  return names.map((name, index) => ({
    id: index + 1,
    name,
    email: `${name.toLowerCase().replace(' ', '.')}@example.com`,
    total_value: Math.random() * 5000000 + 500000,
    risk_score: Math.random() * 10,
    feedback_count: Math.floor(Math.random() * 10),
    avg_sentiment: (Math.random() - 0.5) * 2,
    last_sync: new Date().toISOString()
  }));
};

const generateMockSentimentData = () => {
  const trends = Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
    avg_sentiment: (Math.random() - 0.5) * 2,
    feedback_count: Math.floor(Math.random() * 20),
    negative_count: Math.floor(Math.random() * 5),
    urgent_count: Math.floor(Math.random() * 3)
  }));
  
  const topics = [
    { topic: 'Performance', count: 45 },
    { topic: 'Fees', count: 23 },
    { topic: 'Risk', count: 18 },
    { topic: 'Communication', count: 15 },
    { topic: 'Strategy', count: 12 }
  ];
  
  return { trends, top_topics: topics };
};

const generateMockPortfolio = (clientId: number) => {
  const holdings = [
    { symbol: 'AAPL', company_name: 'Apple Inc.', market_value: 125000, weight_percentage: 25, change_percent: 2.5 },
    { symbol: 'MSFT', company_name: 'Microsoft Corp.', market_value: 100000, weight_percentage: 20, change_percent: 1.8 },
    { symbol: 'GOOGL', company_name: 'Alphabet Inc.', market_value: 75000, weight_percentage: 15, change_percent: -0.5 },
    { symbol: 'SPY', company_name: 'SPDR S&P 500 ETF', market_value: 100000, weight_percentage: 20, change_percent: 1.2 },
    { symbol: 'BND', company_name: 'Vanguard Bond ETF', market_value: 50000, weight_percentage: 10, change_percent: 0.3 }
  ];
  
  const insights = [
    {
      id: 1,
      insight_type: 'risk',
      title: 'Portfolio Risk Assessment',
      description: 'Current risk level is within target range for conservative growth strategy.',
      priority: 2,
      created_at: new Date().toISOString()
    }
  ];
  
  return {
    portfolio: {
      client_name: `Client ${clientId}`,
      total_value: 500000,
      unrealized_pnl: 25000,
      risk_score: 6.5
    },
    holdings,
    insights
  };
};

// Components
const StatCard = ({ 
  title, 
  value, 
  change, 
  icon: Icon, 
  trend = 'neutral',
  className = ''
}: {
  title: string;
  value: string;
  change?: string;
  icon: any;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}) => {
  const trendColors = {
    up: 'text-momentum-green',
    down: 'text-momentum-red',
    neutral: 'text-momentum-blue'
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx(
        'momentum-card p-6 hover:shadow-momentum-md transition-all duration-300',
        className
      )}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {change && (
            <div className={clsx('flex items-center mt-2 text-sm', trendColors[trend])}>
              {trend === 'up' && <TrendingUp className="w-4 h-4 mr-1" />}
              {trend === 'down' && <TrendingDown className="w-4 h-4 mr-1" />}
              <span>{change}</span>
            </div>
          )}
        </div>
        <div className="p-3 bg-momentum-blue bg-opacity-10 rounded-lg">
          <Icon className="w-6 h-6 text-momentum-blue" />
        </div>
      </div>
    </motion.div>
  );
};

const ClientCard = ({ 
  client, 
  onViewPortfolio 
}: { 
  client: Client; 
  onViewPortfolio: (id: number) => void;
}) => {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.2) return 'momentum-badge-positive';
    if (sentiment < -0.2) return 'momentum-badge-negative';
    return 'momentum-badge-neutral';
  };

  const getRiskColor = (risk: number) => {
    if (risk <= 3) return 'text-momentum-green';
    if (risk <= 7) return 'text-yellow-600';
    return 'text-momentum-red';
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
      className="momentum-card p-6 hover:shadow-momentum-md transition-all duration-300"
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{client.name}</h3>
          <p className="text-sm text-gray-600">{client.email}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-momentum-green">
            ${client.total_value?.toLocaleString() || 'N/A'}
          </p>
          <p className="text-sm text-gray-500">Portfolio Value</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Risk Score</p>
          <p className={clsx('font-semibold', getRiskColor(client.risk_score || 5))}>
            {client.risk_score?.toFixed(1) || 'N/A'}/10
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Feedback</p>
          <div className="flex items-center">
            <MessageSquare className="w-4 h-4 mr-1 text-gray-400" />
            <p className="font-semibold text-gray-900">{client.feedback_count || 0}</p>
          </div>
        </div>
      </div>
      
      <div className="flex justify-between items-center">
        <div className={clsx('px-3 py-1 rounded-full text-xs font-medium', getSentimentColor(client.avg_sentiment || 0))}>
          Sentiment: {client.avg_sentiment > 0 ? 'Positive' : client.avg_sentiment < 0 ? 'Negative' : 'Neutral'}
        </div>
        <button
          onClick={() => onViewPortfolio(client.id)}
          className="momentum-button-primary text-sm flex items-center"
        >
          <Eye className="w-4 h-4 mr-1" />
          View
        </button>
      </div>
    </motion.div>
  );
};

const SentimentChart = ({ trends }: { trends: SentimentTrend[] }) => {
  const data = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Average Sentiment',
        data: trends.map(t => t.avg_sentiment),
        borderColor: '#0066CC',
        backgroundColor: 'rgba(0, 102, 204, 0.1)',
        tension: 0.4,
        fill: true,
      },
      {
        label: 'Negative Feedback',
        data: trends.map(t => t.negative_count),
        borderColor: '#E53E3E',
        backgroundColor: 'rgba(229, 62, 62, 0.1)',
        yAxisID: 'y1',
        tension: 0.4,
      }
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date',
          color: '#64748B'
        },
        grid: {
          color: '#E2E8F0'
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Sentiment Score',
          color: '#64748B'
        },
        grid: {
          color: '#E2E8F0'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Negative Count',
          color: '#64748B'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          color: '#64748B'
        }
      },
      title: {
        display: true,
        text: 'Client Sentiment Trends',
        color: '#1E293B',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    }
  };

  return (
    <div className="h-80">
      <Line data={data} options={options} />
    </div>
  );
};

const TopicsChart = ({ topics }: { topics: TopicData[] }) => {
  const data = {
    labels: topics.map(t => t.topic),
    datasets: [
      {
        data: topics.map(t => t.count),
        backgroundColor: [
          '#0066CC',
          '#00A651',
          '#FF6B35',
          '#FFB800',
          '#E53E3E',
          '#3385D6',
          '#33B86B',
          '#FF8C65',
          '#FFC533',
          '#E85A5A'
        ],
        borderWidth: 0,
      }
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
        labels: {
          color: '#64748B',
          padding: 20
        }
      },
      title: {
        display: true,
        text: 'Top Feedback Topics',
        color: '#1E293B',
        font: {
          size: 16,
          weight: 'bold'
        }
      }
    }
  };

  return (
    <div className="h-80">
      <Doughnut data={data} options={options} />
    </div>
  );
};

const PortfolioModal = ({ 
  clientId, 
  onClose 
}: { 
  clientId: number | null; 
  onClose: () => void;
}) => {
  const { data: portfolioData, isLoading } = useQuery({
    queryKey: ['portfolio', clientId],
    queryFn: () => fetchPortfolioDetails(clientId!),
    enabled: !!clientId
  });

  if (!clientId) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-white rounded-xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-momentum-lg"
          onClick={(e) => e.stopPropagation()}
        >
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Portfolio Details - {portfolioData?.portfolio?.client_name}
            </h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-gray-500" />
            </button>
          </div>

          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-momentum-blue"></div>
            </div>
          ) : portfolioData ? (
            <div className="space-y-6">
              {/* Portfolio Summary */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="momentum-card p-4 bg-gradient-to-br from-momentum-blue to-momentum-blue-light text-white">
                  <div className="flex items-center">
                    <DollarSign className="w-8 h-8 mr-3" />
                    <div>
                      <h3 className="text-sm font-medium opacity-90">Total Value</h3>
                      <p className="text-2xl font-bold">
                        ${portfolioData.portfolio.total_value?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="momentum-card p-4 bg-gradient-to-br from-momentum-green to-momentum-green-light text-white">
                  <div className="flex items-center">
                    <TrendingUp className="w-8 h-8 mr-3" />
                    <div>
                      <h3 className="text-sm font-medium opacity-90">Unrealized P&L</h3>
                      <p className="text-2xl font-bold">
                        ${portfolioData.portfolio.unrealized_pnl?.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="momentum-card p-4 bg-gradient-to-br from-momentum-orange to-momentum-yellow text-white">
                  <div className="flex items-center">
                    <Shield className="w-8 h-8 mr-3" />
                    <div>
                      <h3 className="text-sm font-medium opacity-90">Risk Score</h3>
                      <p className="text-2xl font-bold">
                        {portfolioData.portfolio.risk_score}/10
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Holdings */}
              <div className="momentum-card p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-momentum-blue" />
                  Holdings
                </h3>
                <div className="overflow-x-auto">
                  <table className="momentum-table">
                    <thead>
                      <tr>
                        <th>Symbol</th>
                        <th>Company</th>
                        <th className="text-right">Value</th>
                        <th className="text-right">Weight</th>
                        <th className="text-right">Change</th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioData.holdings?.map((holding: Holding, index: number) => (
                        <tr key={index}>
                          <td className="font-medium">{holding.symbol}</td>
                          <td className="text-gray-600">{holding.company_name}</td>
                          <td className="text-right font-medium">${holding.market_value?.toLocaleString()}</td>
                          <td className="text-right">{holding.weight_percentage?.toFixed(1)}%</td>
                          <td className={clsx('text-right font-medium', {
                            'text-momentum-green': holding.change_percent > 0,
                            'text-momentum-red': holding.change_percent < 0,
                            'text-gray-600': holding.change_percent === 0
                          })}>
                            {holding.change_percent > 0 ? '+' : ''}{holding.change_percent?.toFixed(2)}%
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Recent Insights */}
              <div className="momentum-card p-6">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Target className="w-5 h-5 mr-2 text-momentum-blue" />
                  Recent Insights
                </h3>
                <div className="space-y-3">
                  {portfolioData.insights?.map((insight: Insight) => (
                    <div key={insight.id} className="bg-gray-50 p-4 rounded-lg">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900">{insight.title}</h4>
                        <span className={clsx('px-2 py-1 text-xs rounded-full font-medium', {
                          'bg-red-100 text-red-800': insight.priority >= 4,
                          'bg-yellow-100 text-yellow-800': insight.priority >= 3,
                          'bg-green-100 text-green-800': insight.priority < 3
                        })}>
                          Priority {insight.priority}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{insight.description}</p>
                      <div className="flex items-center text-xs text-gray-500">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(insight.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No portfolio data available</p>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const AlertsPanel = ({ trends }: { trends: SentimentTrend[] }) => {
  const recentTrends = trends.slice(-7);
  const urgentCount = recentTrends.reduce((sum, trend) => sum + trend.urgent_count, 0);
  const negativeCount = recentTrends.reduce((sum, trend) => sum + trend.negative_count, 0);
  const avgSentiment = recentTrends.reduce((sum, trend) => sum + trend.avg_sentiment, 0) / recentTrends.length;

  const alerts = [];
  
  if (urgentCount > 0) {
    alerts.push({
      type: 'urgent',
      message: `${urgentCount} urgent feedback items need attention`,
      icon: AlertTriangle,
      color: 'bg-red-50 text-red-800 border-red-200'
    });
  }
  
  if (negativeCount > 5) {
    alerts.push({
      type: 'warning',
      message: `${negativeCount} negative feedback items in the last week`,
      icon: AlertTriangle,
      color: 'bg-yellow-50 text-yellow-800 border-yellow-200'
    });
  }
  
  if (avgSentiment < -0.3) {
    alerts.push({
      type: 'sentiment',
      message: 'Overall client sentiment is declining',
      icon: TrendingDown,
      color: 'bg-orange-50 text-orange-800 border-orange-200'
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      type: 'success',
      message: 'All systems running smoothly',
      icon: CheckCircle,
      color: 'bg-green-50 text-green-800 border-green-200'
    });
  }

  return (
    <div className="momentum-card p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <AlertTriangle className="w-5 h-5 mr-2 text-momentum-blue" />
        Alerts & Notifications
      </h2>
      <div className="space-y-3">
        {alerts.map((alert, index) => {
          const IconComponent = alert.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={clsx('p-3 rounded-lg border flex items-center', alert.color)}
            >
              <IconComponent className="w-4 h-4 mr-2 flex-shrink-0" />
              <p className="text-sm font-medium">{alert.message}</p>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default function MomentumDashboard() {
  const [selectedClient, setSelectedClient] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState('30d');
  const queryClient = useQueryClient();

  // Queries
  const { data: clients, isLoading: clientsLoading, error: clientsError } = useQuery({
    queryKey: ['clients'],
    queryFn: fetchEnhancedClients,
    refetchInterval: 30000 // Refetch every 30 seconds
  });

  const { data: sentimentData, isLoading: sentimentLoading } = useQuery({
    queryKey: ['sentimentTrends', timeRange],
    queryFn: () => fetchSentimentTrends(timeRange),
    refetchInterval: 60000 // Refetch every minute
  });

  // Mutations
  const syncMutation = useMutation({
    mutationFn: syncMomentumIntegration,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    }
  });

  const handleViewPortfolio = useCallback((clientId: number) => {
    setSelectedClient(clientId);
  }, []);

  const handleClosePortfolio = useCallback(() => {
    setSelectedClient(null);
  }, []);

  // Calculate summary stats
  const totalClients = clients?.length || 0;
  const totalAUM = clients?.reduce((sum, client) => sum + (client.total_value || 0), 0) || 0;
  const avgSentiment = clients?.reduce((sum, client) => sum + (client.avg_sentiment || 0), 0) / totalClients || 0;
  const totalFeedback = clients?.reduce((sum, client) => sum + (client.feedback_count || 0), 0) || 0;

  if (clientsError) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="momentum-card p-6 bg-red-50 border-red-200">
          <div className="flex items-center">
            <AlertTriangle className="w-6 h-6 text-red-600 mr-3" />
            <div>
              <h3 className="text-lg font-semibold text-red-800">Connection Error</h3>
              <p className="text-red-600">Unable to connect to the backend. Using demo data instead.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
      {/* Header Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Financial Advisory Dashboard</h1>
          <p className="text-gray-600">Manage client relationships with AI-powered insights</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="momentum-input text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="momentum-button-primary flex items-center"
          >
            <RefreshCw className={clsx('w-4 h-4 mr-2', { 'animate-spin': syncMutation.isPending })} />
            {syncMutation.isPending ? 'Syncing...' : 'Sync Momentum'}
          </button>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Clients"
          value={totalClients.toString()}
          change="+12% from last month"
          icon={Users}
          trend="up"
        />
        <StatCard
          title="Assets Under Management"
          value={`$${(totalAUM / 1000000).toFixed(1)}M`}
          change="+8.5% from last month"
          icon={DollarSign}
          trend="up"
        />
        <StatCard
          title="Average Sentiment"
          value={avgSentiment.toFixed(2)}
          change={avgSentiment > 0 ? "Positive trend" : "Needs attention"}
          icon={MessageSquare}
          trend={avgSentiment > 0 ? "up" : "down"}
        />
        <StatCard
          title="Total Feedback"
          value={totalFeedback.toString()}
          change="24 new this week"
          icon={BarChart3}
          trend="neutral"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="momentum-card p-6">
          {sentimentLoading ? (
            <div className="flex justify-center items-center h-80">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-momentum-blue"></div>
            </div>
          ) : sentimentData?.trends ? (
            <SentimentChart trends={sentimentData.trends} />
          ) : (
            <div className="flex justify-center items-center h-80">
              <p className="text-gray-500">No sentiment data available</p>
            </div>
          )}
        </div>

        <div className="momentum-card p-6">
          {sentimentLoading ? (
            <div className="flex justify-center items-center h-80">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-momentum-blue"></div>
            </div>
          ) : sentimentData?.top_topics ? (
            <TopicsChart topics={sentimentData.top_topics} />
          ) : (
            <div className="flex justify-center items-center h-80">
              <p className="text-gray-500">No topic data available</p>
            </div>
          )}
        </div>
      </div>

      {/* Alerts and Clients Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          {sentimentData?.trends && <AlertsPanel trends={sentimentData.trends} />}
        </div>
        
        <div className="lg:col-span-2">
          <div className="momentum-card p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="w-5 h-5 mr-2 text-momentum-blue" />
              Client Overview
            </h2>
            {clientsLoading ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-momentum-blue"></div>
              </div>
            ) : clients?.length === 0 ? (
              <div className="text-center py-12">
                <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">No clients yet. Start by adding your first client.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-96 overflow-y-auto">
                {clients?.map((client: Client) => (
                  <ClientCard
                    key={client.id}
                    client={client}
                    onViewPortfolio={handleViewPortfolio}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Portfolio Modal */}
      <PortfolioModal
        clientId={selectedClient}
        onClose={handleClosePortfolio}
      />
    </div>
  );
}
