# E2B Sandbox Quick Reference

Fast lookup guide for common E2B sandbox operations.

## Command Cheat Sheet

### Create Sandboxes

```bash
# Python sandbox
python3 scripts/e2b_sandbox_manager.py create --template python

# Node.js sandbox
python3 scripts/e2b_sandbox_manager.py create --template nodejs

# General purpose
python3 scripts/e2b_sandbox_manager.py create --template general

# Minimal (fast)
python3 scripts/e2b_sandbox_manager.py create --template minimal
```

### Execute Code

```bash
# Python
python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id sbx_123 \
  --language python \
  --code "print('Hello')"

# JavaScript
python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id sbx_123 \
  --language javascript \
  --code "console.log('Hello')"

# Bash
python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id sbx_123 \
  --language bash \
  --code "echo 'Hello'"
```

### Sandbox Management

```bash
# Check all sandboxes
python3 scripts/e2b_sandbox_manager.py status

# Check specific sandbox
python3 scripts/e2b_sandbox_manager.py status --sandbox-id sbx_123

# Stop sandbox
python3 scripts/e2b_sandbox_manager.py stop --sandbox-id sbx_123

# Cleanup sandbox
python3 scripts/e2b_sandbox_manager.py cleanup --sandbox-id sbx_123
```

### Lifecycle Operations

```bash
# Create and run lifecycle
python3 scripts/e2b_lifecycle.py create-lifecycle \
  --sandbox-id test_sbx \
  --template python \
  --timeout 300 \
  --script "print('Running')"

# Create workflow
python3 scripts/e2b_lifecycle.py create-workflow \
  --name my-workflow \
  --trigger manual \
  --template python

# List workflows
python3 scripts/e2b_lifecycle.py list-workflows

# Get lifecycle status
python3 scripts/e2b_lifecycle.py status --sandbox-id test_sbx
```

## Environment Setup

```bash
# View configuration
cat config/.env

# Set API key
export E2B_API_KEY="e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773"

# Load from file
export $(cat config/.env | xargs)

# Check setup
python3 scripts/e2b_setup.py
```

## Python API Quick Start

```python
import asyncio
from scripts.e2b_sandbox_manager import E2BSandboxManager

async def main():
    manager = E2BSandboxManager()
    await manager.webhook_client.initialize()

    try:
        # Create sandbox
        result = await manager.create_sandbox("python")
        sandbox_id = result["sandbox_id"]

        # Execute code
        result = await manager.execute_code(
            sandbox_id,
            "print('Result:', 2 + 2)"
        )
        print(result.stdout)

        # Get status
        status = await manager.get_status(sandbox_id)
        print(status)

    finally:
        await manager.cleanup_all()

asyncio.run(main())
```

## Common Tasks

### Run Python Data Analysis

```python
code = """
import pandas as pd
import numpy as np

# Generate random data
data = np.random.rand(100, 3)
df = pd.DataFrame(data, columns=['A', 'B', 'C'])

# Calculate statistics
print(df.describe())
"""

# Execute in Python sandbox
python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id analysis_sbx \
  --code "$code"
```

### Execute Node.js Code

```bash
code='
const axios = require("axios");

(async () => {
  const response = await axios.get("https://api.github.com/users/github");
  console.log(response.data);
})();
'

python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id node_sbx \
  --language javascript \
  --code "$code"
```

### Run Shell Commands

```bash
python3 scripts/e2b_sandbox_manager.py exec \
  --sandbox-id shell_sbx \
  --language bash \
  --code "curl -s https://api.github.com/repos/e2b-dev/e2b | jq '.stars'"
```

### Upload & Process Files

```python
# Upload file to sandbox
manager.file_handler.upload_file(
    local_path="data.csv",
    sandbox_path="/app/data.csv"
)

# Execute code to process it
result = await manager.execute_code(
    sandbox_id,
    """
import pandas as pd
df = pd.read_csv('/app/data.csv')
df.to_csv('/app/processed.csv', index=False)
print('Done')
"""
)

# Download processed file
await manager.download_files(
    sandbox_id,
    [("/app/processed.csv", "output.csv")]
)
```

