'use client';

import { AgentDashboard } from '@/app/components/Agents';

export default function AgentsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          Agent Control Center
        </h1>
        <p className="text-slate-400">
          Monitor and manage all active agents in the AgentX5 system
        </p>
      </header>
      
      <AgentDashboard />
    </div>
  );
}
