#!/usr/bin/env python3
"""
AIRTABLE SETUP - Client/Case Management System
Visual database for Agent 5.0 workflow tracking
"""
import os
import json
from datetime import datetime

print("=" * 80)
print("AIRTABLE CLIENT/CASE MANAGEMENT SETUP")
print("=" * 80)
print(f"Purpose: Visual database for tracking clients, cases, tasks")
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Create config directory
os.makedirs("config/airtable", exist_ok=True)

# Airtable bases to create
airtable_bases = {
    "Client Management": {
        "purpose": "Track all clients and their information",
        "tables": [
            {
                "name": "Clients",
                "fields": [
                    "Client Name (Single line text)",
                    "Email (Email)",
                    "Phone (Phone number)",
                    "Status (Single select: Active, Inactive, Prospect)",
                    "Date Added (Date)",
                    "Agent Assigned (Link to Agents table)",
                    "Notes (Long text)"
                ]
            },
            {
                "name": "Cases",
                "fields": [
                    "Case Name (Single line text)",
                    "Client (Link to Clients table)",
                    "Case Type (Single select: Legal, Financial, Business)",
                    "Status (Single select: Open, In Progress, Closed)",
                    "Priority (Single select: High, Medium, Low)",
                    "Date Opened (Date)",
                    "Date Closed (Date)",
                    "Documents (Attachments)"
                ]
            },
            {
                "name": "Agents",
                "fields": [
                    "Agent Name (Single line text)",
                    "Division (Single select: Legal, Trading, Integration, etc.)",
                    "Status (Single select: Active, Idle, Busy)",
                    "Current Tasks (Link to Tasks table)",
                    "Completed Tasks (Number)"
                ]
            }
        ]
    },
    "Task Management": {
        "purpose": "Track all Agent 5.0 tasks and workflows",
        "tables": [
            {
                "name": "Tasks",
                "fields": [
                    "Task Name (Single line text)",
                    "Description (Long text)",
                    "Status (Single select: Pending, In Progress, Completed, Failed)",
                    "Assigned Agent (Link to Agents table)",
                    "Priority (Single select: High, Medium, Low)",
                    "Due Date (Date)",
                    "Completed Date (Date)",
                    "Related Case (Link to Cases table)"
                ]
            },
            {
                "name": "Workflows",
                "fields": [
                    "Workflow Name (Single line text)",
                    "Type (Single select: Zapier, GitHub Actions, Manual)",
                    "Status (Single select: Active, Paused, Failed)",
                    "Trigger (Single line text)",
                    "Last Run (Date)",
                    "Success Rate (Percent)",
                    "Tasks (Link to Tasks table)"
                ]
            }
        ]
    },
    "Document Tracker": {
        "purpose": "Track all downloaded and generated documents",
        "tables": [
            {
                "name": "Legal Documents",
                "fields": [
                    "Document Name (Single line text)",
                    "Type (Single select: IRS Form, SBA Form, State Form, Template)",
                    "Download Date (Date)",
                    "Source URL (URL)",
                    "File (Attachments)",
                    "Status (Single select: Downloaded, Pending, Failed)",
                    "Related Case (Link to Cases table)"
                ]
            },
            {
                "name": "Market Data",
                "fields": [
                    "Asset Pair (Single line text)",
                    "Type (Single select: Forex, Crypto, Commodity)",
                    "Data Range (Single line text)",
                    "Last Updated (Date)",
                    "File Size (Number)",
                    "Records (Number)",
                    "Status (Single select: Complete, Partial, Failed)"
                ]
            }
        ]
    }
}

print("\nAIRTABLE BASES TO CREATE:")
print("=" * 80)
for base_name, base_info in airtable_bases.items():
    print(f"\n{base_name}")
    print(f"  Purpose: {base_info['purpose']}")
    print(f"  Tables ({len(base_info['tables'])}):")
    for table in base_info['tables']:
        print(f"    • {table['name']} ({len(table['fields'])} fields)")

# Airtable API configuration
airtable_config = {
    "api_key": "YOUR_AIRTABLE_API_KEY",
    "base_id": "YOUR_BASE_ID",
    "api_url": "https://api.airtable.com/v0/",
    "bases": {}
}

# Save config template
with open("config/airtable/config_template.json", "w") as f:
    json.dump(airtable_config, f, indent=2)

print("\n" + "=" * 80)
print("AIRTABLE SETUP INSTRUCTIONS")
print("=" * 80)
print("\n1. Create Airtable account:")
print("   https://airtable.com/signup")
print("   FREE plan: 1,200 records per base, unlimited bases")
print("\n2. Create bases:")
for base_name in airtable_bases.keys():
    print(f"   - {base_name}")
