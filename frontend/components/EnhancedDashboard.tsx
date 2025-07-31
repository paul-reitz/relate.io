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
  const res = await fetch(`${API_BASE_URL}/api/v1/clients`, {
    headers: { 'Authorization': 'Bearer mock-token' }
  });
  if (!res.ok) throw new Error('Failed to fetch clients');
  return res.json();
};

const fetchSentimentTrends = async (timeRange: string = '30d') => {
  const res = await fetch(`${API_BASE_URL}/api/v1/analytics/sentiment-trends?time_range=${timeRange}`, {
    headers: { 'Authorization': 'Bearer mock-token' }
  });
  if (!res.ok) throw new Error('Failed to fetch sentiment trends');
  return res.json();
};

const fetchPortfolioDetails = async (clientId: number) => {
  const res = await fetch(`${API_BASE_URL}/api/v1/portfolios/${clientId}`, {
    headers: { 'Authorization': 'Bearer mock-token' }
  });
  if (!res.ok) throw new Error('Failed to fetch portfolio details');
  return res.json();
};

const syncMomentumIntegration = async () => {
  const res = await fetch(`${API_BASE_URL}/api/v1/integrations/momentum/sync`, {
    method: 'POST',
    headers: { 'Authorization': 'Bearer mock-token' }
  });
  if (!res.ok) throw new Error('Failed to sync with Momentum');
  return res.json();
};

