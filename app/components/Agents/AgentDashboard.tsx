"use client";

import { useState, useEffect } from 'react';
import { Bot, Activity, CheckCircle, XCircle, Loader2, Zap, Database, Cloud } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'error' | 'offline';
  type: string;
  tasksCompleted: number;
  uptime: string;
  lastActivity: string;
}

export function AgentDashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    let retryCount = 0;
    const maxRetries = 5;
    const baseDelay = 5000; // 5 seconds
    let timeoutId: ReturnType<typeof setTimeout> | null = null;

    const fetchWithBackoff = async () => {
      if (!isMounted) return;

      const success = await fetchAgents();

      if (!isMounted) return;

      if (!success) {
        if (retryCount >= maxRetries) {
          // Stop retrying after reaching the maximum number of consecutive failures.
          return;
        }
        retryCount += 1;
      } else {
        // Reset retry count on success to resume normal polling cadence.
        retryCount = 0;
      }

      const delay = baseDelay * Math.pow(2, Math.min(retryCount, 3));
      timeoutId = setTimeout(fetchWithBackoff, delay);
    };

    // Initial fetch with subsequent retries handled by fetchWithBackoff.
    fetchWithBackoff();

    return () => {
      isMounted = false;
      if (timeoutId !== null) {
        clearTimeout(timeoutId);
      }
    };
  }, []);

  const fetchAgents = async (): Promise<boolean> => {
    try {
      const response = await fetch('/api/agents/status-new');
      const data = await response.json();
      setAgents(data.agents || getMockAgents());
      setLoading(false);
      return true;
    } catch (error) {
      console.error('Failed to fetch agents:', error);
      setAgents(getMockAgents());
      setLoading(false);
      return false;
    }
  };

  const getMockAgents = (): Agent[] => [
    {
      id: '1',
      name: 'AgentX5 Master',
      status: 'active',
      type: 'Orchestrator',
      tasksCompleted: 1247,
      uptime: '99.9%',
      lastActivity: '2s ago',
    },
    {
      id: '2',
      name: 'Claude API Agent',
      status: 'active',
      type: 'AI Assistant',
      tasksCompleted: 892,
      uptime: '99.7%',
      lastActivity: '5s ago',
    },
    {
      id: '3',
      name: 'E2B Sandbox Agent',
      status: 'active',
      type: 'Execution',
      tasksCompleted: 543,
      uptime: '98.5%',
      lastActivity: '10s ago',
    },
    {
      id: '4',
      name: 'Legal Document Agent',
      status: 'active',
      type: 'Document Processing',
      tasksCompleted: 324,
      uptime: '99.2%',
      lastActivity: '15s ago',
    },
    {
      id: '5',
      name: 'GitHub Integration Agent',
      status: 'active',
      type: 'Integration',
      tasksCompleted: 456,
      uptime: '99.1%',
      lastActivity: '1m ago',
    },
  ];

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'idle':
        return <Activity className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Loader2 className="w-5 h-5 text-slate-500 animate-spin" />;
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'idle':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'error':
        return 'bg-red-500/20 text-red-400 border-red-500/50';
      default:
        return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'Orchestrator':
        return <Zap className="w-5 h-5" />;
      case 'AI Assistant':
        return <Bot className="w-5 h-5" />;
      case 'Execution':
        return <Cloud className="w-5 h-5" />;
      case 'Analytics':
      case 'Document Processing':
        return <Database className="w-5 h-5" />;
      default:
        return <Activity className="w-5 h-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    );
  }

  const activeAgents = agents.filter(a => a.status === 'active').length;
  const totalTasks = agents.reduce((sum, a) => sum + a.tasksCompleted, 0);

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Total Agents</p>
              <p className="text-3xl font-bold text-white mt-1">{agents.length}</p>
            </div>
            <Bot className="w-10 h-10 text-blue-500" />
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Active Now</p>
              <p className="text-3xl font-bold text-green-500 mt-1">{activeAgents}</p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-500" />
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Tasks Completed</p>
              <p className="text-3xl font-bold text-purple-500 mt-1">{totalTasks}</p>
            </div>
            <Zap className="w-10 h-10 text-purple-500" />
          </div>
        </div>

        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-400 text-sm">Avg Uptime</p>
              <p className="text-3xl font-bold text-blue-500 mt-1">99.2%</p>
            </div>
            <Activity className="w-10 h-10 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Agent List */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Bot className="w-6 h-6 text-blue-500" />
            Agent Status Monitor
          </h2>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-900/50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Agent</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Tasks</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Uptime</th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase">Last Activity</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {agents.map((agent) => (
                <tr key={agent.id} className="hover:bg-slate-700/30 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        {getTypeIcon(agent.type)}
                      </div>
                      <div>
                        <p className="text-white font-medium">{agent.name}</p>
                        <p className="text-slate-400 text-sm">ID: {agent.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-300">{agent.type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border ${getStatusColor(agent.status)}`}>
                      {getStatusIcon(agent.status)}
                      <span className="text-sm font-medium capitalize">{agent.status}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-300">{agent.tasksCompleted.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-300">{agent.uptime}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-slate-400">{agent.lastActivity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
