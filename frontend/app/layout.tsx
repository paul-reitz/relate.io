import type { Metadata } from 'next';
import Providers from '@/components/Providers';  // Import the new component

export const metadata: Metadata = {
  title: 'Relate.io Dashboard',
  description: 'Advisor dashboard for Relate.io',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>  // Wrap children here
      </body>
    </html>
  );
}