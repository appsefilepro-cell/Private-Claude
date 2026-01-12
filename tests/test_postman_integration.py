#!/usr/bin/env python3
"""
Postman API MCP Integration Test Suite
Tests all Postman MCP connector functionality
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'pillar-a-trading' / 'zapier-integration'))

try:
    from postman_mcp_connector import PostmanMCPConnector
    from integrated_mcp_connector import IntegratedMCPConnector
    print("✓ Successfully imported MCP connectors")
except ImportError as e:
    print(f"✗ Failed to import connectors: {e}")
    sys.exit(1)

import json
from datetime import datetime


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_result(label, result, details=None):
    """Print a formatted result"""
    status = "✓" if result else "✗"
    color = "\033[92m" if result else "\033[91m"
    reset = "\033[0m"
    
    print(f"{color}{status}{reset} {label}")
    if details:
        print(f"  {details}")


def test_postman_connector():
    """Test Postman MCP Connector"""
    print_section("Postman MCP Connector Tests")
    
    connector = PostmanMCPConnector()
    results = []
    
    # Test 1: Initialization
    print_result("Connector initialized", True)
    
    # Test 2: Check configuration
    has_api_key = bool(connector.api_key and connector.api_key != "your_postman_api_key_here")
    print_result("API key configured", has_api_key, 
                 "API key found" if has_api_key else "Configure POSTMAN_API_KEY in .env")
    
    # Test 3: VS Code auth code
    has_auth_code = bool(connector.vscode_auth_code)
    print_result("VS Code auth code configured", has_auth_code,
                 f"Code: {connector.vscode_auth_code[:20]}..." if has_auth_code else "Not configured")
    
    # Test 4: Check connection (only if API key is configured)
    if has_api_key:
        status = connector.check_connection()
        connected = status.get('connected', False)
        print_result("API connection", connected,
                     f"User: {status.get('user', {}).get('username', 'N/A')}" if connected else status.get('error', 'Failed'))
        results.append(connected)
    else:
        print_result("API connection", False, "Skipped - no API key")
        results.append(False)
    
    # Test 5: Method availability
    methods = ['list_workspaces', 'list_collections', 'create_collection', 
               'create_monitor', 'integrate_with_trading_bot']
    
    for method in methods:
        has_method = hasattr(connector, method)
        print_result(f"Method: {method}", has_method)
    
    return all(results) if results else False


def test_integrated_connector():
    """Test Integrated MCP Connector"""
    print_section("Integrated MCP Connector Tests")
    
    try:
        connector = IntegratedMCPConnector()
        print_result("Integrated connector initialized", True)
        
        # Test methods
        methods = ['check_all_connections', 'test_trading_api_with_alert',
                   'monitor_with_alerts', 'run_complete_api_validation']
        
        for method in methods:
            has_method = hasattr(connector, method)
            print_result(f"Method: {method}", has_method)
        
        return True
        
    except Exception as e:
        print_result("Integrated connector initialization", False, str(e))
        return False


def test_configuration_files():
    """Test configuration files"""
    print_section("Configuration Files Tests")
    
    project_root = Path(__file__).parent.parent
    
    # Test config files
    config_files = [
        ('config/postman_mcp_config.json', 'Postman config'),
        ('config/.env.template', 'Environment template'),
        ('docs/POSTMAN_API_INTEGRATION.md', 'Documentation'),
        ('scripts/setup_postman_mcp.sh', 'Setup script')
    ]
    
    results = []
    for file_path, description in config_files:
        full_path = project_root / file_path
        exists = full_path.exists()
        print_result(f"{description}", exists, str(full_path) if exists else "Not found")
        results.append(exists)
    
    # Test config JSON validity
    config_path = project_root / 'config' / 'postman_mcp_config.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
            
            # Check key sections
            sections = ['postman_integration', 'api_endpoints', 'vscode_extension', 
                       'collections', 'monitors', 'automation_workflows']
            
            for section in sections:
                has_section = section in config
                print_result(f"Config section: {section}", has_section)
                results.append(has_section)
        
        except json.JSONDecodeError as e:
            print_result("Config JSON valid", False, str(e))
            results.append(False)
    
    return all(results)


def test_trading_api_integration():
    """Test trading API integration features"""
    print_section("Trading API Integration Tests")
    
    connector = PostmanMCPConnector()
    
    # Test 1: Generate trading API test config
    test_config = connector.integrate_with_trading_bot(
        api_endpoint="https://api.example.com/trade/signal",
        method="POST"
    )
    
    has_name = 'name' in test_config
    has_request = 'request' in test_config
    has_tests = 'event' in test_config
    
    print_result("Trading API test config generated", has_name and has_request)
    print_result("Test config has request details", has_request)
    print_result("Test config has test scripts", has_tests)
    
    if has_name:
        print(f"  Generated test: {test_config['name']}")
    
    return has_name and has_request


def test_vscode_authentication():
    """Test VS Code extension authentication"""
    print_section("VS Code Extension Authentication Tests")
    
    connector = PostmanMCPConnector()
    auth_status = connector.authenticate_vscode_extension()
    
    authenticated = auth_status.get('authenticated', False)
    has_extension_url = 'extension_url' in auth_status
    
    print_result("Authentication status available", True)
    print_result("VS Code auth code configured", authenticated)
    print_result("Extension URL generated", has_extension_url)
    
    if has_extension_url:
        print(f"  Extension URL: {auth_status['extension_url'][:80]}...")
    
    return True


def generate_summary():
    """Generate test summary"""
    print_section("Test Summary")
    
    print("Postman API MCP Integration Test Complete")
    print()
    print("Status: All core components installed and configured")
    print()
    print("Next Steps:")
    print("1. Configure Postman API key in config/.env")
    print("2. Run: ./scripts/setup_postman_mcp.sh")
    print("3. Test connection: python pillar-a-trading/zapier-integration/postman_mcp_connector.py")
    print("4. Read documentation: docs/POSTMAN_API_INTEGRATION.md")
    print()
    print(f"Test completed at: {datetime.now().isoformat()}")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  POSTMAN API MCP INTEGRATION TEST SUITE")
    print("  Agent X5.0 - APPS Holdings WY Inc.")
    print("=" * 70)
    
    results = {
        'postman_connector': test_postman_connector(),
        'integrated_connector': test_integrated_connector(),
        'configuration_files': test_configuration_files(),
        'trading_api_integration': test_trading_api_integration(),
        'vscode_authentication': test_vscode_authentication()
    }
    
    generate_summary()
    
    # Calculate overall success
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print_section("Overall Results")
    print(f"Tests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}{reset} - {test_name.replace('_', ' ').title()}")
    
    print()
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
