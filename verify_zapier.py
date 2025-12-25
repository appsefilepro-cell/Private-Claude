#!/usr/bin/env python3
"""
ZAPIER WEBHOOK VERIFICATION SCRIPT
===================================

Simple script to test all your Zapier webhooks.
NO coding knowledge required - just run it!

Usage:
    python verify_zapier.py

What it does:
- Tests all your webhook URLs
- Sends sample data to each webhook
- Verifies they're working
- Shows you the results

Author: Automated Testing System
Date: 2025-12-25
"""

import requests
import json
import time
from datetime import datetime

# ANSI color codes for pretty output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_header():
    """Print welcome header"""
    print(f"\n{BLUE}{BOLD}{'='*60}{RESET}")
    print(f"{BLUE}{BOLD}           ZAPIER WEBHOOK TESTER{RESET}")
    print(f"{BLUE}{BOLD}         No Coding Knowledge Required!{RESET}")
    print(f"{BLUE}{BOLD}{'='*60}{RESET}\n")

def print_section(title):
    """Print section header"""
    print(f"\n{YELLOW}{BOLD}--- {title} ---{RESET}\n")

def test_webhook(name, url, test_data):
    """
    Test a single webhook

    Args:
        name: Name of the webhook (e.g., "OKX Trading")
        url: Webhook URL
        test_data: Dictionary of test data to send

    Returns:
        True if successful, False otherwise
    """
    print(f"Testing {BOLD}{name}{RESET}...")
    print(f"URL: {url}")
    print(f"Sending test data...")

    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        if response.status_code == 200:
            print(f"{GREEN}✅ SUCCESS!{RESET} Webhook is working!")
            print(f"Response: {response.text[:100]}")
            return True
        else:
            print(f"{RED}❌ FAILED!{RESET} Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"{RED}❌ TIMEOUT!{RESET} Webhook took too long to respond")
        return False

    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ CONNECTION ERROR!{RESET} Could not connect to webhook")
        print(f"{YELLOW}Is the URL correct?{RESET}")
        return False

    except Exception as e:
        print(f"{RED}❌ ERROR!{RESET} {str(e)}")
        return False

def main():
    """Main testing function"""
    print_header()

    print(f"{BOLD}Instructions:{RESET}")
    print("1. Replace 'YOUR_WEBHOOK_URL' below with your actual Zapier webhook URLs")
    print("2. Run this script: python verify_zapier.py")
    print("3. Check your email, Slack, and Google Sheets for test notifications")
    print("\nPress Enter to continue...")
    input()

    # Configure your webhook URLs here
    # Replace these with your actual webhook URLs from Zapier
    WEBHOOKS = {
        "OKX Trading": {
            "url": "YOUR_OKX_WEBHOOK_URL",  # Replace this!
            "test_data": {
                "timestamp": datetime.now().isoformat(),
                "pair": "BTC/USDT",
                "side": "BUY",
                "amount": "0.05",
                "price": "45000.00",
                "pattern": "TEST - Golden Cross",
                "pnl": "+$250.00",
                "test_mode": True
            }
        },
        "Error Alerts": {
            "url": "YOUR_ERROR_WEBHOOK_URL",  # Replace this!
            "test_data": {
                "timestamp": datetime.now().isoformat(),
                "system": "Verification Script",
                "error_message": "This is a TEST error - everything is working!",
                "severity": "LOW",
                "test_mode": True
            }
        },
        "Legal Documents": {
            "url": "YOUR_LEGAL_WEBHOOK_URL",  # Replace this!
            "test_data": {
                "case_number": "TEST-12345",
                "court": "Test County Court",
                "plaintiff": "Test Plaintiff LLC",
                "defendant": "Test Defendant",
                "document_type": "Test Notice",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "test_mode": True
            }
        },
        "Test Completion": {
            "url": "YOUR_TEST_WEBHOOK_URL",  # Replace this!
            "test_data": {
                "test_id": f"TEST-{int(time.time())}",
                "test_name": "Zapier Webhook Verification",
                "timestamp": datetime.now().isoformat(),
                "results": "All webhook tests completed successfully!",
                "pass_rate": "100",
                "total_tests": "4",
                "passed_tests": "4",
                "failed_tests": "0",
                "test_mode": True
            }
        }
    }

    # Check if URLs have been configured
    unconfigured = [name for name, config in WEBHOOKS.items()
                    if config['url'].startswith('YOUR_')]

    if unconfigured:
        print_section("⚠️  CONFIGURATION NEEDED")
        print(f"{YELLOW}The following webhooks need to be configured:{RESET}")
        for name in unconfigured:
            print(f"  • {name}")
        print(f"\n{BOLD}How to configure:{RESET}")
        print("1. Open this file in a text editor")
        print("2. Find the WEBHOOKS section (around line 82)")
        print("3. Replace 'YOUR_..._WEBHOOK_URL' with your actual URLs from Zapier")
        print("4. Save the file and run again")
        print(f"\n{YELLOW}Continuing with configured webhooks...{RESET}\n")
        time.sleep(2)

    # Run tests
    print_section("Running Tests")
    results = {}

    for name, config in WEBHOOKS.items():
        if config['url'].startswith('YOUR_'):
            print(f"{YELLOW}⏭️  SKIPPING{RESET} {name} - not configured yet")
            results[name] = None
        else:
            success = test_webhook(name, config['url'], config['test_data'])
            results[name] = success
            print()  # Blank line between tests
            time.sleep(1)  # Wait 1 second between tests

    # Print summary
    print_section("Test Results Summary")

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)

    for name, result in results.items():
        if result is True:
            print(f"{GREEN}✅ PASSED{RESET} - {name}")
        elif result is False:
            print(f"{RED}❌ FAILED{RESET} - {name}")
        else:
            print(f"{YELLOW}⏭️  SKIPPED{RESET} - {name}")

    print(f"\n{BOLD}Total:{RESET} {len(results)} webhooks tested")
    print(f"{GREEN}Passed:{RESET} {passed}")
    print(f"{RED}Failed:{RESET} {failed}")
    print(f"{YELLOW}Skipped:{RESET} {skipped}")

    # Verification checklist
    print_section("Verification Checklist")
    print(f"{BOLD}Please check the following:{RESET}\n")
    print("□ Check your email (terobinsonwy@gmail.com)")
    print("□ Check your Google Sheets (OKX Trading Log)")
    print("□ Check your Slack channels (#trading-alerts, #system-status)")
    print("□ Check Zapier History: https://zapier.com/app/history")

    if failed > 0:
        print(f"\n{YELLOW}{BOLD}Troubleshooting:{RESET}")
        print("1. Make sure your Zaps are turned ON in Zapier")
        print("2. Check that webhook URLs are correct (no extra spaces)")
        print("3. Verify all apps are connected in Zapier")
        print("4. Check Zapier History for detailed error messages")
        print("5. Try turning the Zap OFF and ON again")

    if passed > 0:
        print(f"\n{GREEN}{BOLD}🎉 Webhooks are working! Check your notifications!{RESET}\n")

    print(f"{BLUE}{'='*60}{RESET}\n")

if __name__ == "__main__":
    # Check if requests library is installed
    try:
        import requests
    except ImportError:
        print(f"{RED}ERROR:{RESET} requests library not found")
        print(f"\n{BOLD}Installation instructions:{RESET}")
        print("Run this command to install:")
        print(f"  {YELLOW}pip install requests{RESET}")
        print("\nOr use the HTML test page instead:")
        print(f"  Open {YELLOW}verify_zapier.html{RESET} in your web browser")
        exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Test cancelled by user{RESET}")
        exit(0)
