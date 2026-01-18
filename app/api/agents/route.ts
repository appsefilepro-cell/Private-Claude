import { NextRequest, NextResponse } from 'next/server';
import * as fs from 'fs';
import * as path from 'path';

// Agent versions and their status
const AGENT_VERSIONS = {
  agentx2: {
    version: '2.0',
    name: 'AgentX 2.0 - Legacy Orchestrator',
    status: 'active',
    capabilities: ['basic_automation', 'task_routing'],
    agents: 50,
  },
  agentx3: {
    version: '3.0',
    name: 'AgentX 3.0 - Trading & Legal',
    status: 'active',
    capabilities: ['trading', 'legal_docs', 'zapier_integration'],
    agents: 100,
  },
  agentx4: {
    version: '4.0',
    name: 'AgentX 4.0 - Multi-Pillar',
    status: 'active',
    capabilities: ['multi_pillar', 'workflow_orchestration', 'api_connectors'],
    agents: 150,
  },
  agentx5: {
    version: '5.0',
    name: 'AgentX 5.0 - Quantum Swarm',
    status: 'active',
    capabilities: ['swarm_intelligence', 'quantum_trading', 'forensic_recovery', '24_7_operations'],
    agents: 759,
    squads: {
      legal: 253,
      trading: 253,
      research: 253,
    },
  },
};

const INTEGRATIONS = {
  github_copilot: { status: 'connected', type: 'code_assistant' },
  gitlab_duo: { status: 'connected', type: 'ci_cd_assistant' },
  vscode: { status: 'configured', type: 'ide_integration' },
  claude_api: { status: 'ready', type: 'ai_backend' },
  openai_api: { status: 'ready', type: 'ai_backend' },
  gemini_api: { status: 'ready', type: 'ai_backend' },
  zapier: { status: 'ready', type: 'automation' },
  render: { status: 'configured', type: 'deployment' },
  docker: { status: 'configured', type: 'containerization' },
};

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const detail = searchParams.get('detail');
  const agent = searchParams.get('agent');

  // If specific agent requested
  if (agent && AGENT_VERSIONS[agent as keyof typeof AGENT_VERSIONS]) {
    return NextResponse.json({
      success: true,
      agent: AGENT_VERSIONS[agent as keyof typeof AGENT_VERSIONS],
      timestamp: new Date().toISOString(),
    });
  }

  // Calculate totals
  const totalAgents = Object.values(AGENT_VERSIONS).reduce((sum, a) => sum + a.agents, 0);
  const activeVersions = Object.values(AGENT_VERSIONS).filter((a) => a.status === 'active').length;

  // Basic response
  const response = {
    success: true,
    system: 'AgentX5 Unified Multi-Agent System',
    version: '5.0.0',
    total_agents: totalAgents,
    active_versions: activeVersions,
    status: 'operational',
    trading_mode: process.env.LIVE_TRADING === 'true' ? 'LIVE' : 'PAPER',
    timestamp: new Date().toISOString(),
  };

  // If detailed response requested
  if (detail === 'full') {
    return NextResponse.json({
      ...response,
      agent_versions: AGENT_VERSIONS,
      integrations: INTEGRATIONS,
      deployment: {
        render: {
          dashboard: 'agentx5-dashboard',
          api: 'agentx5-api',
          trading: 'agentx5-trading',
          orchestrator: 'agentx5-orchestrator',
        },
        docker: {
          services: 9,
          compose_file: 'docker-compose.yml',
        },
      },
      capabilities: {
        trading: ['crypto', 'forex', 'indices', 'options'],
        legal: ['document_generation', 'case_management', 'forensics'],
        automation: ['zapier', 'github_actions', 'webhooks'],
      },
    });
  }

  return NextResponse.json(response);
}

export async function POST(req: NextRequest) {
  try {
    const { action, agent } = await req.json();

    switch (action) {
      case 'activate_all':
        return NextResponse.json({
          success: true,
          message: 'All agent versions activated',
          agents_activated: Object.keys(AGENT_VERSIONS).length,
          total_agents: Object.values(AGENT_VERSIONS).reduce((sum, a) => sum + a.agents, 0),
          timestamp: new Date().toISOString(),
        });

      case 'activate':
        if (agent && AGENT_VERSIONS[agent as keyof typeof AGENT_VERSIONS]) {
          return NextResponse.json({
            success: true,
            message: `${AGENT_VERSIONS[agent as keyof typeof AGENT_VERSIONS].name} activated`,
            agent: AGENT_VERSIONS[agent as keyof typeof AGENT_VERSIONS],
            timestamp: new Date().toISOString(),
          });
        }
        return NextResponse.json({ error: 'Invalid agent specified' }, { status: 400 });

      case 'status':
        return NextResponse.json({
          success: true,
          agent_versions: AGENT_VERSIONS,
          integrations: INTEGRATIONS,
          timestamp: new Date().toISOString(),
        });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Agent API error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
