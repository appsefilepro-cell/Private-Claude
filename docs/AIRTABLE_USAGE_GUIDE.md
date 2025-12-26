
# AIRTABLE USAGE GUIDE FOR AGENT 5.0

## Quick Start

1. Install Airtable Python library:
   ```bash
   pip install airtable-python-wrapper
   ```

2. Configure credentials:
   ```bash
   cp config/airtable/config_template.json config/airtable/config.json
   # Edit config.json with your API key and Base IDs
   ```

3. Test connection:
   ```bash
   python scripts/airtable_integration.py
   ```

## Common Operations

### Create a new client:
```python
from airtable import Airtable
import json

with open('config/airtable/config.json') as f:
    config = json.load(f)

clients = Airtable(config['base_id'], 'Clients', api_key=config['api_key'])
clients.insert({
    'Client Name': 'John Doe',
    'Email': 'john@example.com',
    'Phone': '555-1234',
    'Status': 'Active'
})
```

### Update a task status:
```python
tasks = Airtable(config['base_id'], 'Tasks', api_key=config['api_key'])
tasks.update('rec123456', {'Status': 'Completed'})
```

### Query records:
```python
# Get all active clients
active_clients = clients.get_all(formula="Status = 'Active'")
```

## Agent 5.0 Integration

- Legal Division: Logs all document downloads to Legal Documents table
- Trading Division: Tracks market data updates in Market Data table
- Integration Division: Manages workflow status in Workflows table
- All Divisions: Update task status in Tasks table

## Zapier Automations

All Zapier workflows automatically sync with Airtable:
- New clients from Gmail → Clients table
- Task completions → Tasks table updates
- Document downloads → Legal Documents table
- Weekly summaries → Email reports from Airtable views
