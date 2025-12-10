"""
Zapier MCP Status Checker
Quick utility to check Zapier MCP connection and spending cap status
"""

import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from zapier_mcp_connector import ZapierMCPConnector


def print_banner():
    """Print status banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ZAPIER MCP CONNECTION STATUS CHECKER               ║
║                   Agent X2.0 Integration                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def main():
    """Main status check"""
    print_banner()

    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 64)

    # Initialize connector
    connector = ZapierMCPConnector()

    # Check configuration
    print("\n📋 CONFIGURATION:")
    print("-" * 64)
    print(f"  Endpoint: {connector.endpoint}")
    print(f"  Bearer Token: {'✓ Configured' if connector.bearer_token else '✗ Not Configured'}")
    print(f"  Webhook URL: {'✓ Configured' if connector.webhook_url else '✗ Not Configured'}")

    # Check connection
    print("\n🔌 CONNECTION STATUS:")
    print("-" * 64)
    status = connector.check_connection()

    if status.get('connected'):
        print("  Status: ✅ CONNECTED")
        print(f"  HTTP Status: {status.get('status_code')}")
    else:
        print("  Status: ❌ NOT CONNECTED")
        if 'error' in status:
            print(f"  Error: {status['error']}")
        if 'status_code' in status:
            print(f"  HTTP Status: {status['status_code']}")

    # Check spending status
    print("\n💰 SPENDING CAP STATUS:")
    print("-" * 64)
    spending = connector.get_spending_status()

    if spending.get('status') == 'active':
        print("  Status: ✅ ACTIVE (Within limits)")
    elif spending.get('status') == 'cap_reached':
        print("  Status: ⚠️  CAP REACHED")
        print("  Reset Time: 3:00 AM")
    else:
        print("  Status: ⚠️  UNKNOWN")
        if 'note' in spending:
            print(f"  Note: {spending['note']}")

    # Show next steps
    print("\n📌 NEXT STEPS:")
    print("-" * 64)

    if not status.get('connected'):
        print("  1. Verify bearer token is correct in config/.env")
        print("  2. Check if spending cap has been reached")
        print("  3. Wait until 3:00 AM for cap reset if needed")
        print("  4. Verify network connectivity")
    else:
        print("  ✓ Zapier MCP is ready to use")
        print("  → Run: python execute_zapier_integration.py")
        print("  → Or use ZapierMCPConnector in your scripts")

    print("\n" + "=" * 64)
    print("For integration examples, see:")
    print("  - pillar-a-trading/zapier-integration/zapier_mcp_connector.py")
    print("  - pillar-a-trading/agent-3.0/agent_3_orchestrator.py")
    print("=" * 64 + "\n")


if __name__ == "__main__":
    main()
