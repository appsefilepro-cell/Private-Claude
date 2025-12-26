#!/usr/bin/env python3
"""
ADD 5 NEW CLIENTS TO AGENT X5 - READY FOR PRESENTATION
Run: python3 add_5_clients_now.py
"""

import sqlite3
import json
from datetime import datetime

print("🚀 ADDING 5 NEW CLIENTS TO AGENT X5")
print("=" * 60)

# Connect to Cleo database
db_path = "pillar-f-cleo/cleo_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure tables exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    client_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    client_type TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS matters (
    matter_id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER,
    matter_name TEXT,
    matter_type TEXT,
    status TEXT DEFAULT 'active',
    estimated_value REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(client_id)
)
''')

conn.commit()

# 5 New Clients for Presentation
clients = [
    {
        "name": "John Anderson Estate",
        "email": "janderson@example.com",
        "phone": "+1-555-0101",
        "client_type": "Estate",
        "matter": "Probate Administration - Anderson Estate",
        "matter_type": "Probate",
        "value": 450000
    },
    {
        "name": "Maria Rodriguez",
        "email": "mrodriguez@example.com",
        "phone": "+1-555-0102",
        "client_type": "Individual",
        "matter": "Credit Repair - 3 Bureau Disputes",
        "matter_type": "Credit Repair",
        "value": 15000
    },
    {
        "name": "Tech Startup LLC",
        "email": "legal@techstartup.com",
        "phone": "+1-555-0103",
        "client_type": "Business",
        "matter": "Business Formation & Contracts",
        "matter_type": "Business Law",
        "value": 25000
    },
    {
        "name": "Sarah Johnson",
        "email": "sjohnson@example.com",
        "phone": "+1-555-0104",
        "client_type": "Individual",
        "matter": "Tax Preparation - 1040 + Schedule C",
        "matter_type": "Tax Services",
        "value": 2500
    },
    {
        "name": "Community Nonprofit Inc",
        "email": "info@communitynonprofit.org",
        "phone": "+1-555-0105",
        "client_type": "Nonprofit",
        "matter": "501(c)(3) Application - Form 1023",
        "matter_type": "Nonprofit Formation",
        "value": 5000
    }
]

added_clients = []

for idx, client in enumerate(clients, 1):
    # Add client
    cursor.execute('''
        INSERT INTO clients (name, email, phone, client_type, status)
        VALUES (?, ?, ?, ?, 'active')
    ''', (client['name'], client['email'], client['phone'], client['client_type']))
    
    client_id = cursor.lastrowid
    
    # Add matter
    cursor.execute('''
        INSERT INTO matters (client_id, matter_name, matter_type, status, estimated_value)
        VALUES (?, ?, ?, 'active', ?)
    ''', (client_id, client['matter'], client['matter_type'], client['value']))
    
    matter_id = cursor.lastrowid
    
    added_clients.append({
        "client_id": client_id,
        "matter_id": matter_id,
        **client
    })
    
    print(f"✅ Client {idx}: {client['name']}")
    print(f"   ID: {client_id} | Matter: {client['matter']}")
    print(f"   Value: ${client['value']:,.2f}")
    print()

conn.commit()

# Verify total clients
cursor.execute("SELECT COUNT(*) FROM clients")
total_clients = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM matters")
total_matters = cursor.fetchone()[0]

# Get all clients for display
cursor.execute('''
    SELECT c.client_id, c.name, c.email, c.client_type, m.matter_name, m.estimated_value
    FROM clients c
    LEFT JOIN matters m ON c.client_id = m.client_id
    ORDER BY c.client_id DESC
    LIMIT 10
''')

recent_clients = cursor.fetchall()

conn.close()

# Save results
with open('new_clients_added.json', 'w') as f:
    json.dump(added_clients, f, indent=2)

print("=" * 60)
print("📊 AGENT X5 CLIENT DATABASE STATUS")
print("=" * 60)
print(f"Total Clients in System: {total_clients}")
print(f"Total Active Matters: {total_matters}")
print(f"New Clients Added: 5")
print()
print("Recent Clients:")
print("-" * 60)
for client in recent_clients[:5]:
    print(f"ID {client[0]}: {client[1]}")
    print(f"  Type: {client[3]} | Matter: {client[4]}")
    print(f"  Value: ${client[5]:,.2f}" if client[5] else "  Value: N/A")
    print()

print("=" * 60)
print("✅ READY FOR PRESENTATION!")
print("=" * 60)
print()
print("📋 Client details saved to: new_clients_added.json")
print("🗄️  Database location: pillar-f-cleo/cleo_database.db")
print()
print("🚀 Next: Show the API with these clients")
print("   Run: uvicorn api.main:app --reload")
print("   URL: http://localhost:8000/api/docs")
print()
