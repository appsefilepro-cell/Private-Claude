#!/usr/bin/env python3
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
