#!/usr/bin/env python3
"""
Webhook Configuration Validator and Replacer
Scans for placeholder webhooks and helps configure real ones
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WebhookValidator:
    """Validator and replacer for webhook configurations"""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.placeholder_patterns = [
            r'xxxxx',
            r'XXXXX',
            r'XXXXXX',
            r'placeholder',
            r'PLACEHOLDER',
            r'hooks\.zapier\.com/hooks/catch/[Xx]+',
            r'example\.com',
        ]
        self.found_placeholders = []

    def scan_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan a single file for webhook placeholders"""
        placeholders = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.placeholder_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        placeholders.append({
                            'file': str(file_path.relative_to(self.base_path)),
                            'line': line_num,
                            'content': line.strip()[:100],
                            'pattern': pattern
                        })
                        break  # Only report once per line

        except Exception as e:
            logger.warning(f"Could not scan {file_path}: {e}")

        return placeholders

    def scan_all_configs(self) -> Dict[str, List]:
        """Scan all configuration files for placeholders"""
        logger.info("Scanning for webhook placeholders...")

        # File patterns to scan
        patterns = [
            '**/*.json',
            '**/*.yaml',
            '**/*.yml',
            '**/.env.example',
            '**/.env.template',
            '**/config/**',
        ]

        # Exclude patterns
        exclude_patterns = [
            '.git',
            '__pycache__',
            'node_modules',
            '.pytest_cache',
        ]

        scanned_files = set()
        all_placeholders = []

        # Scan JSON files
        for pattern in ['**/*.json', '**/*.yaml', '**/*.yml', '**/.env*']:
            for file_path in self.base_path.rglob(pattern.split('/')[-1] if '/' in pattern else pattern):
                # Skip excluded directories
                if any(exc in str(file_path) for exc in exclude_patterns):
                    continue

                # Skip if already scanned
                if file_path in scanned_files:
                    continue

                scanned_files.add(file_path)
                placeholders = self.scan_file(file_path)
                all_placeholders.extend(placeholders)

        self.found_placeholders = all_placeholders

        return {
            'total_files_scanned': len(scanned_files),
            'files_with_placeholders': len(set(p['file'] for p in all_placeholders)),
            'total_placeholders': len(all_placeholders),
            'placeholders': all_placeholders
        }

    def extract_webhook_urls(self, text: str) -> List[str]:
        """Extract potential webhook URLs from text"""
        url_pattern = r'https?://[^\s<>"\']+/hooks?/[^\s<>"\']+'
        return re.findall(url_pattern, text)

    def validate_webhook_url(self, url: str) -> bool:
        """Validate that a webhook URL is not a placeholder"""
        for pattern in self.placeholder_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        return True

    def generate_webhook_config_template(self) -> Dict[str, str]:
        """Generate template for webhook configuration"""
        return {
            'ZAPIER_TASK_WEBHOOK': 'https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_KEY/',
            'ZAPIER_REMINDER_WEBHOOK': 'https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_KEY/',
            'ZAPIER_DOCUMENT_WEBHOOK': 'https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_KEY/',
            'ZAPIER_ERROR_WEBHOOK': 'https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_KEY/',
            'ZAPIER_GENERAL_WEBHOOK': 'https://hooks.zapier.com/hooks/catch/YOUR_ID/YOUR_KEY/',
            'E2B_WEBHOOK_URL': 'https://your-e2b-endpoint.com/webhook',
            'GITHUB_WEBHOOK_URL': 'https://your-github-webhook.com/hook',
        }

    def create_env_template(self, output_path: Path = None) -> Path:
        """Create .env template with webhook placeholders"""
        if output_path is None:
            output_path = self.base_path / '.env.webhooks.template'

        template = self.generate_webhook_config_template()

        env_content = "# Webhook Configuration Template\n"
        env_content += f"# Generated: {datetime.now().isoformat()}\n\n"
        env_content += "# Zapier Webhooks\n"

        for key, value in template.items():
            env_content += f"{key}={value}\n"

        env_content += "\n# Instructions:\n"
        env_content += "# 1. Copy this file to .env\n"
        env_content += "# 2. Replace all placeholder URLs with your actual webhook URLs\n"
        env_content += "# 3. Get Zapier webhook URLs from: https://zapier.com/app/zaps\n"
        env_content += "# 4. Get E2B webhook URLs from: https://e2b.dev\n"

        output_path.write_text(env_content)
        logger.info(f"Created webhook template: {output_path}")

        return output_path

    def replace_placeholders_interactive(self):
        """Interactive mode to replace placeholders"""
        if not self.found_placeholders:
            logger.info("No placeholders found. Run scan_all_configs() first.")
            return

        # Group by file
        files_with_placeholders = {}
        for p in self.found_placeholders:
            file = p['file']
            if file not in files_with_placeholders:
                files_with_placeholders[file] = []
            files_with_placeholders[file].append(p)

        logger.info("\n" + "="*70)
        logger.info("WEBHOOK PLACEHOLDER REPLACEMENT")
        logger.info("="*70 + "\n")

        logger.info(f"Found placeholders in {len(files_with_placeholders)} files:\n")

        for file, placeholders in files_with_placeholders.items():
            logger.info(f"\n📄 {file}")
            logger.info(f"   {len(placeholders)} placeholder(s) found")

            for p in placeholders[:3]:  # Show first 3
                logger.info(f"   Line {p['line']}: {p['content'][:80]}...")

        logger.info("\n" + "="*70)
        logger.info("RECOMMENDATIONS:")
        logger.info("="*70)
        logger.info("1. Create actual webhook URLs in Zapier/E2B/GitHub")
        logger.info("2. Store them in .env file (use .env.webhooks.template)")
        logger.info("3. Update configuration files to read from environment variables")
        logger.info("4. Never commit real webhook URLs to git")
        logger.info("\nExample .env entry:")
        logger.info("ZAPIER_TASK_WEBHOOK=https://hooks.zapier.com/hooks/catch/12345/abcdef/")

    def generate_report(self) -> Path:
        """Generate detailed webhook validation report"""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'scan_results': self.scan_all_configs(),
            'recommendations': [
                'Replace all placeholder URLs with actual webhook endpoints',
                'Use environment variables for sensitive webhook URLs',
                'Test all webhooks before production deployment',
                'Implement webhook signature verification for security',
                'Monitor webhook delivery success rates',
            ]
        }

        report_path = self.base_path / 'logs' / f"webhook_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"\n📊 Webhook validation report: {report_path}")

        return report_path

    def suggest_webhook_setup(self):
        """Suggest webhook setup steps"""
        logger.info("\n" + "="*70)
        logger.info("WEBHOOK SETUP GUIDE")
        logger.info("="*70 + "\n")

        logger.info("🔧 ZAPIER WEBHOOKS:")
        logger.info("   1. Go to https://zapier.com/app/zaps")
        logger.info("   2. Create a new Zap")
        logger.info("   3. Choose 'Webhooks by Zapier' as trigger")
        logger.info("   4. Select 'Catch Hook'")
        logger.info("   5. Copy the webhook URL provided")
        logger.info("   6. Paste into your .env file\n")

        logger.info("🔧 E2B WEBHOOKS:")
        logger.info("   1. Go to https://e2b.dev/docs")
        logger.info("   2. Create sandbox with webhook support")
        logger.info("   3. Configure webhook endpoint")
        logger.info("   4. Add to E2B configuration\n")

        logger.info("🔧 GITHUB WEBHOOKS:")
        logger.info("   1. Go to repository Settings > Webhooks")
        logger.info("   2. Click 'Add webhook'")
        logger.info("   3. Set Payload URL to your endpoint")
        logger.info("   4. Choose events to trigger webhook")
        logger.info("   5. Add secret for security\n")

        logger.info("="*70)


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("WEBHOOK CONFIGURATION VALIDATOR")
    print("="*70 + "\n")

    validator = WebhookValidator()

    # Scan for placeholders
    results = validator.scan_all_configs()

    print(f"Scanned {results['total_files_scanned']} files")
    print(f"Found {results['total_placeholders']} placeholder(s) in {results['files_with_placeholders']} file(s)\n")

    if results['total_placeholders'] > 0:
        validator.replace_placeholders_interactive()

        # Create template
        template_path = validator.create_env_template()
        print(f"\n✅ Created webhook template: {template_path}")

        # Show setup guide
        validator.suggest_webhook_setup()

        # Generate report
        validator.generate_report()
    else:
        print("✅ No webhook placeholders found!")
        print("All webhooks appear to be configured.\n")


if __name__ == '__main__':
    main()
