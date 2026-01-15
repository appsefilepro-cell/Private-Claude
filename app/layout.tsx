import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Agent X5: Quantum Dashboard',
  description: '759-Agent Swarm Command Center - Titan X Trading & CFO Recovery',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-black">{children}</body>
    </html>
  );
}
