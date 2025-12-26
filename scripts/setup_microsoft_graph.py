#!/usr/bin/env python3
"""
MICROSOFT GRAPH API SETUP - Word, Excel, OneDrive, Outlook
Integration for Agent 5.0 document templates
"""
import os
import json
from datetime import datetime

print("=" * 80)
print("MICROSOFT GRAPH API INTEGRATION SETUP")
print("=" * 80)
print(f"Services: Word, Excel, OneDrive, Outlook")
print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Create config directory
os.makedirs("config/microsoft", exist_ok=True)
os.makedirs("data/microsoft_templates", exist_ok=True)

# Microsoft Graph API services
graph_services = {
    "Microsoft Word Online": {
        "purpose": "Legal document templates",
        "scope": "Files.ReadWrite.All",
        "features": [
            "Create legal document templates",
            "Generate contracts from templates",
            "Merge data into Word documents",
            "Export to PDF",
            "Cloud-based editing"
        ]
    },
    "Microsoft Excel Online": {
        "purpose": "Financial tracking and data analysis",
        "scope": "Files.ReadWrite.All",
        "features": [
            "Trading bot performance tracking",
            "Market data analysis",
            "Financial calculations",
            "Charts and visualizations",
            "Data import/export"
        ]
    },
    "OneDrive": {
        "purpose": "Document storage and sharing",
        "scope": "Files.ReadWrite.All",
        "features": [
            "5GB free storage",
            "Automatic sync",
            "Version history",
            "Share files with team",
            "Mobile access"
        ]
    },
    "Outlook": {
        "purpose": "Email integration (alternative to Gmail)",
        "scope": "Mail.ReadWrite",
        "features": [
            "Send/receive emails",
            "Calendar integration",
            "Contact management",
            "Task tracking",
            "Rules and automation"
        ]
    }
}

print("\nMICROSOFT GRAPH SERVICES:")
print("=" * 80)
for service_name, service_info in graph_services.items():
    print(f"\n{service_name}")
    print(f"  Purpose: {service_info['purpose']}")
    print(f"  Scope: {service_info['scope']}")
    print(f"  Features:")
    for feature in service_info['features']:
        print(f"    - {feature}")

# Azure AD App Registration config
app_registration = {
    "appId": "YOUR_APPLICATION_ID",
    "displayName": "Agent 5.0 Automation",
    "tenantId": "YOUR_TENANT_ID",
    "authority": "https://login.microsoftonline.com/YOUR_TENANT_ID",
    "clientId": "YOUR_CLIENT_ID",
    "clientSecret": "YOUR_CLIENT_SECRET",
    "scopes": [
        "https://graph.microsoft.com/Files.ReadWrite.All",
        "https://graph.microsoft.com/Mail.ReadWrite",
        "https://graph.microsoft.com/User.Read",
        "https://graph.microsoft.com/Calendars.ReadWrite"
    ]
}

# Save app registration template
with open("config/microsoft/app_registration_template.json", "w") as f:
    json.dump(app_registration, f, indent=2)

print("\n" + "=" * 80)
print("AZURE AD APP REGISTRATION SETUP")
print("=" * 80)
print("\n1. Go to Azure Portal:")
print("   https://portal.azure.com/")
print("\n2. Navigate to: Azure Active Directory > App registrations")
print("\n3. Click: + New registration")
print("   - Name: Agent 5.0 Automation")
print("   - Supported account types: Single tenant")
print("   - Redirect URI: Web - http://localhost:8080/")
print("\n4. After creation, note:")
print("   - Application (client) ID")
print("   - Directory (tenant) ID")
print("\n5. Create client secret:")
print("   - Go to: Certificates & secrets")
print("   - Click: + New client secret")
print("   - Description: Agent 5.0")
print("   - Expires: 24 months")
print("   - Copy the secret VALUE (not the ID)")
print("\n6. Configure API permissions:")
print("   - Go to: API permissions")
print("   - Add these Microsoft Graph permissions:")
print("     • Files.ReadWrite.All (Delegated)")
print("     • Mail.ReadWrite (Delegated)")
print("     • User.Read (Delegated)")
print("     • Calendars.ReadWrite (Delegated)")
print("   - Click: Grant admin consent")
print("\n7. Save credentials to:")
print("   config/microsoft/app_credentials.json")

