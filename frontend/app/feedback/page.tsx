'use client';

import { useRouter } from 'next/navigation';
import { useSearchParams } from 'next/navigation';
import { useState } from 'react';

export default function Feedback() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const client_id = searchParams.get('client_id');
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!client_id || !text) {
      setError('Missing information');
      return;
    }
    try {
      const res = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: parseInt(client_id), text }),
      });
      if (!res.ok) throw new Error('Failed to submit');
      setSubmitted(true);
    } catch (err) {
      setError('Submission failed');
    }
  };

  if (submitted) {
    return <div className="p-4">Thank you for your feedback!</div>;
  }

  return (
    <main className="p-4">
      <h1 className="text-2xl">Provide Feedback</h1>
      <form onSubmit={handleSubmit} className="mt-4">
        <textarea
          className="w-full p-2 border"
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Your feedback..."
        />
        {error && <p className="text-red-500">{error}</p>}
        <button type="submit" className="mt-2 bg-blue-500 text-white p-2">Submit</button>
      </form>
    </main>
  );
}