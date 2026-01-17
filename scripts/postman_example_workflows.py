"""
Example Workflow: Postman API Integration with Agent X5.0
Demonstrates complete integration workflow
"""

import os
import sys
from pathlib import Path

# Add integration path
sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'zapier-integration'))

from postman_mcp_connector import PostmanMCPConnector
import json


def example_1_basic_connection():
    """Example 1: Check basic Postman API connection"""
    print("\n" + "=" * 70)
    print("Example 1: Check Postman API Connection")
    print("=" * 70 + "\n")
    
    connector = PostmanMCPConnector()
    
    # Check VS Code authentication
    auth_status = connector.authenticate_vscode_extension()
    print("VS Code Extension Authentication:")
    print(json.dumps(auth_status, indent=2))
    
    if auth_status.get('authenticated'):
        print("\n✓ VS Code extension can be authenticated")
        print(f"Use this URL: {auth_status['extension_url']}")
    else:
        print("\n⚠ Configure POSTMAN_VSCODE_AUTH_CODE in config/.env")


def example_2_trading_api_test():
    """Example 2: Create trading API test configuration"""
    print("\n" + "=" * 70)
    print("Example 2: Create Trading API Test")
    print("=" * 70 + "\n")
    
    connector = PostmanMCPConnector()
    
    # Define trading endpoints to test
    endpoints = [
        {"url": "http://localhost:8000/api/health", "method": "GET"},
        {"url": "http://localhost:8000/api/market/BTC-USD", "method": "GET"},
        {"url": "http://localhost:8000/api/trade/signal", "method": "POST"}
    ]
    
    print("Creating test configurations for trading API endpoints:\n")
    
    for endpoint in endpoints:
        test_config = connector.integrate_with_trading_bot(
            api_endpoint=endpoint['url'],
            method=endpoint['method']
        )
        
        print(f"✓ {test_config['name']}")
        print(f"  Method: {test_config['request']['method']}")
        print(f"  URL: {test_config['request']['url']}")
        print(f"  Tests: {len(test_config['event'])} test scripts")
        print()


def example_3_create_collection():
    """Example 3: Create a new Postman collection"""
    print("\n" + "=" * 70)
    print("Example 3: Create Postman Collection")
    print("=" * 70 + "\n")
    
    connector = PostmanMCPConnector()
    
    collection_data = {
        "name": "Agent X5.0 Trading Bot API",
        "description": "Automated tests for Agent X5.0 trading bot endpoints including market data, trade signals, and health checks"
    }
    
    print(f"Creating collection: {collection_data['name']}")
    print(f"Description: {collection_data['description']}\n")
    
    # Note: This will only work if API key is configured
    print("💡 To actually create the collection:")
    print("   1. Configure POSTMAN_API_KEY in config/.env")
    print("   2. Run: connector.create_collection(name='...', description='...')")
    print()


def example_4_monitoring_setup():
    """Example 4: Set up API monitoring"""
    print("\n" + "=" * 70)
    print("Example 4: Set Up API Monitoring")
    print("=" * 70 + "\n")
    
    # Monitor configuration
    monitor_config = {
        "name": "Trading API Health Monitor",
        "schedule": {
            "cron": "0 */6 * * *",  # Every 6 hours
            "timezone": "America/Los_Angeles"
        },
        "notifications": {
            "on_failure": True,
            "email": "alerts@example.com"
        }
    }
    
    print("Monitor Configuration:")
    print(json.dumps(monitor_config, indent=2))
    print()
    
    print("This monitor will:")
    print("  • Run every 6 hours")
    print("  • Test all API endpoints")
    print("  • Send email alerts on failure")
    print("  • Log results for tracking")
    print()
    
    print("💡 To create this monitor:")
    print("   1. Create a collection with your tests")
    print("   2. Get the collection ID")
    print("   3. Run: connector.create_monitor(collection_id='...', name='...', schedule={...})")
    print()


