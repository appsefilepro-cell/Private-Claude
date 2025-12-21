#!/usr/bin/env python3
"""
Complete Integration Setup
Automates the setup of E2B, Zapier, GitHub, and Gemini API integrations
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class IntegrationManager:
    """Manages all API integrations and setups"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / 'config'
        self.load_environment()

    def load_environment(self):
        """Load environment variables from .env file"""
        env_file = self.config_dir / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

    def setup_e2b(self) -> Dict[str, Any]:
        """Setup E2B sandbox and webhooks"""
        print("🚀 Setting up E2B integration...")

        api_key = os.getenv('E2B_API_KEY')
        if not api_key:
            return {'status': 'error', 'message': 'E2B_API_KEY not found'}

        try:
            # Create sandbox
            response = requests.post(
                'https://api.e2b.dev/sandboxes',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={'template': 'python3', 'timeout': 300},
                timeout=30
            )

            if response.status_code == 201:
                sandbox_data = response.json()
                print(f"✅ E2B Sandbox created: {sandbox_data.get('id')}")
                return {'status': 'success', 'sandbox': sandbox_data}
            else:
                print(f"⚠️  E2B setup: {response.status_code}")
                return {'status': 'partial', 'message': 'Check API key'}

        except Exception as e:
            print(f"❌ E2B error: {e}")
            return {'status': 'error', 'message': str(e)}

    def setup_zapier(self) -> Dict[str, Any]:
        """Configure Zapier webhook"""
        print("⚡ Setting up Zapier integration...")

        webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')
        if not webhook_url or 'YOUR_WEBHOOK_ID' in webhook_url:
            print("⚠️  Zapier webhook URL not configured")
            return {'status': 'pending', 'message': 'Configure ZAPIER_WEBHOOK_URL'}

        try:
            # Test webhook
            test_data = {
                'event': 'test',
                'source': 'Private-Claude',
                'timestamp': '2025-12-21T00:00:00Z'
            }

            response = requests.post(webhook_url, json=test_data, timeout=10)

            if response.status_code == 200:
                print("✅ Zapier webhook configured")
                return {'status': 'success'}
            else:
                print(f"⚠️  Zapier response: {response.status_code}")
                return {'status': 'partial'}

        except Exception as e:
            print(f"❌ Zapier error: {e}")
            return {'status': 'error', 'message': str(e)}

    def setup_github(self) -> Dict[str, Any]:
        """Setup GitHub integration"""
        print("🐙 Setting up GitHub integration...")

        token = os.getenv('GITHUB_TOKEN')
        if not token:
            print("⚠️  GITHUB_TOKEN not found")
            return {'status': 'pending', 'message': 'Configure GITHUB_TOKEN'}

        try:
            # Test GitHub API
            response = requests.get(
                'https://api.github.com/repos/appsefilepro-cell/Private-Claude',
                headers={'Authorization': f'Bearer {token}'},
                timeout=10
            )

            if response.status_code == 200:
                print("✅ GitHub integration configured")
                return {'status': 'success', 'repo': response.json().get('full_name')}
            else:
                print(f"⚠️  GitHub response: {response.status_code}")
                return {'status': 'partial'}

        except Exception as e:
            print(f"❌ GitHub error: {e}")
            return {'status': 'error', 'message': str(e)}

    def setup_gemini(self) -> Dict[str, Any]:
        """Setup Google Gemini AI"""
        print("🤖 Setting up Gemini AI integration...")

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            print("⚠️  GEMINI_API_KEY not configured")
            return {'status': 'pending', 'message': 'Configure GEMINI_API_KEY'}

        try:
            # Test Gemini API
            url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
            response = requests.post(
                url,
                json={
                    'contents': [{
                        'parts': [{'text': 'Say "Hello"'}]
                    }]
                },
                timeout=15
            )

            if response.status_code == 200:
                print("✅ Gemini AI configured")
                return {'status': 'success'}
            else:
                print(f"⚠️  Gemini response: {response.status_code}")
                return {'status': 'partial'}

        except Exception as e:
            print(f"❌ Gemini error: {e}")
            return {'status': 'error', 'message': str(e)}

    def verify_all_configs(self) -> Dict[str, Any]:
        """Verify all configuration files exist"""
        print("📋 Verifying configuration files...")

        required_configs = [
            'e2b_webhook_config.json',
            'zapier_connector.json',
            'github_webhook_integration.json',
            'mcp_server_config.json',
            'postman_collection.json'
        ]

        results = {}
        for config_file in required_configs:
            path = self.config_dir / config_file
            exists = path.exists()
            results[config_file] = exists
            status = "✅" if exists else "❌"
            print(f"{status} {config_file}")

        all_exist = all(results.values())
        return {'status': 'success' if all_exist else 'partial', 'files': results}

    def run_complete_setup(self):
        """Run complete integration setup"""
        print("\n" + "="*60)
        print("🔧 PRIVATE-CLAUDE INTEGRATION SETUP")
        print("="*60 + "\n")

        results = {
            'configs': self.verify_all_configs(),
            'e2b': self.setup_e2b(),
            'zapier': self.setup_zapier(),
            'github': self.setup_github(),
            'gemini': self.setup_gemini()
        }

        print("\n" + "="*60)
        print("📊 SETUP SUMMARY")
        print("="*60)

        for service, result in results.items():
            status = result.get('status', 'unknown')
            icon = {'success': '✅', 'partial': '⚠️', 'pending': '⏳', 'error': '❌'}.get(status, '❓')
            print(f"{icon} {service.upper()}: {status}")

        print("\n" + "="*60)
        print("📝 NEXT STEPS")
        print("="*60)
        print("1. Configure missing API keys in config/.env")
        print("2. Set up Zapier webhook at https://zapier.com/app/zaps")
        print("3. Configure GitHub token for repository access")
        print("4. Run webhook handler: python3 scripts/e2b_webhook_handler.py")
        print("5. Test with Postman collection: config/postman_collection.json")
        print("\n✨ Setup complete!\n")

        return results


def main():
    """Main entry point"""
    manager = IntegrationManager()
    results = manager.run_complete_setup()

    # Save results
    results_file = manager.config_dir / 'setup_results.json'
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"📄 Results saved to: {results_file}")


if __name__ == '__main__':
    main()