# Create authentication script
auth_script = """#!/usr/bin/env python3
import os
import json
from msal import ConfidentialClientApplication

def authenticate_microsoft_graph():
    # Load credentials
    creds_file = 'config/microsoft/app_credentials.json'

    if not os.path.exists(creds_file):
        print("ERROR: Credentials file not found!")
        print(f"Please create: {creds_file}")
        print("Follow setup instructions to get credentials from Azure Portal")
        return None

    with open(creds_file, 'r') as f:
        config = json.load(f)

    # Create MSAL application
    app = ConfidentialClientApplication(
        config['clientId'],
        authority=config['authority'],
        client_credential=config['clientSecret']
    )

    # Get access token
    result = app.acquire_token_for_client(scopes=config['scopes'])

    if 'access_token' in result:
        print("✅ Microsoft Graph API authenticated successfully!")

        # Save token
        token_file = 'data/microsoft_credentials/token.json'
        os.makedirs('data/microsoft_credentials', exist_ok=True)

        with open(token_file, 'w') as f:
            json.dump({
                'access_token': result['access_token'],
                'expires_in': result['expires_in'],
                'token_type': result['token_type']
            }, f, indent=2)

        print(f"   Token saved to: {token_file}")
        return result['access_token']
    else:
        print("⚠️ Authentication failed:")
        print(f"   {result.get('error')}")
        print(f"   {result.get('error_description')}")
        return None

if __name__ == '__main__':
    print("=" * 80)
    print("MICROSOFT GRAPH API AUTHENTICATION")
    print("=" * 80)
    token = authenticate_microsoft_graph()
    if token:
        print("\\n✅ Authentication complete!")
        print("   Microsoft Graph API is now accessible")
    else:
        print("\\n⚠️ Authentication failed")
        print("   Follow setup instructions to configure Azure AD app")
"""

with open("scripts/microsoft_graph_auth.py", "w") as f:
    f.write(auth_script)

os.chmod("scripts/microsoft_graph_auth.py", 0o755)
print("\n✅ Authentication script created: scripts/microsoft_graph_auth.py")

# Document templates configuration
templates_config = {
    "timestamp": datetime.now().isoformat(),
    "templates": {
        "legal_contracts": {
            "format": "Word (.docx)",
            "location": "OneDrive/Templates/Legal/",
            "templates": [
                "Service Agreement Template",
                "Non-Disclosure Agreement (NDA)",
                "Independent Contractor Agreement",
                "Consulting Agreement",
                "Client Onboarding Form"
            ]
        },
        "financial_spreadsheets": {
            "format": "Excel (.xlsx)",
            "location": "OneDrive/Templates/Financial/",
            "templates": [
                "Trading Bot Performance Tracker",
                "Monthly Revenue Report",
                "Expense Tracker",
                "Invoice Template",
                "Budget Planner"
            ]
        }
    },
    "delegation": {
        "Legal Division": "Word templates for contracts",
        "Finance Division": "Excel spreadsheets for tracking",
        "Integration Division": "OneDrive sync automation",
        "Communication Division": "Outlook email integration"
    }
}

with open("config/microsoft/templates_config.json", "w") as f:
    json.dump(templates_config, f, indent=2)

print("✅ Templates config saved: config/microsoft/templates_config.json")

print("\n" + "=" * 80)
print("MICROSOFT GRAPH API SETUP COMPLETE")
print("=" * 80)
print(f"\n📋 Services Configured ({len(graph_services)}):")
for service_name in graph_services.keys():
    print(f"   • {service_name}")

print("\n📁 Configuration Files:")
print("   • config/microsoft/app_registration_template.json (template)")
print("   • config/microsoft/app_credentials.json (create after Azure setup)")
print("   • config/microsoft/templates_config.json (templates configuration)")
print("   • data/microsoft_credentials/token.json (created after auth)")

print("\n📄 Document Templates:")
print("   • Legal contracts: 5 templates")
print("   • Financial spreadsheets: 5 templates")

print("\n🚀 Next Steps:")
print("   1. Follow instructions above to create Azure AD app")
print("   2. Save credentials to config/microsoft/app_credentials.json")
print("   3. Run: python scripts/microsoft_graph_auth.py")
print("   4. Use Microsoft Graph API for document generation")

print("\n💰 Cost: FREE")
print("   • Microsoft 365 Personal: FREE trial (1 month)")
print("   • OneDrive: 5GB free storage")
print("   • Word/Excel Online: FREE with Microsoft account")
print("   • Outlook: FREE email service")

print("\n🔄 Zapier Integrations:")
print("   • Workflow #22: Word template → PDF generation")
print("   • Workflow #23: Excel data sync to Google Sheets")
print("   • Workflow #24: OneDrive file upload notification")

print("\n" + "=" * 80)
print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
