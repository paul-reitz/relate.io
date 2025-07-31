import type { Metadata } from 'next';
import Providers from '@/components/Providers';  // Import the new component
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });

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
      <body className={inter.className}>
        <Providers>{children}</Providers>  // Wrap children here
      </body>
    </html>
  );
}