def example_5_vscode_workflow():
    """Example 5: VS Code Extension Workflow"""
    print("\n" + "=" * 70)
    print("Example 5: VS Code Extension Workflow")
    print("=" * 70 + "\n")
    
    connector = PostmanMCPConnector()
    auth = connector.authenticate_vscode_extension()
    
    if auth.get('authenticated'):
        print("✓ VS Code Extension Authentication Ready\n")
        print("Step-by-step workflow:")
        print()
        print("1. Install Postman Extension in VS Code:")
        print("   - Open VS Code")
        print("   - Go to Extensions (Ctrl+Shift+X)")
        print("   - Search for 'Postman'")
        print("   - Click Install")
        print()
        print("2. Authenticate using the provided code:")
        print(f"   Click this link: {auth['extension_url']}")
        print()
        print("3. Use Postman in VS Code:")
        print("   - Access collections from sidebar")
        print("   - Send API requests directly from editor")
        print("   - Debug responses in real-time")
        print("   - Sync with Postman Cloud")
        print()
    else:
        print("⚠ VS Code authentication not configured")
        print()
        print("To set up:")
        print("1. Add to config/.env:")
        print("   POSTMAN_VSCODE_AUTH_CODE=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe")
        print()


def example_6_complete_workflow():
    """Example 6: Complete automation workflow"""
    print("\n" + "=" * 70)
    print("Example 6: Complete Automation Workflow")
    print("=" * 70 + "\n")
    
    print("Complete workflow combining all features:\n")
    
    workflow_steps = [
        {
            "step": 1,
            "name": "Create Collections",
            "description": "Create test collections for all API endpoints",
            "tools": ["Postman API", "Python Script"]
        },
        {
            "step": 2,
            "name": "Define Tests",
            "description": "Add test scripts to validate responses",
            "tools": ["VS Code Extension", "Postman Cloud"]
        },
        {
            "step": 3,
            "name": "Set Up Monitors",
            "description": "Schedule automatic test runs every 6 hours",
            "tools": ["Postman API", "Monitor API"]
        },
        {
            "step": 4,
            "name": "Configure Alerts",
            "description": "Connect to Zapier for alert automation",
            "tools": ["Zapier", "Email", "Slack"]
        },
        {
            "step": 5,
            "name": "Log Results",
            "description": "Store test results in Google Sheets",
            "tools": ["Zapier", "Google Sheets"]
        },
        {
            "step": 6,
            "name": "CI/CD Integration",
            "description": "Run tests in GitHub Actions pipeline",
            "tools": ["Newman CLI", "GitHub Actions"]
        }
    ]
    
    for step in workflow_steps:
        print(f"Step {step['step']}: {step['name']}")
        print(f"  Description: {step['description']}")
        print(f"  Tools: {', '.join(step['tools'])}")
        print()
    
    print("Benefits of this workflow:")
    print("  ✓ 24/7 automated API monitoring")
    print("  ✓ Instant alerts on failures")
    print("  ✓ Historical test result tracking")
    print("  ✓ Integration with existing tools")
    print("  ✓ Automated incident response")
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("  POSTMAN API MCP INTEGRATION - EXAMPLE WORKFLOWS")
    print("  Agent X5.0 - APPS Holdings WY Inc.")
    print("=" * 70)
    
    # Run all examples
    example_1_basic_connection()
    example_2_trading_api_test()
    example_3_create_collection()
    example_4_monitoring_setup()
    example_5_vscode_workflow()
    example_6_complete_workflow()
    
    # Final notes
    print("\n" + "=" * 70)
    print("  GETTING STARTED")
    print("=" * 70 + "\n")
    
    print("Quick Start:")
    print("1. Run setup script:")
    print("   ./scripts/setup_postman_mcp.sh")
    print()
    print("2. Configure API keys in config/.env:")
    print("   POSTMAN_API_KEY=your_api_key")
    print("   POSTMAN_VSCODE_AUTH_CODE=482ee78e89079905b270c99d578eb06ae729773eb796e9544ba5e96ea37923fe")
    print()
    print("3. Test connection:")
    print("   python pillar-a-trading/zapier-integration/postman_mcp_connector.py")
    print()
    print("4. Read full documentation:")
    print("   docs/POSTMAN_API_INTEGRATION.md")
    print()
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
