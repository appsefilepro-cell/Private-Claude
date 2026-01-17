import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  try {
    const agents = [
      {
        id: '1',
        name: 'AgentX5 Master',
        status: 'active',
        type: 'Orchestrator',
        tasksCompleted: Math.floor(Math.random() * 2000) + 1000,
        uptime: '99.9%',
        lastActivity: `${Math.floor(Math.random() * 60)}s ago`,
      },
      {
        id: '2',
        name: 'Claude API Agent',
        status: 'active',
        type: 'AI Assistant',
        tasksCompleted: Math.floor(Math.random() * 1500) + 500,
        uptime: '99.7%',
        lastActivity: `${Math.floor(Math.random() * 60)}s ago`,
      },
      {
        id: '3',
        name: 'E2B Sandbox Agent',
        status: 'active',
        type: 'Execution',
        tasksCompleted: Math.floor(Math.random() * 1000) + 300,
        uptime: '98.5%',
        lastActivity: `${Math.floor(Math.random() * 120)}s ago`,
      },
      {
        id: '4',
        name: 'Legal Document Agent',
        status: 'active',
        type: 'Document Processing',
        tasksCompleted: Math.floor(Math.random() * 500) + 100,
        uptime: '97.2%',
        lastActivity: `${Math.floor(Math.random() * 180)}s ago`,
      },
      {
        id: '5',
        name: 'GitHub Integration Agent',
        status: 'active',
        type: 'Integration',
        tasksCompleted: Math.floor(Math.random() * 800) + 200,
        uptime: '99.1%',
        lastActivity: `${Math.floor(Math.random() * 90)}s ago`,
      },
    ];

    return NextResponse.json({
      agents,
      timestamp: new Date().toISOString(),
      totalAgents: agents.length,
      activeAgents: agents.filter(a => a.status === 'active').length,
    });
  } catch (error) {
    console.error('Agent status error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch agent status' },
      { status: 500 }
    );
  }
}
