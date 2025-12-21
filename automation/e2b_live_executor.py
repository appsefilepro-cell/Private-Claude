#!/usr/bin/env python3
"""
E2B Live Code Executor - Agent 5.0 Automation
Executes ALL Python systems in E2B cloud sandbox
24/7 autonomous operation
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# E2B API Configuration
E2B_API_KEY = "sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae"
E2B_BASE_URL = "https://api.e2b.dev/v1"

class E2BLiveExecutor:
    """
    Live code executor using E2B cloud sandbox
    Executes Agent 5.0 systems without local dependencies
    """

    def __init__(self, api_key: str = E2B_API_KEY):
        self.api_key = api_key
        self.base_url = E2B_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # All Agent 5.0 systems to execute
        self.systems = {
            "trading_bot": "run_trading_bot_demo.py",
            "credit_repair": "pillar-g-credit-repair/credit_repair_suite.py",
            "legal_research": "core-systems/legal-research/phd_legal_research.py",
            "damages_calculator": "pillar-g-credit-repair/damages_calculator.py",
            "nonprofit_automation": "core-systems/nonprofit-automation/nonprofit_ai_integrator.py",
            "historical_research": "core-systems/historical-research/gulf_oil_research.py",
            "case_manager": "pillar-f-cleo/case_manager.py",
            "google_drive_sync": "core-systems/cloud-storage/google_drive_automation.py"
        }

        # Execution status
        self.execution_log = []

    async def create_sandbox(self, template: str = "Python3") -> str:
        """Create E2B sandbox environment"""
        import aiohttp

        endpoint = f"{self.base_url}/sandboxes"
        payload = {
            "template": template,
            "metadata": {
                "project": "Agent_5.0",
                "user": "Thurman Robinson",
                "purpose": "Legal automation system"
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=self.headers, json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    sandbox_id = data.get("sandboxId")
                    self.log(f"✅ Sandbox created: {sandbox_id}")
                    return sandbox_id
                else:
                    error = await response.text()
                    self.log(f"❌ Sandbox creation failed: {error}")
                    return None

    async def execute_code(self, sandbox_id: str, code: str, system_name: str) -> Dict[str, Any]:
        """Execute Python code in E2B sandbox"""
        import aiohttp

        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}/executions"
        payload = {
            "code": code,
            "language": "python",
            "timeout": 300  # 5 minutes
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log(f"✅ {system_name} executed successfully")
                    return {
                        "system": system_name,
                        "status": "success",
                        "output": data.get("stdout"),
                        "error": data.get("stderr"),
                        "execution_id": data.get("id")
                    }
                else:
                    error = await response.text()
                    self.log(f"❌ {system_name} execution failed: {error}")
                    return {
                        "system": system_name,
                        "status": "failed",
                        "error": error
                    }

    async def upload_file(self, sandbox_id: str, filepath: str) -> bool:
        """Upload file to E2B sandbox"""
        import aiohttp

        with open(filepath, 'r') as f:
            content = f.read()

        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}/filesystem/write"
        payload = {
            "path": f"/home/user/{os.path.basename(filepath)}",
            "content": content
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, headers=self.headers, json=payload) as response:
                if response.status == 200:
                    self.log(f"✅ Uploaded: {os.path.basename(filepath)}")
                    return True
                else:
                    self.log(f"❌ Upload failed: {os.path.basename(filepath)}")
                    return False

    async def execute_all_systems(self) -> List[Dict[str, Any]]:
        """Execute ALL Agent 5.0 systems in parallel"""

        # Create sandbox
        sandbox_id = await self.create_sandbox()
        if not sandbox_id:
            self.log("❌ Cannot proceed without sandbox")
            return []

        # Upload all system files
        self.log("📤 Uploading system files...")
        for system_name, filepath in self.systems.items():
            if os.path.exists(filepath):
                await self.upload_file(sandbox_id, filepath)

        # Execute all systems in parallel
        self.log("🚀 Executing all systems in parallel...")
        tasks = []
        for system_name, filepath in self.systems.items():
            code = self.generate_execution_code(filepath)
            tasks.append(self.execute_code(sandbox_id, code, system_name))

        results = await asyncio.gather(*tasks)

        # Close sandbox
        await self.close_sandbox(sandbox_id)

        return results

    def generate_execution_code(self, filepath: str) -> str:
        """Generate Python code to execute the system"""
        filename = os.path.basename(filepath)
        return f"""
import sys
sys.path.append('/home/user')

