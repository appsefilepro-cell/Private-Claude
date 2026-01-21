'use client';

import { useChat } from 'ai/react';
import { useState, useEffect } from 'react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();
  const [agentStatus, setAgentStatus] = useState({
    total_agents: 750,
    active: 0,
    cost: '$0/month'
  });

  useEffect(() => {
    // Simulate AgentX5 activation
    const interval = setInterval(() => {
      setAgentStatus(prev => ({
        ...prev,
        active: Math.min(prev.active + 50, 750)
      }));
    }, 100);

    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ fontFamily: 'system-ui', maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '20px', borderRadius: '10px', marginBottom: '20px', color: 'white' }}>
        <h1 style={{ margin: 0 }}>🤖 FREE AI Chatbot + AgentX5</h1>
        <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>750 Agents • $0/month • No Fees</p>
      </div>

      {/* Agent Status */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '20px' }}>
        <div style={{ background: '#f0f9ff', padding: '15px', borderRadius: '8px', border: '2px solid #0ea5e9' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#0284c7' }}>
            {agentStatus.active}/{agentStatus.total_agents}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>Agents Active</div>
        </div>
        <div style={{ background: '#f0fdf4', padding: '15px', borderRadius: '8px', border: '2px solid #10b981' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#059669' }}>
            {agentStatus.cost}
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>Monthly Cost</div>
        </div>
        <div style={{ background: '#fef3f2', padding: '15px', borderRadius: '8px', border: '2px solid #f97316' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ea580c' }}>
            FREE
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>All Tools</div>
        </div>
      </div>

      {/* Connected Services */}
      <div style={{ background: '#fafafa', padding: '15px', borderRadius: '8px', marginBottom: '20px' }}>
        <div style={{ fontSize: '14px', fontWeight: 'bold', marginBottom: '10px' }}>🔌 Connected Services (FREE):</div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ Gemini API
          </span>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ Genspark Agent
          </span>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ AgentX5 (750)
          </span>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ SharePoint (25%)
          </span>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ Zapier (39)
          </span>
          <span style={{ background: 'white', padding: '5px 10px', borderRadius: '5px', fontSize: '12px', border: '1px solid #e5e7eb' }}>
            ✅ Trading 24/7
          </span>
        </div>
      </div>

      {/* Chat Messages */}
      <div style={{ background: 'white', border: '1px solid #e5e7eb', borderRadius: '8px', minHeight: '400px', maxHeight: '500px', overflow: 'auto', padding: '20px', marginBottom: '20px' }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: '#9ca3af', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '10px' }}>💬</div>
            <div>Start chatting with your FREE AI agents!</div>
            <div style={{ fontSize: '14px', marginTop: '10px' }}>
              Ask about legal research, fraud detection, trading, or anything else.
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: m.role === 'user' ? '#3b82f6' : '#10b981',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '16px',
                marginRight: '10px'
              }}>
                {m.role === 'user' ? '👤' : '🤖'}
              </div>
              <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                {m.role === 'user' ? 'You' : 'AgentX5'}
              </div>
            </div>
            <div style={{
              marginLeft: '42px',
              padding: '12px',
              background: m.role === 'user' ? '#eff6ff' : '#f0fdf4',
              borderRadius: '8px',
              border: m.role === 'user' ? '1px solid #dbeafe' : '1px solid #dcfce7'
            }}>
              {m.content}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ textAlign: 'center', color: '#9ca3af' }}>
            <div>🤖 AgentX5 thinking...</div>
          </div>
        )}
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit}>
        <div style={{ display: 'flex', gap: '10px' }}>
          <input
            value={input}
            onChange={handleInputChange}
            placeholder="Ask anything... (Legal research, fraud detection, trading, etc.)"
            disabled={isLoading}
            style={{
              flex: 1,
              padding: '15px',
              borderRadius: '8px',
              border: '2px solid #e5e7eb',
              fontSize: '16px',
              outline: 'none'
            }}
          />
          <button
            type="submit"
            disabled={isLoading}
            style={{
              padding: '15px 30px',
              background: isLoading ? '#9ca3af' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {isLoading ? '...' : 'Send'}
          </button>
        </div>
      </form>

      {/* Footer */}
      <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '12px', color: '#9ca3af' }}>
        <div>💎 100% FREE • No Monthly Fees • Unlimited Usage</div>
        <div style={{ marginTop: '5px' }}>
          Powered by: Gemini • Genspark • AgentX5 • Vercel
        </div>
      </div>
    </div>
  );
}
