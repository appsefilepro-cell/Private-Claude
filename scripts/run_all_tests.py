#!/usr/bin/env python3
"""
Run All Tests - Agent X5 System
================================

Executes all system tests, integration tests, and verification checks.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).parent.parent


def run_syntax_checks():
    """Check all Python files for syntax errors"""
    print("=" * 60)
    print("SYNTAX CHECKS")
    print("=" * 60)

    errors = []
    scripts_dir = WORKSPACE_ROOT / "scripts"

    for py_file in scripts_dir.glob("*.py"):
        try:
            with open(py_file) as f:
                compile(f.read(), py_file, "exec")
            print(f"  ✓ {py_file.name}")
        except SyntaxError as e:
            errors.append(f"{py_file.name}: {e}")
            print(f"  ✗ {py_file.name}: {e}")

    return len(errors) == 0


def run_config_validation():
    """Validate all JSON config files"""
    print("\n" + "=" * 60)
    print("CONFIG VALIDATION")
    print("=" * 60)

    errors = []
    config_dir = WORKSPACE_ROOT / "config"

    for json_file in config_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                json.load(f)
            print(f"  ✓ {json_file.name}")
        except json.JSONDecodeError as e:
            errors.append(f"{json_file.name}: {e}")
            print(f"  ✗ {json_file.name}: {e}")

    return len(errors) == 0


def run_agent_verification():
    """Verify agent configuration"""
    print("\n" + "=" * 60)
    print("AGENT VERIFICATION")
    print("=" * 60)

    status_file = WORKSPACE_ROOT / "AGENT_X5_STATUS_REPORT.json"

    if status_file.exists():
        with open(status_file) as f:
            status = json.load(f)

        total = status.get("total_agents", 0)
        active = status.get("active_agents", 0)
        mode = status.get("trading_mode", "UNKNOWN")

        print(f"  Total Agents: {total}")
        print(f"  Active Agents: {active}")
        print(f"  Trading Mode: {mode}")
        print(f"  Status: {'✓ PASS' if total == active else '✗ FAIL'}")

        return total == active
    else:
        print("  ✗ Status file not found")
        return False


def run_workflow_check():
    """Check GitHub Actions workflows"""
    print("\n" + "=" * 60)
    print("WORKFLOW CHECK")
    print("=" * 60)

    workflows_dir = WORKSPACE_ROOT / ".github" / "workflows"

    if workflows_dir.exists():
        workflows = list(workflows_dir.glob("*.yml"))
        print(f"  Found {len(workflows)} workflows:")
        for wf in workflows:
            print(f"    ✓ {wf.name}")
        return len(workflows) > 0
    else:
        print("  ✗ Workflows directory not found")
        return False


def run_api_check():
    """Check API configurations"""
    print("\n" + "=" * 60)
    print("API CHECK")
    print("=" * 60)

    api_file = WORKSPACE_ROOT / "config" / "api_keys_active.json"

    if api_file.exists():
        with open(api_file) as f:
            config = json.load(f)

        apis = config.get("api_keys_configuration", {})

        for category, providers in apis.items():
            if isinstance(providers, dict) and category not in ["description", "version", "status"]:
                print(f"  {category}:")
                for name, details in providers.items():
                    if isinstance(details, dict):
                        status = details.get("status", "UNKNOWN")
                        print(f"    ✓ {name}: {status}")

        return True
    else:
        print("  ✗ API config not found")
        return False


def generate_test_report(results):
    """Generate test report"""
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "tests_run": len(results),
        "tests_passed": sum(1 for r in results.values() if r),
        "tests_failed": sum(1 for r in results.values() if not r),
        "results": {k: "PASS" if v else "FAIL" for k, v in results.items()},
        "status": "PASS" if all(results.values()) else "FAIL"
    }

    report_path = WORKSPACE_ROOT / "test-results" / "full_system_test.json"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report


def main():
    """Run all tests"""
    print("=" * 60)
    print("AGENT X5 - FULL SYSTEM TEST")
    print("=" * 60)
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 60)

    results = {
        "syntax_checks": run_syntax_checks(),
        "config_validation": run_config_validation(),
        "agent_verification": run_agent_verification(),
        "workflow_check": run_workflow_check(),
        "api_check": run_api_check()
    }

    report = generate_test_report(results)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests Run: {report['tests_run']}")
    print(f"Tests Passed: {report['tests_passed']}")
    print(f"Tests Failed: {report['tests_failed']}")
    print(f"Overall Status: {report['status']}")
    print("=" * 60)

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
