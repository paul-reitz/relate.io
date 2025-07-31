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

  if (clientsError || feedbackError) return <div className="text-red-500">Error loading data</div>;

  return (
    <div className="grid grid-cols-2 gap-4">
      <div>
        <h2 className="text-xl">Clients</h2>
        <ul className="list-disc pl-5">
          {clients?.map((client: any) => (
            <li key={client.id}>{client.name} - Value: ${client.portfolio_value.toFixed(2)}</li>
          ))}
        </ul>
      </div>
      <div>
        <h2 className="text-xl">Sentiment Alerts</h2>
        <ul className="list-disc pl-5">
          {feedback?.map((fb: any) => (
            <li key={fb.id}>{fb.text} ({fb.sentiment})</li>
          ))}
        </ul>
      </div>
    </div>
  );
}