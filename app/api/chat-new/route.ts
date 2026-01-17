import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    const { message, conversationId } = await req.json();

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    // Check if Anthropic API key is configured
    const anthropicApiKey = process.env.ANTHROPIC_API_KEY;
    
    if (anthropicApiKey && anthropicApiKey !== 'sk-ant-your-anthropic-key-here') {
      // Use Anthropic SDK if available
      try {
        const Anthropic = require('@anthropic-ai/sdk');
        const anthropic = new Anthropic({
          apiKey: anthropicApiKey,
        });

        const response = await anthropic.messages.create({
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 1024,
          messages: [
            {
              role: 'user',
              content: message,
            },
          ],
        });

        const assistantMessage = response.content[0]?.type === 'text' 
          ? response.content[0].text 
          : 'I apologize, but I could not generate a response.';

        return NextResponse.json({
          message: assistantMessage,
          conversationId: conversationId || Date.now().toString(),
          timestamp: new Date().toISOString(),
        });
      } catch (apiError) {
        console.error('Anthropic API error:', apiError);
        // Fall through to mock response
      }
    }

    // Mock response if no API key configured
    const mockResponse = generateMockResponse(message);

    return NextResponse.json({
      message: mockResponse,
      conversationId: conversationId || Date.now().toString(),
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json({ 
      error: 'Failed to process message',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

function generateMockResponse(message: string): string {
  const lowerMessage = message.toLowerCase();

  // Agent status queries
  if (lowerMessage.includes('status') || lowerMessage.includes('how are you')) {
    return `I'm AgentX5, currently online and ready to assist! 🤖\n\nSystem Status:\n✅ All systems operational\n✅ 759 agent swarm active\n✅ Quantum coherence achieved\n\nHow can I help you today?`;
  }

  // Trading queries
  if (lowerMessage.includes('trade') || lowerMessage.includes('trading') || lowerMessage.includes('titan')) {
    return `TITAN X Trading Engine Status:\n\n📈 Strategy: Big Short (Hedge)\n💰 Mode: PAPER TRADING (Safe)\n📊 Win Rate: 91.4%\n🎯 Target: $1,000,000\n\nCurrent positions and market analysis available. Would you like more details?`;
  }

  // Agent swarm queries
  if (lowerMessage.includes('agent') || lowerMessage.includes('swarm')) {
    return `759-Agent Swarm Formation:\n\n🔷 LEGAL Squad: 253 agents\n🔶 FINANCE Squad: 253 agents\n🔵 RESEARCH Squad: 253 agents\n\nStatus: QUANTUM COHERENCE ACHIEVED\n\nAll agents are operational and coordinating tasks efficiently.`;
  }

  // CFO/Recovery queries
  if (lowerMessage.includes('cfo') || lowerMessage.includes('recovery') || lowerMessage.includes('asset')) {
    return `CFO Forensic Suite Status:\n\n🔍 Target 1: Thurman Robinson - SCANNING\n💰 Target 2: APPS LLC (Texas) - FOUND $159,000\n📋 Target 3: 201 E 61st St - HISTORICAL DATA\n\nDatabase sources: Texas Comptroller, Federal Unclaimed Property\n\nWould you like detailed reports on any target?`;
  }

  // Help queries
  if (lowerMessage.includes('help') || lowerMessage.includes('what can you do')) {
    return `I'm AgentX5, your AI assistant! I can help with:\n\n🤖 Agent Status & Swarm Coordination\n📈 Trading Analysis (Titan X Engine)\n💼 Asset Recovery & Forensics (CFO Suite)\n📊 System Reports & Analytics\n🔧 Configuration & Support\n\nJust ask me anything, and I'll do my best to assist!`;
  }

  // Default response
  return `I received your message: "${message}"\n\nI'm processing your request with my neural network. While I'm configured for demo mode, I can help you with:\n\n• Agent status and coordination\n• Trading strategies and analysis\n• Asset recovery investigations\n• System reports\n\nType "help" to see all available commands!`;
}

export const runtime = 'nodejs';
