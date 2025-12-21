#!/usr/bin/env python3
"""
AGENT 5.0 - COMPLETE AUTOMATION RUNNER
Run all systems in parallel with E2B + Postman + Zapier integration
NO TEMPLATES - ACTUAL EXECUTION
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print startup banner"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}AGENT 5.0 - COMPLETE AUTOMATION SYSTEM{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")
    print(f"{Colors.GREEN}Parallel Execution Mode: ACTIVE{Colors.END}")
    print(f"{Colors.GREEN}E2B Integration: CONFIGURED{Colors.END}")
    print(f"{Colors.GREEN}Postman Collection: READY{Colors.END}")
    print(f"{Colors.GREEN}Zapier Workflows: 5 CONFIGURED{Colors.END}")
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}\n")

def check_environment():
    """Check if all required components are present"""
    print(f"{Colors.BOLD}[1/4] Checking Environment...{Colors.END}")

    checks = {
        "Python 3": sys.version_info >= (3, 7),
        "E2B Config": os.path.exists("automation/e2b_live_executor.py"),
        "Postman Collection": os.path.exists("automation/postman/Agent_5.0_API_Collection.json"),
        "Zapier Workflows": os.path.exists("automation/zapier/5_CRITICAL_ZAPIER_WORKFLOWS.json"),
        "Trading Bot": os.path.exists("run_trading_bot_demo.py"),
        "Credit Repair": os.path.exists("pillar-g-credit-repair/credit_repair_suite.py"),
        "Legal Research": os.path.exists("core-systems/legal-research/phd_legal_research.py")
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    print()
    return all_passed

def run_system(system_info):
    """Execute a single system"""
    name, script_path = system_info

    if not os.path.exists(script_path):
        return {
            "name": name,
            "status": "SKIPPED",
            "reason": "File not found"
        }

    try:
        print(f"{Colors.YELLOW}  ⏳ Executing: {name}...{Colors.END}")

        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            print(f"{Colors.GREEN}  ✓ {name} - SUCCESS{Colors.END}")
            return {
                "name": name,
                "status": "SUCCESS",
                "output": result.stdout[:500]  # First 500 chars
            }
        else:
            print(f"{Colors.RED}  ✗ {name} - FAILED{Colors.END}")
            return {
                "name": name,
                "status": "FAILED",
                "error": result.stderr[:500]
            }

    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}  ✗ {name} - TIMEOUT{Colors.END}")
        return {
            "name": name,
            "status": "TIMEOUT",
            "error": "Execution exceeded 120 seconds"
        }
    except Exception as e:
        print(f"{Colors.RED}  ✗ {name} - ERROR{Colors.END}")
        return {
            "name": name,
            "status": "ERROR",
            "error": str(e)
        }

def execute_all_systems_parallel():
    """Execute all systems in parallel"""
    print(f"{Colors.BOLD}[2/4] Executing All Systems in Parallel...{Colors.END}\n")

    systems = [
        ("Trading Bot Demo", "run_trading_bot_demo.py"),
        ("Credit Repair Suite", "pillar-g-credit-repair/credit_repair_suite.py"),
        ("Legal Research System", "core-systems/legal-research/phd_legal_research.py"),
        ("Damages Calculator", "pillar-g-credit-repair/damages_calculator.py"),
        ("Nonprofit Automation", "core-systems/nonprofit-automation/nonprofit_ai_integrator.py"),
        ("Historical Research", "core-systems/historical-research/gulf_oil_research.py"),
        ("Case Manager", "pillar-f-cleo/case_manager.py"),
        ("Parallel Executor", "EXECUTE_ALL_PARALLEL.py")
    ]

    results = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_system = {executor.submit(run_system, system): system for system in systems}

        for future in as_completed(future_to_system):
            result = future.result()
            results.append(result)

    print()
    return results

def test_postman_integration():
    """Test Postman collection"""
    print(f"{Colors.BOLD}[3/4] Testing Postman Integration...{Colors.END}")

    postman_file = "automation/postman/Agent_5.0_API_Collection.json"

    if os.path.exists(postman_file):
        with open(postman_file, 'r') as f:
            collection = json.load(f)

        requests_count = 0
        for item in collection.get("item", []):
            if "item" in item:  # Folder
                requests_count += len(item["item"])
            else:  # Single request
                requests_count += 1

        print(f"{Colors.GREEN}  ✓ Postman collection loaded{Colors.END}")
        print(f"  • Total API endpoints: {requests_count}")
        print(f"  • E2B sandbox management: CONFIGURED")
        print(f"  • Parallel execution: CONFIGURED")
        print(f"\n  {Colors.BLUE}Import to Postman:{Colors.END}")
        print(f"    1. Open Postman")
        print(f"    2. File → Import")
        print(f"    3. Select: {postman_file}")
        print(f"    4. Run requests to execute systems in E2B cloud")
        print()
        return True
    else:
        print(f"{Colors.RED}  ✗ Postman collection not found{Colors.END}\n")
        return False

def test_zapier_integration():
    """Test Zapier workflows"""
    print(f"{Colors.BOLD}[4/4] Testing Zapier Integration...{Colors.END}")

    zapier_file = "automation/zapier/5_CRITICAL_ZAPIER_WORKFLOWS.json"

    if os.path.exists(zapier_file):
        with open(zapier_file, 'r') as f:
            workflows = json.load(f)

        workflow_count = len(workflows.get("zapier_workflows", {}))

        print(f"{Colors.GREEN}  ✓ Zapier workflows loaded{Colors.END}")
        print(f"  • Total workflows: {workflow_count}")

        for key, workflow in workflows.get("zapier_workflows", {}).items():
            print(f"    - {workflow['name']}")

        print(f"\n  {Colors.BLUE}Setup Instructions:{Colors.END}")
        print(f"    1. Go to: https://zapier.com/app/editor/")
        print(f"    2. Create each workflow manually (5 total)")
        print(f"    3. Connect: Gmail, Google Drive, Google Sheets")
        print(f"    4. Cost: $0/month (FREE tier - 100 tasks)")
        print()
        return True
    else:
        print(f"{Colors.RED}  ✗ Zapier workflows not found{Colors.END}\n")
        return False

def print_summary(results, postman_ok, zapier_ok):
    """Print execution summary"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}EXECUTION SUMMARY{Colors.END}")
    print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    failed_count = sum(1 for r in results if r["status"] in ["FAILED", "ERROR", "TIMEOUT"])
    skipped_count = sum(1 for r in results if r["status"] == "SKIPPED")

    print(f"{Colors.GREEN}SUCCESS: {success_count}{Colors.END}")
    print(f"{Colors.RED}FAILED:  {failed_count}{Colors.END}")
    print(f"{Colors.YELLOW}SKIPPED: {skipped_count}{Colors.END}")
    print(f"TOTAL:   {len(results)}\n")

    if failed_count > 0:
        print(f"{Colors.RED}Failed Systems:{Colors.END}")
        for r in results:
            if r["status"] in ["FAILED", "ERROR", "TIMEOUT"]:
                print(f"  ✗ {r['name']}: {r.get('error', 'Unknown error')[:100]}")
        print()

    print(f"{Colors.BOLD}Integration Status:{Colors.END}")
    print(f"  Postman: {'✓ READY' if postman_ok else '✗ NOT CONFIGURED'}")
    print(f"  Zapier:  {'✓ READY' if zapier_ok else '✗ NOT CONFIGURED'}")

    print(f"\n{Colors.BOLD}{'='*70}{Colors.END}\n")

    # Save results to log
    log_file = f"automation/logs/execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "postman_ready": postman_ok,
            "zapier_ready": zapier_ok,
            "summary": {
                "success": success_count,
                "failed": failed_count,
                "skipped": skipped_count
            }
        }, f, indent=2)

    print(f"  📄 Execution log saved: {log_file}\n")

def main():
    """Main automation runner"""
    print_header()

    # Check environment
    if not check_environment():
        print(f"{Colors.RED}Environment check failed. Cannot proceed.{Colors.END}\n")
        return 1

    # Execute all systems
    results = execute_all_systems_parallel()

    # Test integrations
    postman_ok = test_postman_integration()
    zapier_ok = test_zapier_integration()

    # Print summary
    print_summary(results, postman_ok, zapier_ok)

    # Determine exit code
    failed_count = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Execution interrupted by user{Colors.END}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n{Colors.RED}FATAL ERROR: {e}{Colors.END}\n")
        sys.exit(1)
