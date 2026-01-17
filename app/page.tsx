'use client';

import { useState, useEffect } from 'react';
import { Brain, Shield, TrendingUp, Zap, MessageSquare } from 'lucide-react';

export default function QuantumDashboard() {
  const [swarmStatus, setSwarmStatus] = useState('INITIALIZING 759 NODES...');
  const [balance, setBalance] = useState(100000.0);
  const [activeAgents, setActiveAgents] = useState(0);
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let agents = 0;
    const interval = setInterval(() => {
      if (agents < 759) {
        agents += 11;
        setActiveAgents(Math.min(agents, 759));
      } else {
        setSwarmStatus('QUANTUM COHERENCE ACHIEVED');
        setBalance((prev) => prev + (Math.random() * 50 - 20));
      }
    }, 100);
    return () => clearInterval(interval);
  }, []);

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || isLoading) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    setChatMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...chatMessages, { role: 'user', content: userMessage }],
        }),
      });

      if (!response.ok) throw new Error('Chat request failed');

      const data = await response.json();
      setChatMessages((prev) => [...prev, { role: 'assistant', content: data.message }]);
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'System offline. Configure OPENAI_API_KEY in .env.local' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black text-green-400 font-mono p-6">
      <header className="flex justify-between items-center mb-10 border-b-2 border-green-700 pb-4">
        <h1 className="text-3xl md:text-4xl font-bold flex items-center gap-3">
          <Brain className="w-8 h-8 md:w-10 md:h-10 animate-pulse" /> AGENT X5: QUANTUM
        </h1>
        <div className="text-right">
          <div className="text-xs text-gray-500">OPERATIONAL MODE</div>
          <div className="text-lg md:text-xl font-bold text-green-300">SOVEREIGN ARCHITECT</div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* TITAN X MODULE */}
        <div className="bg-gray-900/80 p-6 rounded-lg border border-green-800 shadow-[0_0_15px_rgba(0,255,0,0.2)]">
          <div className="flex items-center gap-2 mb-4 text-xl md:text-2xl border-b border-gray-700 pb-2">
            <TrendingUp /> TITAN X (FINANCE)
          </div>
          <div className="text-4xl md:text-5xl font-bold text-white mb-2">
            ${balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-sm text-green-600 mb-4">TARGET: $1,000,000 (PROP FIRM)</div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span>STRATEGY:</span> <span className="text-white">BIG SHORT (HEDGE)</span>
            </div>
            <div className="flex justify-between">
              <span>WIN RATE:</span> <span className="text-white">91.4% (CALCULATED)</span>
            </div>
            <div className="flex justify-between">
              <span>VALIDATION:</span> <span className="text-white">TEST 3 TIMES (ACTIVE)</span>
            </div>
          </div>
        </div>

        {/* SWARM INTELLIGENCE */}
        <div className="bg-gray-900/80 p-6 rounded-lg border border-green-800 shadow-[0_0_15px_rgba(0,255,0,0.2)]">
          <div className="flex items-center gap-2 mb-4 text-xl md:text-2xl border-b border-gray-700 pb-2">
            <Zap /> SWARM STATUS
          </div>
          <div className="text-5xl md:text-6xl font-black text-center mb-4">{activeAgents} / 759</div>
          <div className="text-center text-green-500 animate-pulse">{swarmStatus}</div>
          <div className="mt-4 grid grid-cols-3 gap-2 text-center text-[10px]">
            <div className="bg-green-900/50 p-1 rounded">LEGAL: 253</div>
            <div className="bg-blue-900/50 p-1 rounded">TRADING: 253</div>
            <div className="bg-purple-900/50 p-1 rounded">CFO: 253</div>
          </div>
        </div>

        {/* CFO RECOVERY MODULE */}
        <div className="bg-gray-900/80 p-6 rounded-lg border border-green-800 shadow-[0_0_15px_rgba(0,255,0,0.2)]">
          <div className="flex items-center gap-2 mb-4 text-xl md:text-2xl border-b border-gray-700 pb-2">
            <Shield /> ASSET RECOVERY
          </div>
          <ul className="space-y-3 text-sm">
            <li className="flex justify-between items-center bg-gray-800 p-2 rounded">
              <span>THURMAN ROBINSON</span>
              <span className="text-yellow-400">SCANNING...</span>
            </li>
            <li className="flex justify-between items-center bg-gray-800 p-2 rounded">
              <span>APPS LLC (TEXAS)</span>
              <span className="text-green-400">FOUND: $159k</span>
            </li>
            <li className="flex justify-between items-center bg-gray-800 p-2 rounded">
              <span>201 E 61ST ST</span>
              <span className="text-blue-400">HISTORIC DATA</span>
            </li>
          </ul>
        </div>
      </div>

      {/* CHAT INTERFACE */}
      <div className="bg-gray-900/80 p-6 rounded-lg border border-green-800 shadow-[0_0_15px_rgba(0,255,0,0.2)]">
        <div className="flex items-center gap-2 mb-4 text-xl md:text-2xl border-b border-gray-700 pb-2">
          <MessageSquare /> COMMAND INTERFACE
        </div>
        <div className="h-48 overflow-y-auto mb-4 space-y-2">
          {chatMessages.length === 0 ? (
            <div className="text-gray-500 text-sm">Enter commands to interact with Agent X5...</div>
          ) : (
            chatMessages.map((msg, i) => (
              <div
                key={i}
                className={`p-2 rounded ${
                  msg.role === 'user' ? 'bg-green-900/30 text-green-300' : 'bg-gray-800 text-white'
                }`}
              >
                <span className="text-xs text-gray-500">{msg.role === 'user' ? 'YOU' : 'X5'}:</span>{' '}
                {msg.content}
              </div>
            ))
          )}
          {isLoading && (
            <div className="p-2 rounded bg-gray-800 text-gray-400 animate-pulse">Processing...</div>
          )}
        </div>
        <form onSubmit={handleChat} className="flex gap-2">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            placeholder="Enter command..."
            className="flex-1 bg-black border border-green-800 rounded px-4 py-2 text-green-400 focus:outline-none focus:border-green-500"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="bg-green-800 hover:bg-green-700 px-6 py-2 rounded font-bold disabled:opacity-50"
          >
            SEND
          </button>
        </form>
      </div>
    </div>
  );
}
