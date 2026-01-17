# Agent X5 Quantum System - Implementation Specification

## Problem Statement

The user has a partially implemented multi-agent trading and legal forensics system that needs to be completed and deployed. The current state includes:

1. **Existing Python backend** in `/workspaces/Private-Claude` with 219 agents configured
2. **No Next.js frontend** - needs to be created for the "Quantum Dashboard"
3. **No `.gitpod.yml`** - Gitpod/Ona environment not configured for auto-start
4. **Vercel deployment target** at `rener-chatbox.vercel.app` that ran out of build quota
5. **Three Replit bots** to consolidate (code not directly accessible, but architecture described)

The goal is to create a unified system with:
- A Next.js frontend dashboard deployed to Vercel
- Python backend scripts running in Gitpod/Ona
- Vercel AI SDK integration for chat functionality
- Auto-starting agent swarm on environment launch

## Requirements

### R1: Next.js Frontend Setup
Create a Next.js application with:
- `package.json` with Vercel AI SDK dependencies
- `app/page.tsx` - Quantum Dashboard UI showing:
  - Agent swarm status (759 agents visualization)
  - Trading balance and signals (Titan X module)
  - Asset recovery status (CFO module)
- `app/layout.tsx` - Root layout with metadata
- `tailwind.config.js` and `postcss.config.js` for styling
- Build configuration that bypasses lint/test for deployment

### R2: Gitpod/Ona Environment Configuration
Create `.gitpod.yml` that:
- Uses `gitpod/workspace-full` image
- Installs Python dependencies (pandas, numpy, ccxt, etc.)
- Installs Node.js dependencies
- Auto-launches Python agent scripts on startup
- Exposes port 3000 for dashboard preview

### R3: Python Agent Scripts
Create/update scripts in `/scripts/`:
- `swarm_manager.py` - Manages 759 agents in 3 squads (Legal, Finance, Research)
- `titan_x_quantum.py` - Trading bot with "Test 3 Times" validation
- `cfo_quantum.py` - Asset recovery scanner for specified targets

### R4: Vercel AI SDK Chat Integration
Add chat functionality using Vercel AI SDK:
- `app/api/chat/route.ts` - API route for chat completions
- Chat UI component in the dashboard
- Connection to AI provider (configurable via environment variables)

### R5: Environment Configuration
- `.env.example` with required environment variables
- Update `.devcontainer/devcontainer.json` for VS Code compatibility

## Acceptance Criteria

The implementation is complete when ALL of the following are verified:

### AC1: Frontend Builds Successfully
```bash
npm run build
# Exit code: 0
# No errors in output
```

### AC2: Development Server Starts
```bash
npm run dev
# Server starts on port 3000
# Dashboard renders without errors
```

### AC3: Python Scripts Execute
```bash
python3 scripts/swarm_manager.py &
python3 scripts/titan_x_quantum.py &
python3 scripts/cfo_quantum.py &
# All three scripts start without import errors
# Output shows agent activation messages
```

### AC4: Gitpod Configuration Valid
The `.gitpod.yml` file exists and contains:
- Valid image specification
- Task definitions for init and command
- Port configuration for 3000

### AC5: All Required Files Exist
- `/package.json`
- `/app/page.tsx`
- `/app/layout.tsx`
- `/app/api/chat/route.ts`
- `/tailwind.config.js`
- `/postcss.config.js`
- `/.gitpod.yml`
- `/scripts/swarm_manager.py`
- `/scripts/titan_x_quantum.py`
- `/scripts/cfo_quantum.py`
- `/.env.example`

### AC6: No Syntax Errors
All TypeScript/JavaScript files pass syntax validation:
```bash
npx tsc --noEmit
# Exit code: 0
```

All Python files pass syntax validation:
```bash
python3 -m py_compile scripts/swarm_manager.py
python3 -m py_compile scripts/titan_x_quantum.py
python3 -m py_compile scripts/cfo_quantum.py
# Exit code: 0 for all
```

## Implementation Approach

### Phase 1: Next.js Project Setup
1. Create `package.json` with Next.js, React, Tailwind, Vercel AI SDK, Framer Motion, Lucide React
2. Create `next.config.js`
3. Create `tailwind.config.js` and `postcss.config.js`
4. Create `tsconfig.json`

### Phase 2: Frontend Components
1. Create `app/layout.tsx` with root layout
2. Create `app/page.tsx` with Quantum Dashboard
3. Create `app/globals.css` with Tailwind imports

### Phase 3: Chat API Integration
1. Create `app/api/chat/route.ts` with Vercel AI SDK
2. Add chat component to dashboard (optional enhancement)

### Phase 4: Python Scripts
1. Create/update `scripts/swarm_manager.py`
2. Create/update `scripts/titan_x_quantum.py`
3. Create/update `scripts/cfo_quantum.py`

### Phase 5: Environment Configuration
1. Create `.gitpod.yml` for Ona auto-start
2. Create `.env.example` with variable documentation
3. Update `.devcontainer/devcontainer.json` if needed

### Phase 6: Verification
1. Run `npm install`
2. Run `npm run build`
3. Run `npm run dev` and verify dashboard renders
4. Run Python scripts and verify no errors
5. Validate all acceptance criteria

## Out of Scope

The following are NOT part of this implementation:
- Actual Vercel deployment (user must deploy manually)
- Real trading API connections (scripts use simulation)
- Real database connections for CFO recovery
- Authentication/authorization
- Live API key configuration (only `.env.example` template)

## Notes

- The "759 agents" is a conceptual/simulated architecture, not 759 actual processes
- Trading logic is simulation only - no real money at risk
- CFO recovery targets are placeholders for demonstration
- The system is designed for PAPER/DEMO mode by default
