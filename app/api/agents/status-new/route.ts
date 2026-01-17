import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    // In a real implementation, this would fetch agent status from a database or monitoring service
    const agents = [
      {
        id: '1',
        name: 'AgentX5 Master',
        status: 'active',
        type: 'Orchestrator',
        tasksCompleted: Math.floor(1200 + Math.random() * 100),
        uptime: '99.9%',
        lastActivity: `${Math.floor(Math.random() * 10) + 1}s ago`,
      },
      {
        id: '2',
        name: 'Claude API Agent',
        status: 'active',
        type: 'AI Assistant',
        tasksCompleted: Math.floor(850 + Math.random() * 100),
        uptime: '99.7%',
        lastActivity: `${Math.floor(Math.random() * 20) + 1}s ago`,
      },
      {
        id: '3',
        name: 'E2B Sandbox Agent',
        status: 'active',
        type: 'Execution',
        tasksCompleted: Math.floor(500 + Math.random() * 100),
        uptime: '98.5%',
        lastActivity: `${Math.floor(Math.random() * 30) + 1}s ago`,
      },
      {
        id: '4',
        name: 'Legal Document Agent',
        status: 'active',
        type: 'Document Processing',
        tasksCompleted: Math.floor(300 + Math.random() * 50),
        uptime: '99.2%',
        lastActivity: `${Math.floor(Math.random() * 60) + 1}s ago`,
      },
      {
        id: '5',
        name: 'GitHub Integration Agent',
        status: 'active',
        type: 'Integration',
        tasksCompleted: Math.floor(400 + Math.random() * 100),
        uptime: '99.1%',
        lastActivity: `${Math.floor(Math.random() * 2) + 1}m ago`,
      },
    ];

    return NextResponse.json({
      agents,
      timestamp: new Date().toISOString(),
      totalAgents: agents.length,
      activeAgents: agents.filter(a => a.status === 'active').length,
    });
  } catch (error) {
    console.error('Agent status API error:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch agent status',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export const runtime = 'nodejs';