// Components
const ClientCard = ({ client, onViewPortfolio }: { client: Client; onViewPortfolio: (id: number) => void }) => {
  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.2) return 'text-green-600 bg-green-100';
    if (sentiment < -0.2) return 'text-red-600 bg-red-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  const getRiskColor = (risk: number) => {
    if (risk <= 3) return 'text-green-600';
    if (risk <= 7) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{client.name}</h3>
          <p className="text-sm text-gray-600">{client.email}</p>
        </div>
        <div className="text-right">
          <p className="text-lg font-bold text-green-600">
            ${client.total_value?.toLocaleString() || 'N/A'}
          </p>
          <p className="text-sm text-gray-500">Portfolio Value</p>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-500">Risk Score</p>
          <p className={`font-semibold ${getRiskColor(client.risk_score || 5)}`}>
            {client.risk_score?.toFixed(1) || 'N/A'}/10
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Feedback</p>
          <p className="font-semibold text-gray-900">{client.feedback_count || 0}</p>
        </div>
      </div>
      
      <div className="flex justify-between items-center">
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(client.avg_sentiment || 0)}`}>
          Sentiment: {client.avg_sentiment > 0 ? 'Positive' : client.avg_sentiment < 0 ? 'Negative' : 'Neutral'}
        </div>
        <button
          onClick={() => onViewPortfolio(client.id)}
          className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
        >
          View Portfolio
        </button>
      </div>
    </div>
  );
};

const SentimentChart = ({ trends }: { trends: SentimentTrend[] }) => {
  const data = {
    labels: trends.map(t => new Date(t.date).toLocaleDateString()),
    datasets: [
      {
        label: 'Average Sentiment',
        data: trends.map(t => t.avg_sentiment),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Negative Feedback Count',
        data: trends.map(t => t.negative_count),
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        yAxisID: 'y1',
      }
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      x: {
        display: true,
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Sentiment Score'
        }
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        title: {
          display: true,
          text: 'Negative Count'
        },
        grid: {
          drawOnChartArea: false,
        },
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Client Sentiment Trends'
      }
    }
  };

  return <Line data={data} options={options} />;
};

const TopicsChart = ({ topics }: { topics: TopicData[] }) => {
  const data = {
    labels: topics.map(t => t.topic),
    datasets: [
      {
        data: topics.map(t => t.count),
        backgroundColor: [
          '#FF6384',
          '#36A2EB',
          '#FFCE56',
          '#4BC0C0',
          '#9966FF',
          '#FF9F40',
          '#FF6384',
          '#C9CBCF',
          '#4BC0C0',
          '#FF6384'
        ],
      }
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: 'Top Feedback Topics'
      }
    }
  };

  return <Doughnut data={data} options={options} />;
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Portfolio Details - {portfolioData?.portfolio?.client_name}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : portfolioData ? (
          <div className="space-y-6">
            {/* Portfolio Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800">Total Value</h3>
                <p className="text-2xl font-bold text-blue-900">
                  ${portfolioData.portfolio.total_value?.toLocaleString()}
                </p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-green-800">Unrealized P&L</h3>
                <p className="text-2xl font-bold text-green-900">
                  ${portfolioData.portfolio.unrealized_pnl?.toLocaleString()}
                </p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-yellow-800">Risk Score</h3>
                <p className="text-2xl font-bold text-yellow-900">
                  {portfolioData.portfolio.risk_score}/10
                </p>
              </div>
            </div>

            {/* Holdings */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Holdings</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">Symbol</th>
                      <th className="px-4 py-2 text-left text-sm font-medium text-gray-900">Company</th>
                      <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">Value</th>
                      <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">Weight</th>
                      <th className="px-4 py-2 text-right text-sm font-medium text-gray-900">Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolioData.holdings?.map((holding: Holding, index: number) => (
                      <tr key={index} className="border-t border-gray-200">
                        <td className="px-4 py-2 font-medium">{holding.symbol}</td>
                        <td className="px-4 py-2 text-sm text-gray-600">{holding.company_name}</td>
                        <td className="px-4 py-2 text-right">${holding.market_value?.toLocaleString()}</td>
                        <td className="px-4 py-2 text-right">{holding.weight_percentage?.toFixed(1)}%</td>
                        <td className={`px-4 py-2 text-right ${
                          holding.change_percent > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {holding.change_percent > 0 ? '+' : ''}{holding.change_percent?.toFixed(2)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent Insights */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Recent Insights</h3>
              <div className="space-y-3">
                {portfolioData.insights?.map((insight: Insight) => (
                  <div key={insight.id} className="bg-gray-50 p-4 rounded-lg">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{insight.title}</h4>
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        insight.priority >= 4 ? 'bg-red-100 text-red-800' :
                        insight.priority >= 3 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        Priority {insight.priority}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{insight.description}</p>
                    <p className="text-xs text-gray-500 mt-2">
                      {new Date(insight.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-center text-gray-500">No portfolio data available</p>
        )}
      </div>
    </div>
  );
};

const AlertsPanel = ({ trends }: { trends: SentimentTrend[] }) => {
  const recentTrends = trends.slice(-7); // Last 7 days
  const urgentCount = recentTrends.reduce((sum, trend) => sum + trend.urgent_count, 0);
  const negativeCount = recentTrends.reduce((sum, trend) => sum + trend.negative_count, 0);
  const avgSentiment = recentTrends.reduce((sum, trend) => sum + trend.avg_sentiment, 0) / recentTrends.length;

  const alerts = [];
  
  if (urgentCount > 0) {
    alerts.push({
      type: 'urgent',
      message: `${urgentCount} urgent feedback items need attention`,
      color: 'bg-red-100 text-red-800 border-red-200'
    });
  }
  
  if (negativeCount > 5) {
    alerts.push({
      type: 'warning',
      message: `${negativeCount} negative feedback items in the last week`,
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200'
    });
  }
  
  if (avgSentiment < -0.3) {
    alerts.push({
      type: 'sentiment',
      message: 'Overall client sentiment is declining',
      color: 'bg-orange-100 text-orange-800 border-orange-200'
    });
  }

  if (alerts.length === 0) {
    alerts.push({
      type: 'success',
      message: 'All systems running smoothly',
      color: 'bg-green-100 text-green-800 border-green-200'
    });
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Alerts & Notifications</h2>
      <div className="space-y-3">
        {alerts.map((alert, index) => (
          <div key={index} className={`p-3 rounded-lg border ${alert.color}`}>
            <p className="text-sm font-medium">{alert.message}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default function EnhancedDashboard() {
  const [selectedClient, setSelectedClient] = useState<number | null>(null);
  const [timeRange, setTimeRange] = useState('30d');
  const queryClient = useQueryClient();

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/1`); // Mock advisor ID
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Handle different types of real-time updates
      switch (data.type) {
        case 'new_feedback':
          queryClient.invalidateQueries({ queryKey: ['sentimentTrends'] });
          queryClient.invalidateQueries({ queryKey: ['clients'] });
          break;
        case 'portfolio_synced':
          queryClient.invalidateQueries({ queryKey: ['clients'] });
          queryClient.invalidateQueries({ queryKey: ['portfolio', data.client_id] });
          break;
        case 'client_created':
          queryClient.invalidateQueries({ queryKey: ['clients'] });
          break;
      }
    };

    return () => ws.close();
  }, [queryClient]);

  // Queries
  const { data: clients, isLoading: clientsLoading, error: clientsError } = useQuery({
    queryKey: ['clients'],
    queryFn: fetchEnhancedClients
  });

  const { data: sentimentData, isLoading: sentimentLoading } = useQuery({
    queryKey: ['sentimentTrends', timeRange],
    queryFn: () => fetchSentimentTrends(timeRange)
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

  if (clientsError) {
    return (
      <div className="p-6 bg-red-100 border border-red-200 rounded-lg">
        <p className="text-red-800">Error loading dashboard data. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Enhanced Dashboard</h1>
            <p className="text-gray-600">Financial Advisor Relationship Management</p>
          </div>
          <div className="flex space-x-4">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="90d">Last 90 days</option>
            </select>
            <button
              onClick={() => syncMutation.mutate()}
              disabled={syncMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {syncMutation.isPending ? 'Syncing...' : 'Sync Momentum'}
            </button>
          </div>
        </div>

        {/* Analytics Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            {sentimentLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : sentimentData?.trends ? (
              <SentimentChart trends={sentimentData.trends} />
            ) : (
              <p className="text-center text-gray-500">No sentiment data available</p>
            )}
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
            {sentimentLoading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : sentimentData?.top_topics ? (
              <TopicsChart topics={sentimentData.top_topics} />
            ) : (
              <p className="text-center text-gray-500">No topic data available</p>
            )}
          </div>
        </div>

        {/* Alerts and Clients Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-1">
            {sentimentData?.trends && <AlertsPanel trends={sentimentData.trends} />}
          </div>
          
          <div className="lg:col-span-2">
            <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Client Overview</h2>
              {clientsLoading ? (
                <div className="flex justify-center items-center h-32">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : clients?.length === 0 ? (
                <p className="text-center text-gray-500">No clients yet.</p>
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
    </div>
  );
}
