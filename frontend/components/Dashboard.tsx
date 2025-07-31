'use client';

import { useQuery } from '@tanstack/react-query';

const fetchClients = async () => {
  const res = await fetch('/api/clients');
  if (!res.ok) throw new Error('Failed to fetch clients');
  return res.json();
};

const fetchFeedback = async () => {
  const res = await fetch('/api/feedback');
  if (!res.ok) throw new Error('Failed to fetch feedback');
  return res.json();
};

export default function Dashboard() {
  const { data: clients, isError: clientsError } = useQuery({ queryKey: ['clients'], queryFn: fetchClients });
  const { data: feedback, isError: feedbackError } = useQuery({ queryKey: ['feedback'], queryFn: fetchFeedback });

  if (clientsError || feedbackError) return <div className="text-red-500 p-4 bg-red-100 rounded-md">Error loading data</div>;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 bg-background min-h-screen">
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold text-text mb-4">Clients</h2>
        {clients?.length === 0 ? (
          <p className="text-gray-500">No clients yet.</p>
        ) : (
          <ul className="space-y-4">
            {clients?.map((client: any) => (
              <li key={client.id} className="p-4 bg-gray-50 rounded-md border border-gray-100 hover:bg-gray-100 transition">
                <span className="font-medium text-primary">{client.name}</span> - Value: <span className="text-secondary">${client.portfolio_value.toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="bg-white p-6 rounded-lg shadow-md border border-gray-200">
        <h2 className="text-xl font-semibold text-text mb-4">Sentiment Alerts</h2>
        {feedback?.length === 0 ? (
          <p className="text-gray-500">No feedback yet.</p>
        ) : (
          <ul className="space-y-4">
            {feedback?.map((fb: any) => (
              <li key={fb.id} className="p-4 bg-gray-50 rounded-md border border-gray-100 hover:bg-gray-100 transition">
                {fb.text} <span className={`font-bold ${fb.sentiment === 'POSITIVE' ? 'text-green-600' : fb.sentiment === 'NEGATIVE' ? 'text-red-600' : 'text-yellow-600'}`}>({fb.sentiment})</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}