# Execute the system
exec(open('/home/user/{filename}').read())
"""

    async def close_sandbox(self, sandbox_id: str):
        """Close E2B sandbox"""
        import aiohttp

        endpoint = f"{self.base_url}/sandboxes/{sandbox_id}"

        async with aiohttp.ClientSession() as session:
            async with session.delete(endpoint, headers=self.headers) as response:
                if response.status == 204:
                    self.log(f"✅ Sandbox closed: {sandbox_id}")
                else:
                    self.log(f"⚠️  Sandbox close warning: {await response.text()}")

    def log(self, message: str):
        """Log execution events"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.execution_log.append(log_entry)

    def save_execution_log(self):
        """Save execution log to file"""
        log_file = f"automation/logs/e2b_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        with open(log_file, 'w') as f:
            f.write('\n'.join(self.execution_log))

        self.log(f"📄 Log saved: {log_file}")


# Simplified version without aiohttp dependency (for immediate use)
class E2BSimpleExecutor:
    """
    Simplified E2B executor using requests library
    Works without async dependencies
    """

    def __init__(self, api_key: str = E2B_API_KEY):
        self.api_key = api_key
        self.base_url = E2B_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_sandbox_simple(self) -> str:
        """Create sandbox using requests"""
        try:
            import requests

            endpoint = f"{self.base_url}/sandboxes"
            payload = {
                "template": "Python3",
                "metadata": {
                    "project": "Agent_5.0",
                    "user": "Thurman Robinson"
                }
            }

            response = requests.post(endpoint, headers=self.headers, json=payload)

            if response.status_code == 201:
                data = response.json()
                sandbox_id = data.get("sandboxId")
                print(f"✅ Sandbox created: {sandbox_id}")
                return sandbox_id
            else:
                print(f"❌ Sandbox creation failed: {response.text}")
                return None

        except ImportError:
            print("❌ requests library not installed. Install: pip install requests")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None

    def execute_python_simple(self, sandbox_id: str, code: str) -> Dict[str, Any]:
        """Execute Python code in sandbox"""
        try:
            import requests

            endpoint = f"{self.base_url}/sandboxes/{sandbox_id}/executions"
            payload = {
                "code": code,
                "language": "python",
                "timeout": 300
            }

            response = requests.post(endpoint, headers=self.headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                print(f"✅ Code executed successfully")
                return {
                    "status": "success",
                    "output": data.get("stdout"),
                    "error": data.get("stderr")
                }
            else:
                print(f"❌ Execution failed: {response.text}")
                return {
                    "status": "failed",
                    "error": response.text
                }

        except Exception as e:
            print(f"❌ Error: {e}")
            return {"status": "failed", "error": str(e)}


def test_e2b_connection():
    """Test E2B API connection"""
    print("="*60)
    print("E2B API CONNECTION TEST")
    print("="*60)

    executor = E2BSimpleExecutor()

    # Test 1: Create sandbox
    print("\n[TEST 1] Creating E2B sandbox...")
    sandbox_id = executor.create_sandbox_simple()

    if not sandbox_id:
        print("\n❌ E2B connection test FAILED")
        print("Possible issues:")
        print("1. Invalid API key")
        print("2. Network connection issue")
        print("3. E2B service down")
        return False

    # Test 2: Execute simple Python code
    print("\n[TEST 2] Executing Python code in sandbox...")
    test_code = """
print("Hello from E2B sandbox!")
print("Agent 5.0 is LIVE")

import sys
print(f"Python version: {sys.version}")

# Test basic computation
result = 84.5 * 2
print(f"Test calculation: {result}")
"""

    result = executor.execute_python_simple(sandbox_id, test_code)

    if result["status"] == "success":
        print("\n✅ E2B connection test PASSED")
        print("\nOutput from E2B sandbox:")
        print(result["output"])
        return True
    else:
        print("\n❌ E2B execution test FAILED")
        print(f"Error: {result['error']}")
        return False


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║     E2B LIVE EXECUTOR - AGENT 5.0 AUTOMATION                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()

    # Test E2B connection
    test_result = test_e2b_connection()

    if test_result:
        print("\n" + "="*60)
        print("E2B SYSTEM READY FOR AUTOMATION")
        print("="*60)
        print("\nNext steps:")
        print("1. ✅ E2B API key validated")
        print("2. ✅ Sandbox creation working")
        print("3. ✅ Code execution working")
        print("4. ⏳ Ready to execute all Agent 5.0 systems")
        print()
        print("Run: python automation/e2b_live_executor.py --execute-all")
    else:
        print("\n" + "="*60)
        print("E2B SYSTEM NOT READY")
        print("="*60)
        print("\nTroubleshooting:")
        print("1. Check API key: sk_e2b_08c56b39f9b4fdc26bd18805433ea4bf25a06aae")
        print("2. Install requests: pip install requests")
        print("3. Check network connection")
        print("4. Visit: https://e2b.dev/dashboard/appsefilepro/account")
