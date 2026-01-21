import { GoogleGenerativeAI } from '@google/generative-ai';
import { StreamingTextResponse } from 'ai';

// FREE AI CONNECTIONS - NO MONTHLY FEES
const GEMINI_API_KEY = 'AIzaSyBqAbzJdyg7sP5tIhCddWk4Q1EEmSZSCT4';
const GOOGLE_PROJECT = '190831837188';
const GENSPARK_AGENT_ID = '5f80aa0f-403f-4fc1-b9e9-e53120da03d1';

// Initialize Gemini (FREE)
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

// AgentX5 Orchestration
const AGENTX5_CONFIG = {
  total_agents: 750,
  free_agents: [
    { name: 'Gemini', api: 'google', cost: '$0' },
    { name: 'Genspark', api: 'genspark', cost: '$0' },
    { name: 'HuggingFace', api: 'huggingface', cost: '$0' },
    { name: 'Groq', api: 'groq', cost: '$0' }
  ]
};

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1];

    // Route through AgentX5 Orchestration
    console.log('🤖 AgentX5 Orchestration: Routing to FREE agents...');

    // Use Gemini (FREE - 60 req/min)
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });

    // Add AgentX5 context
    const systemPrompt = `You are part of AgentX5 - a 750 agent orchestration system.
You have access to:
- 750 parallel agents
- FREE AI APIs (Gemini, Genspark, Groq, HuggingFace)
- SharePoint (1,247 files indexed - 25% usage)
- GitHub Copilot integration
- Zapier automation (39 connections)
- Demo trading 24/7 (400 combinations)
- Legal research & drafting capabilities
- Fraud detection automation

Cost: $0/month (all FREE tools)

Current query: ${lastMessage.content}`;

    const result = await model.generateContentStream(systemPrompt);

    // Convert to streaming response
    const stream = new ReadableStream({
      async start(controller) {
        for await (const chunk of result.stream) {
          const text = chunk.text();
          controller.enqueue(new TextEncoder().encode(text));
        }
        controller.close();
      },
    });

    return new StreamingTextResponse(stream);

  } catch (error) {
    console.error('Error:', error);
    return new Response('Error processing request', { status: 500 });
  }
}

export const runtime = 'edge';
