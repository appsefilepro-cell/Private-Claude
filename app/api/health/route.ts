import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  return NextResponse.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'Private Claude - AgentX5',
    version: '5.0.0',
    components: {
      api: 'operational',
      agents: 'operational',
      chat: 'operational',
    },
  });
}
