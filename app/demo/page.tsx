'use client';

import { useState } from 'react';
import { ChatBox } from '../components/Chat/ChatBox';
import { AgentDashboard } from '../components/Agents/AgentDashboard';
import { MessageSquare, Bot, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'dashboard'>('chat');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link 
                href="/"
                className="text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Bot className="w-8 h-8 text-blue-500" />
                  AgentX5 Demo
                </h1>
                <p className="text-slate-400 text-sm">New Chat & Dashboard Components</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('chat')}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'chat'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700'
            }`}
          >
            <MessageSquare className="w-5 h-5" />
            Chat Interface
          </button>
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
              activeTab === 'dashboard'
                ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700'
            }`}
          >
            <Bot className="w-5 h-5" />
            Agent Dashboard
          </button>
        </div>

        {/* Content */}
        <div className="animate-fadeIn">
          {activeTab === 'chat' ? (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chat Box */}
              <div className="lg:col-span-2 h-[600px]">
                <ChatBox 
                  agentName="AgentX5"
                  apiEndpoint="/api/chat-new"
                  placeholder="Ask AgentX5 anything..."
                />
              </div>

              {/* Info Panel */}
              <div className="space-y-4">
                <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
                  <h3 className="text-white font-semibold text-lg mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-500" />
                    Chat Features
                  </h3>
                  <ul className="space-y-3 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Real-time messaging with AgentX5</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Message status indicators</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Auto-scroll to latest message</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Error handling & retry logic</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Modern gradient UI design</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>Keyboard shortcuts (Enter to send)</span>
                    </li>
                  </ul>
                </div>

                <div className="bg-gradient-to-br from-blue-900/30 to-purple-900/30 border border-blue-700/50 rounded-xl p-6">
                  <h3 className="text-white font-semibold mb-2">Try Commands:</h3>
                  <ul className="space-y-2 text-blue-200 text-sm">
                    <li>• "status" - System status</li>
                    <li>• "trade" - Trading info</li>
                    <li>• "agents" - Swarm status</li>
                    <li>• "cfo" - Asset recovery</li>
                    <li>• "help" - All commands</li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div>
              <AgentDashboard />
              
              {/* Info Panel */}
              <div className="mt-6 bg-slate-800 border border-slate-700 rounded-xl p-6">
                <h3 className="text-white font-semibold text-lg mb-4 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-blue-500" />
                  Dashboard Features
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <h4 className="text-slate-300 font-medium mb-2">Real-time Monitoring</h4>
                    <ul className="space-y-2 text-slate-400 text-sm">
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Live agent status updates</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Auto-refresh every 5 seconds</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Task completion tracking</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-slate-300 font-medium mb-2">Statistics</h4>
                    <ul className="space-y-2 text-slate-400 text-sm">
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Total agent count</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Active agents metric</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Uptime percentages</span>
                      </li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-slate-300 font-medium mb-2">Agent Details</h4>
                    <ul className="space-y-2 text-slate-400 text-sm">
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Agent type classification</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Last activity timestamps</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-500">✓</span>
                        <span>Status indicators</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-700 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-slate-400 text-sm">
            <p>AgentX5 v5.0.0 | New Components Demo</p>
            <p className="mt-2">
              All existing files preserved • Only additive changes • Ready for Render deployment
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