print("\n3. Get API key:")
print("   - Go to: https://airtable.com/account")
print("   - Click: Generate API key")
print("   - Copy the key")
print("\n4. Get Base IDs:")
print("   - Go to: https://airtable.com/api")
print("   - Select each base")
print("   - Copy the Base ID from the URL (starts with 'app')")
print("\n5. Save credentials:")
print("   - Create: config/airtable/config.json")
print("   - Add your API key and Base IDs")

# Create Airtable integration script
integration_script = """#!/usr/bin/env python3
import os
import json
from airtable import Airtable

def connect_airtable():
    # Load config
    config_file = 'config/airtable/config.json'

    if not os.path.exists(config_file):
        print("ERROR: Airtable config not found!")
        print(f"Please create: {config_file}")
        print("Follow setup instructions to get API key and Base IDs")
        return None

    with open(config_file, 'r') as f:
        config = json.load(f)

    # Test connection
    try:
        # Connect to Clients table (example)
        clients = Airtable(
            config['base_id'],
            'Clients',
            api_key=config['api_key']
        )

        # Try to get all records
        records = clients.get_all()
        print(f"✅ Connected to Airtable!")
        print(f"   Found {len(records)} client records")

        return clients

    except Exception as e:
        print(f"⚠️ Connection failed: {str(e)}")
        return None

def create_client_record(name, email, phone, status="Active"):
    config_file = 'config/airtable/config.json'
    with open(config_file, 'r') as f:
        config = json.load(f)

    clients = Airtable(config['base_id'], 'Clients', api_key=config['api_key'])

    record = clients.insert({
        'Client Name': name,
        'Email': email,
        'Phone': phone,
        'Status': status,
        'Date Added': datetime.now().strftime('%Y-%m-%d')
    })

    print(f"✅ Client record created: {name}")
    return record

if __name__ == '__main__':
    print("=" * 80)
    print("AIRTABLE CONNECTION TEST")
    print("=" * 80)
    connect_airtable()
"""

with open("scripts/airtable_integration.py", "w") as f:
    f.write(integration_script)

os.chmod("scripts/airtable_integration.py", 0o755)
print("\n✅ Integration script created: scripts/airtable_integration.py")

# Zapier workflows for Airtable
zapier_workflows = [
    {
        "workflow_number": 25,
        "name": "New Client → Airtable Record",
        "trigger": "Gmail (new email with subject: New Client)",
        "action": "Airtable (create record in Clients table)"
    },
    {
        "workflow_number": 26,
        "name": "Task Completion → Update Airtable",
        "trigger": "Python script (webhook)",
        "action": "Airtable (update record status to Completed)"
    },
    {
        "workflow_number": 27,
        "name": "Document Download → Log in Airtable",
        "trigger": "GitHub Actions (workflow completion)",
        "action": "Airtable (create record in Legal Documents table)"
    },
    {
        "workflow_number": 28,
        "name": "Weekly Report → Airtable Summary",
        "trigger": "Schedule (every Monday)",
        "action": "Airtable (generate summary view) + Email report"
    }
]

# Save Zapier workflows config
with open("config/airtable/zapier_workflows.json", "w") as f:
    json.dump(zapier_workflows, f, indent=2)

print("✅ Zapier workflows config saved: config/airtable/zapier_workflows.json")

# Create example usage guide
usage_guide = """
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
"""

with open("docs/AIRTABLE_USAGE_GUIDE.md", "w") as f:
    f.write(usage_guide)

print("✅ Usage guide created: docs/AIRTABLE_USAGE_GUIDE.md")

print("\n" + "=" * 80)
print("AIRTABLE SETUP COMPLETE")
print("=" * 80)
print(f"\n📊 Bases to Create ({len(airtable_bases)}):")
for base_name in airtable_bases.keys():
    print(f"   • {base_name}")

print("\n📁 Configuration Files:")
print("   • config/airtable/config_template.json (template)")
print("   • config/airtable/config.json (create with your credentials)")
print("   • config/airtable/zapier_workflows.json (Zapier integration)")
print("   • docs/AIRTABLE_USAGE_GUIDE.md (how to use)")

print("\n🔄 Zapier Workflows:")
for workflow in zapier_workflows:
    print(f"   • Workflow #{workflow['workflow_number']}: {workflow['name']}")

print("\n🚀 Next Steps:")
print("   1. Create Airtable account (FREE)")
print("   2. Create the 3 bases listed above")
print("   3. Get API key from account settings")
print("   4. Get Base IDs from API documentation")
print("   5. Save to config/airtable/config.json")
print("   6. Run: python scripts/airtable_integration.py")

print("\n💰 Cost: FREE")
print("   • Free plan: 1,200 records per base")
print("   • Unlimited bases")
print("   • API access included")
print("   • Perfect for Agent 5.0 workflow tracking")

print("\n🎯 Use Cases:")
print("   • Track all clients and their cases")
print("   • Monitor Agent 5.0 task progress")
print("   • Log document downloads and data updates")
print("   • Visual dashboard for all operations")
print("   • Team collaboration on cases")

print("\n" + "=" * 80)
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
