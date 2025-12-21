#!/usr/bin/env python3
"""
API Manager CLI
Command-line interface for managing E2B, Zapier, GitHub, and Gemini APIs
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path

class APIManager:
    """Centralized API management for all integrations"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.config_dir = self.root_dir / 'config'
        self.load_env()

    def load_env(self):
        """Load environment variables"""
        env_file = self.config_dir / '.env'
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if line.strip() and not line.startswith('#') and '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

    # E2B Commands
    def e2b_create_sandbox(self, template='python3', timeout=300):
        """Create new E2B sandbox"""
        api_key = os.getenv('E2B_API_KEY')
        if not api_key:
            return {'error': 'E2B_API_KEY not set'}

        try:
            response = requests.post(
                'https://api.e2b.dev/sandboxes',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={'template': template, 'timeout': timeout},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def e2b_list_sandboxes(self):
        """List all E2B sandboxes"""
        api_key = os.getenv('E2B_API_KEY')
        if not api_key:
            return {'error': 'E2B_API_KEY not set'}

        try:
            response = requests.get(
                'https://api.e2b.dev/sandboxes',
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def e2b_execute_code(self, sandbox_id, code, language='python'):
        """Execute code in E2B sandbox"""
        api_key = os.getenv('E2B_API_KEY')
        if not api_key:
            return {'error': 'E2B_API_KEY not set'}

        try:
            response = requests.post(
                f'https://api.e2b.dev/sandboxes/{sandbox_id}/execute',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={'code': code, 'language': language},
                timeout=60
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    # Zapier Commands
    def zapier_trigger(self, event_type, data):
        """Trigger Zapier webhook"""
        webhook_url = os.getenv('ZAPIER_WEBHOOK_URL')
        if not webhook_url or 'YOUR_WEBHOOK_ID' in webhook_url:
            return {'error': 'ZAPIER_WEBHOOK_URL not configured'}

        payload = {
            'event': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'Private-Claude'
        }

        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            return {'status': response.status_code, 'response': response.text}
        except Exception as e:
            return {'error': str(e)}

    # GitHub Commands
    def github_create_issue(self, title, body):
        """Create GitHub issue"""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            return {'error': 'GITHUB_TOKEN not set'}

        try:
            response = requests.post(
                'https://api.github.com/repos/appsefilepro-cell/Private-Claude/issues',
                headers={
                    'Authorization': f'Bearer {token}',
                    'Content-Type': 'application/json'
                },
                json={'title': title, 'body': body},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    def github_list_branches(self):
        """List GitHub branches"""
        token = os.getenv('GITHUB_TOKEN')
        if not token:
            return {'error': 'GITHUB_TOKEN not set'}

        try:
            response = requests.get(
                'https://api.github.com/repos/appsefilepro-cell/Private-Claude/branches',
                headers={'Authorization': f'Bearer {token}'},
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    # Gemini Commands
    def gemini_generate(self, prompt):
        """Generate content with Gemini"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key or api_key == 'your_gemini_api_key_here':
            return {'error': 'GEMINI_API_KEY not configured'}

        try:
            url = f'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={api_key}'
            response = requests.post(
                url,
                json={
                    'contents': [{
                        'parts': [{'text': prompt}]
                    }]
                },
                timeout=30
            )
            return response.json()
        except Exception as e:
            return {'error': str(e)}

    # Utility Commands
    def status_all(self):
        """Check status of all APIs"""
        results = {
            'e2b': 'configured' if os.getenv('E2B_API_KEY') else 'not configured',
            'zapier': 'configured' if os.getenv('ZAPIER_WEBHOOK_URL') and 'YOUR_WEBHOOK_ID' not in os.getenv('ZAPIER_WEBHOOK_URL', '') else 'not configured',
            'github': 'configured' if os.getenv('GITHUB_TOKEN') else 'not configured',
            'gemini': 'configured' if os.getenv('GEMINI_API_KEY') and os.getenv('GEMINI_API_KEY') != 'your_gemini_api_key_here' else 'not configured'
        }
        return results


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='API Manager for Private-Claude')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # E2B commands
    e2b_parser = subparsers.add_parser('e2b', help='E2B commands')
    e2b_subparsers = e2b_parser.add_subparsers(dest='e2b_command')

    e2b_create = e2b_subparsers.add_parser('create', help='Create sandbox')
    e2b_create.add_argument('--template', default='python3', help='Sandbox template')

    e2b_subparsers.add_parser('list', help='List sandboxes')

    e2b_exec = e2b_subparsers.add_parser('exec', help='Execute code')
    e2b_exec.add_argument('sandbox_id', help='Sandbox ID')
    e2b_exec.add_argument('code', help='Code to execute')

    # Zapier commands
    zapier_parser = subparsers.add_parser('zapier', help='Zapier commands')
    zapier_parser.add_argument('event', help='Event type')
    zapier_parser.add_argument('--data', default='{}', help='JSON data')

    # GitHub commands
    github_parser = subparsers.add_parser('github', help='GitHub commands')
    github_subparsers = github_parser.add_subparsers(dest='github_command')

    github_issue = github_subparsers.add_parser('issue', help='Create issue')
    github_issue.add_argument('title', help='Issue title')
    github_issue.add_argument('body', help='Issue body')

    github_subparsers.add_parser('branches', help='List branches')

    # Gemini commands
    gemini_parser = subparsers.add_parser('gemini', help='Gemini commands')
    gemini_parser.add_argument('prompt', help='Prompt for Gemini')

    # Status command
    subparsers.add_parser('status', help='Check API status')

    args = parser.parse_args()

    manager = APIManager()

    # Execute commands
    result = None

    if args.command == 'e2b':
        if args.e2b_command == 'create':
            result = manager.e2b_create_sandbox(template=args.template)
        elif args.e2b_command == 'list':
            result = manager.e2b_list_sandboxes()
        elif args.e2b_command == 'exec':
            result = manager.e2b_execute_code(args.sandbox_id, args.code)

    elif args.command == 'zapier':
        data = json.loads(args.data)
        result = manager.zapier_trigger(args.event, data)

    elif args.command == 'github':
        if args.github_command == 'issue':
            result = manager.github_create_issue(args.title, args.body)
        elif args.github_command == 'branches':
            result = manager.github_list_branches()

    elif args.command == 'gemini':
        result = manager.gemini_generate(args.prompt)

    elif args.command == 'status':
        result = manager.status_all()

    else:
        parser.print_help()
        return

    # Print result
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