## Status Codes

### Sandbox Status
- `creating`: Initializing sandbox
- `running`: Ready for code execution
- `executing`: Code is running
- `stopping`: Shutting down
- `stopped`: Not running
- `error`: Error occurred
- `cleanup`: Cleaning up resources

### Execution Status
- `success`: Code executed successfully (exit code 0)
- `error`: Code execution failed or error occurred
- `timeout`: Execution exceeded timeout
- `killed`: Process was terminated

## Resource Limits by Template

| Template | CPU | Memory | Timeout |
|----------|-----|--------|---------|
| minimal | 1 | 512MB | 120s |
| python | 2 | 2GB | 300s |
| nodejs | 2 | 2GB | 300s |
| general | 4 | 4GB | 600s |

## Webhook Events

Events triggered automatically:

```
sandbox_created
sandbox_stopped
sandbox_destroyed
execution_complete
execution_failed
workflow_triggered
zapier_integration_triggered
```

Access webhook history:
```python
events = lifecycle.event_bus.get_history()
for event in events:
    print(f"{event.timestamp}: {event.event_type.value}")
```

## Monitoring

```python
# Monitor execution
monitor = manager.monitor
monitor.start()

result = await manager.execute_code(sandbox_id, code)

metric = monitor.capture()
print(f"CPU: {metric['cpu_percent']}%")
print(f"Memory: {metric['memory_percent']}%")

# Get summary
summary = monitor.get_summary()
print(summary)
```

## Logging Levels

```bash
# Set logging level
export LOG_LEVEL=DEBUG  # Verbose logging
export LOG_LEVEL=INFO   # Normal logging
export LOG_LEVEL=WARNING  # Only warnings
export LOG_LEVEL=ERROR  # Only errors
```

## Troubleshooting Quick Fixes

```bash
# Verify API key
curl -H "Authorization: Bearer $E2B_API_KEY" https://api.e2b.dev/health

# Check installed packages
python3 -c "import aiohttp; import psutil; print('OK')"

# View recent logs
ls -lt logs/ | head -5
tail logs/latest.log

# List all active sandboxes
python3 scripts/e2b_sandbox_manager.py status

# Force cleanup
python3 scripts/e2b_sandbox_manager.py cleanup --sandbox-id old_sbx

# Reinstall dependencies
pip install --upgrade aiohttp psutil
```

## File Paths Reference

| Component | Location |
|-----------|----------|
| Main manager | `scripts/e2b_sandbox_manager.py` |
| Lifecycle | `scripts/e2b_lifecycle.py` |
| Setup script | `scripts/e2b_setup.py` |
| Templates | `config/e2b_sandbox_templates.json` |
| Environment | `config/.env` |
| Documentation | `E2B_SANDBOX_SETUP.md` |
| Uploads | `/tmp/e2b_uploads/` |
| Downloads | `/tmp/e2b_downloads/` |
| Logs | `logs/` |

## Tips & Tricks

1. **Reuse Sandbox IDs**: Use meaningful names for easier tracking
   ```bash
   --sandbox-id "analysis_$(date +%s)"
   ```

2. **Batch Operations**: Create workflows for multiple executions
   ```python
   scripts = ["cmd1", "cmd2", "cmd3"]
   # Runs sequentially in one lifecycle
   ```

3. **Monitor Resource Usage**: Check metrics during long operations
   ```python
   metric = monitor.capture()  # Get current stats
   ```

4. **Compress Files**: Large files automatically compressed
   ```python
   # 100MB → 20MB (automatic)
   manager.file_handler.upload_file("large.zip", "/app/data.zip")
   ```

5. **Retry Failed Executions**: Configure retry logic
   ```python
   config.max_retries = 3
   config.retry_delay = 5
   ```

## Performance Benchmarks

- Create sandbox: ~2 seconds
- Execute simple code: ~500ms
- Download 1MB file: ~1 second
- Webhook delivery: ~100ms

---

**For detailed documentation**: See `E2B_SANDBOX_SETUP.md`
