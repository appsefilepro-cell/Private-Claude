#!/usr/bin/env python3
"""
System Remediation Engine
Comprehensive codebase scanner for errors, configuration issues, and auto-fixes
"""

import os
import sys
import json
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SystemRemediationEngine:
    """Main remediation engine for scanning and fixing system issues"""

    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.issues = []
        self.fixes_applied = []
        self.scan_results = {
            'timestamp': datetime.now().isoformat(),
            'base_path': self.base_path,
            'issues_found': [],
            'fixes_applied': [],
            'summary': {}
        }

    def scan_all(self) -> Dict[str, Any]:
        """Run all scans and return comprehensive results"""
        logger.info(f"Starting comprehensive system scan at {self.base_path}")

        # Run all scanning operations
        self.scan_python_syntax()
        self.scan_imports()
        self.scan_configurations()
        self.scan_dependencies()
        self.scan_environment_variables()
        self.scan_api_integrations()
        self.scan_missing_files()
        self.scan_permissions()
        self.scan_git_issues()

        # Generate summary
        self.generate_summary()

        # Auto-fix common issues
        self.auto_fix_issues()

        return self.scan_results

    def scan_python_syntax(self) -> None:
        """Scan all Python files for syntax errors"""
        logger.info("Scanning Python files for syntax errors...")
        python_files = list(Path(self.base_path).rglob('*.py'))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    ast.parse(source)
            except SyntaxError as e:
                issue = {
                    'type': 'SYNTAX_ERROR',
                    'severity': 'CRITICAL',
                    'file': str(py_file),
                    'line': e.lineno,
                    'message': str(e),
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)
                logger.error(f"Syntax error in {py_file}: {e}")
            except Exception as e:
                logger.warning(f"Could not parse {py_file}: {e}")

    def scan_imports(self) -> None:
        """Scan for missing imports and dependencies"""
        logger.info("Scanning for import issues...")
        python_files = list(Path(self.base_path).rglob('*.py'))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                    tree = ast.parse(source)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._check_import(alias.name, py_file)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._check_import(node.module, py_file)
            except Exception as e:
                logger.debug(f"Could not analyze imports in {py_file}: {e}")

    def _check_import(self, module_name: str, file_path: Path) -> None:
        """Check if a module can be imported"""
        # Skip standard library and relative imports
        if module_name.startswith('.'):
            return

        # Get base module name
        base_module = module_name.split('.')[0]

        # Skip known standard library modules
        stdlib_modules = {
            'os', 'sys', 'json', 're', 'ast', 'subprocess', 'pathlib',
            'typing', 'datetime', 'logging', 'asyncio', 'collections',
            'itertools', 'functools', 'time', 'math', 'random', 'hashlib',
            'urllib', 'http', 'email', 'base64', 'csv', 'io', 'pickle',
            'sqlite3', 'socket', 'threading', 'multiprocessing', 'queue',
            'unittest', 'doctest', 'pprint', 'copy', 'shutil', 'glob',
            'tempfile', 'warnings', 'traceback', 'inspect', 'contextlib'
        }

        if base_module in stdlib_modules:
            return

        # Try to import the module
        try:
            __import__(base_module)
        except ImportError:
            issue = {
                'type': 'MISSING_DEPENDENCY',
                'severity': 'WARNING',
                'file': str(file_path),
                'module': module_name,
                'message': f"Module '{module_name}' not installed",
                'auto_fixable': True,
                'fix_command': f"pip install {base_module}"
            }
            # Avoid duplicates
            if not any(i.get('module') == module_name and i.get('type') == 'MISSING_DEPENDENCY'
                      for i in self.issues):
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)
                logger.warning(f"Missing dependency: {module_name} (used in {file_path})")

    def scan_configurations(self) -> None:
        """Scan configuration files for completeness"""
        logger.info("Scanning configuration files...")

        config_dir = Path(self.base_path) / 'config'
        if not config_dir.exists():
            issue = {
                'type': 'MISSING_DIRECTORY',
                'severity': 'WARNING',
                'path': str(config_dir),
                'message': 'Config directory does not exist',
                'auto_fixable': True
            }
            self.issues.append(issue)
            self.scan_results['issues_found'].append(issue)
            return

        # Check for essential config files
        essential_configs = [
            '.env.example',
            'agent_5_config.json',
        ]

        for config_file in essential_configs:
            config_path = config_dir / config_file
            if not config_path.exists():
                issue = {
                    'type': 'MISSING_CONFIG',
                    'severity': 'WARNING',
                    'file': config_file,
                    'path': str(config_path),
                    'message': f'Missing essential config file: {config_file}',
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

        # Validate JSON config files
        for json_file in config_dir.glob('*.json'):
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                issue = {
                    'type': 'INVALID_JSON',
                    'severity': 'CRITICAL',
                    'file': str(json_file),
                    'message': f'Invalid JSON: {e}',
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

    def scan_dependencies(self) -> None:
        """Check if all dependencies from requirements.txt are installed"""
        logger.info("Checking installed dependencies...")

        requirements_file = Path(self.base_path) / 'requirements.txt'
        if not requirements_file.exists():
            issue = {
                'type': 'MISSING_FILE',
                'severity': 'WARNING',
                'file': 'requirements.txt',
                'message': 'requirements.txt not found',
                'auto_fixable': False
            }
            self.issues.append(issue)
            self.scan_results['issues_found'].append(issue)
            return

        try:
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name (before ==, >=, etc.)
                        package = re.split(r'[>=<]', line)[0].strip()

                        try:
                            __import__(package.replace('-', '_'))
                        except ImportError:
                            issue = {
                                'type': 'UNINSTALLED_REQUIREMENT',
                                'severity': 'WARNING',
                                'package': package,
                                'message': f'Required package not installed: {package}',
                                'auto_fixable': True,
                                'fix_command': f'pip install {line}'
                            }
                            self.issues.append(issue)
                            self.scan_results['issues_found'].append(issue)
        except Exception as e:
            logger.error(f"Error reading requirements.txt: {e}")

    def scan_environment_variables(self) -> None:
        """Check for required environment variables"""
        logger.info("Checking environment variables...")

        env_file = Path(self.base_path) / 'config' / '.env'
        env_example = Path(self.base_path) / 'config' / '.env.example'

        if not env_example.exists():
            logger.warning("No .env.example file found to validate against")
            return

        if not env_file.exists():
            issue = {
                'type': 'MISSING_ENV',
                'severity': 'CRITICAL',
                'message': '.env file does not exist',
                'auto_fixable': True,
                'fix_action': 'copy_env_example'
            }
            self.issues.append(issue)
            self.scan_results['issues_found'].append(issue)
            return

        # Parse .env.example for required variables
        try:
            with open(env_example, 'r') as f:
                example_vars = set()
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        var_name = line.split('=')[0].strip()
                        example_vars.add(var_name)

            # Check actual .env file
            with open(env_file, 'r') as f:
                actual_vars = set()
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        var_name = line.split('=')[0].strip()
                        actual_vars.add(var_name)

            # Find missing variables
            missing_vars = example_vars - actual_vars
            for var in missing_vars:
                issue = {
                    'type': 'MISSING_ENV_VAR',
                    'severity': 'WARNING',
                    'variable': var,
                    'message': f'Missing environment variable: {var}',
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

        except Exception as e:
            logger.error(f"Error checking environment variables: {e}")

    def scan_api_integrations(self) -> None:
        """Scan for API integration issues"""
        logger.info("Checking API integrations...")

        integration_dir = Path(self.base_path) / 'config' / 'integrations'
        if not integration_dir.exists():
            issue = {
                'type': 'MISSING_DIRECTORY',
                'severity': 'INFO',
                'path': str(integration_dir),
                'message': 'Integrations directory does not exist',
                'auto_fixable': True
            }
            self.issues.append(issue)
            self.scan_results['issues_found'].append(issue)
            return

        # Check integration config files
        for integration_file in integration_dir.glob('*.json'):
            try:
                with open(integration_file, 'r') as f:
                    config = json.load(f)

                # Check for required fields
                if 'enabled' not in config:
                    issue = {
                        'type': 'INCOMPLETE_CONFIG',
                        'severity': 'WARNING',
                        'file': str(integration_file),
                        'message': f'Integration config missing "enabled" field',
                        'auto_fixable': True
                    }
                    self.issues.append(issue)
                    self.scan_results['issues_found'].append(issue)

            except json.JSONDecodeError as e:
                issue = {
                    'type': 'INVALID_JSON',
                    'severity': 'CRITICAL',
                    'file': str(integration_file),
                    'message': f'Invalid JSON in integration config: {e}',
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

    def scan_missing_files(self) -> None:
        """Check for missing essential files and directories"""
        logger.info("Checking for missing essential files...")

        essential_dirs = [
            'scripts',
            'config',
            'docs',
            'tests',
            'logs'
        ]

        for dir_name in essential_dirs:
            dir_path = Path(self.base_path) / dir_name
            if not dir_path.exists():
                issue = {
                    'type': 'MISSING_DIRECTORY',
                    'severity': 'WARNING',
                    'directory': dir_name,
                    'path': str(dir_path),
                    'message': f'Essential directory missing: {dir_name}',
                    'auto_fixable': True
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

    def scan_permissions(self) -> None:
        """Check file permissions for scripts"""
        logger.info("Checking file permissions...")

        scripts_dir = Path(self.base_path) / 'scripts'
        if not scripts_dir.exists():
            return

        for script_file in scripts_dir.glob('*.py'):
            # Check if file is executable
            if not os.access(script_file, os.X_OK):
                issue = {
                    'type': 'PERMISSION_ISSUE',
                    'severity': 'INFO',
                    'file': str(script_file),
                    'message': f'Script not executable: {script_file.name}',
                    'auto_fixable': True,
                    'fix_command': f'chmod +x {script_file}'
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

    def scan_git_issues(self) -> None:
        """Check for git-related issues"""
        logger.info("Checking git status...")

        git_dir = Path(self.base_path) / '.git'
        if not git_dir.exists():
            issue = {
                'type': 'NOT_GIT_REPO',
                'severity': 'INFO',
                'message': 'Not a git repository',
                'auto_fixable': False
            }
            self.issues.append(issue)
            self.scan_results['issues_found'].append(issue)
            return

        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.stdout.strip():
                issue = {
                    'type': 'UNCOMMITTED_CHANGES',
                    'severity': 'INFO',
                    'message': 'Repository has uncommitted changes',
                    'auto_fixable': False
                }
                self.issues.append(issue)
                self.scan_results['issues_found'].append(issue)

        except Exception as e:
            logger.debug(f"Could not check git status: {e}")

    def generate_summary(self) -> None:
        """Generate summary statistics"""
        logger.info("Generating summary...")

        severity_counts = {
            'CRITICAL': 0,
            'WARNING': 0,
            'INFO': 0
        }

        type_counts = {}
        auto_fixable_count = 0

        for issue in self.issues:
            severity = issue.get('severity', 'INFO')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            issue_type = issue.get('type', 'UNKNOWN')
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

            if issue.get('auto_fixable', False):
                auto_fixable_count += 1

        self.scan_results['summary'] = {
            'total_issues': len(self.issues),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'auto_fixable': auto_fixable_count,
            'requires_manual_fix': len(self.issues) - auto_fixable_count
        }

    def auto_fix_issues(self) -> None:
        """Automatically fix issues where possible"""
        logger.info("Attempting to auto-fix issues...")

        for issue in self.issues:
            if not issue.get('auto_fixable', False):
                continue

            try:
                if issue['type'] == 'MISSING_DIRECTORY':
                    self._fix_missing_directory(issue)
                elif issue['type'] == 'MISSING_ENV':
                    self._fix_missing_env(issue)
                elif issue['type'] == 'PERMISSION_ISSUE':
                    self._fix_permissions(issue)
                elif issue['type'] == 'INCOMPLETE_CONFIG':
                    self._fix_incomplete_config(issue)

            except Exception as e:
                logger.error(f"Failed to auto-fix {issue['type']}: {e}")

    def _fix_missing_directory(self, issue: Dict) -> None:
        """Create missing directory"""
        dir_path = Path(issue['path'])
        dir_path.mkdir(parents=True, exist_ok=True)

        fix_record = {
            'issue_type': issue['type'],
            'action': 'created_directory',
            'path': str(dir_path),
            'timestamp': datetime.now().isoformat()
        }
        self.fixes_applied.append(fix_record)
        self.scan_results['fixes_applied'].append(fix_record)
        logger.info(f"Created directory: {dir_path}")

    def _fix_missing_env(self, issue: Dict) -> None:
        """Copy .env.example to .env"""
        env_example = Path(self.base_path) / 'config' / '.env.example'
        env_file = Path(self.base_path) / 'config' / '.env'

        if env_example.exists():
            with open(env_example, 'r') as src:
                with open(env_file, 'w') as dst:
                    dst.write(src.read())

            fix_record = {
                'issue_type': issue['type'],
                'action': 'created_env_file',
                'source': str(env_example),
                'destination': str(env_file),
                'timestamp': datetime.now().isoformat()
            }
            self.fixes_applied.append(fix_record)
            self.scan_results['fixes_applied'].append(fix_record)
            logger.info("Created .env file from .env.example")

    def _fix_permissions(self, issue: Dict) -> None:
        """Fix file permissions"""
        file_path = Path(issue['file'])
        os.chmod(file_path, 0o755)

        fix_record = {
            'issue_type': issue['type'],
            'action': 'fixed_permissions',
            'file': str(file_path),
            'timestamp': datetime.now().isoformat()
        }
        self.fixes_applied.append(fix_record)
        self.scan_results['fixes_applied'].append(fix_record)
        logger.info(f"Fixed permissions for: {file_path}")

    def _fix_incomplete_config(self, issue: Dict) -> None:
        """Fix incomplete configuration"""
        config_file = Path(issue['file'])

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Add missing 'enabled' field
            if 'enabled' not in config:
                config['enabled'] = False

            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)

            fix_record = {
                'issue_type': issue['type'],
                'action': 'updated_config',
                'file': str(config_file),
                'timestamp': datetime.now().isoformat()
            }
            self.fixes_applied.append(fix_record)
            self.scan_results['fixes_applied'].append(fix_record)
            logger.info(f"Fixed incomplete config: {config_file}")

        except Exception as e:
            logger.error(f"Could not fix config {config_file}: {e}")

    def save_results(self, output_file: str = None) -> str:
        """Save scan results to JSON file"""
        if output_file is None:
            output_file = Path(self.base_path) / 'logs' / f'remediation_scan_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.scan_results, f, indent=2)

        logger.info(f"Scan results saved to: {output_path}")
        return str(output_path)

    def print_report(self) -> None:
        """Print formatted report to console"""
        print("\n" + "="*80)
        print("SYSTEM REMEDIATION SCAN REPORT")
        print("="*80)
        print(f"\nScan Time: {self.scan_results['timestamp']}")
        print(f"Base Path: {self.scan_results['base_path']}")

        summary = self.scan_results['summary']
        print(f"\n{'SUMMARY':^80}")
        print("-"*80)
        print(f"Total Issues Found: {summary['total_issues']}")
        print(f"  - Critical: {summary['by_severity'].get('CRITICAL', 0)}")
        print(f"  - Warnings: {summary['by_severity'].get('WARNING', 0)}")
        print(f"  - Info: {summary['by_severity'].get('INFO', 0)}")
        print(f"\nAuto-Fixable: {summary['auto_fixable']}")
        print(f"Requires Manual Fix: {summary['requires_manual_fix']}")
        print(f"Fixes Applied: {len(self.fixes_applied)}")

        if summary['by_type']:
            print(f"\n{'ISSUES BY TYPE':^80}")
            print("-"*80)
            for issue_type, count in sorted(summary['by_type'].items()):
                print(f"  {issue_type}: {count}")

        if self.fixes_applied:
            print(f"\n{'FIXES APPLIED':^80}")
            print("-"*80)
            for fix in self.fixes_applied:
                print(f"  - {fix['action']}: {fix.get('path', fix.get('file', 'N/A'))}")

        # Print top critical issues
        critical_issues = [i for i in self.issues if i.get('severity') == 'CRITICAL']
        if critical_issues:
            print(f"\n{'CRITICAL ISSUES':^80}")
            print("-"*80)
            for issue in critical_issues[:10]:  # Show first 10
                print(f"  [{issue['type']}] {issue['message']}")
                if 'file' in issue:
                    print(f"    File: {issue['file']}")

        print("\n" + "="*80 + "\n")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='System Remediation Engine')
    parser.add_argument('--path', type=str, help='Base path to scan (default: current directory)')
    parser.add_argument('--output', type=str, help='Output file for results (default: logs/remediation_scan_*.json)')
    parser.add_argument('--no-autofix', action='store_true', help='Disable auto-fixing')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')

    args = parser.parse_args()

    # Create engine
    engine = SystemRemediationEngine(base_path=args.path)

    # Run scan
    results = engine.scan_all()

    # Disable auto-fix if requested
    if args.no_autofix:
        engine.fixes_applied = []
        engine.scan_results['fixes_applied'] = []

    # Save results
    output_file = engine.save_results(args.output)

    # Print report
    if not args.quiet:
        engine.print_report()

    # Exit with appropriate code
    critical_count = results['summary']['by_severity'].get('CRITICAL', 0)
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == '__main__':
    main()
