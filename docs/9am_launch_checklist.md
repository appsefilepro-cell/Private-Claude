# 9 AM Launch Checklist (Dual/Triple Short Stack)

## Pre-Launch (08:55)

- [ ] Activate venv: `& "C:/AgentX/VS CODE GITHUB/.venv/Scripts/Activate.ps1"`
- [ ] Copy config/.env.example to config/.env and set values
- [ ] Ensure TRADING_MODE/ENVIRONMENT = paper (for safety)
- [ ] Confirm logs directory exists (`logs/`)

## Launch (09:00)

- [ ] Run: `python scripts/launch_9am_dual_strategy.py`
- [ ] Verify log streaming in `logs/trading_9am_YYYYMMDD.log`

## Monitor

- [ ] Watch balance/win-rate lines in log
- [ ] Keep max positions <= configured cap
- [ ] Check dashboard (if running) at <http://localhost:8080>

## Emergency Stop

- Press Ctrl+C in the launcher terminal
- To stop background orchestrators: `Stop-Process -Name python -Id <pid>`
