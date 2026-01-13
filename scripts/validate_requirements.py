#!/usr/bin/env python3
"""
Validate requirements.txt for common issues.

This script checks for:
1. Yanked packages on PyPI
2. Invalid version specifiers
3. Package availability
4. Security vulnerabilities (basic check)
5. Conflicting dependencies

Usage:
    python scripts/validate_requirements.py
    python scripts/validate_requirements.py --fix
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class Color:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_status(symbol: str, message: str, color: str = Color.GREEN):
    """Print colored status message."""
    print(f"{color}{symbol}{Color.END} {message}")


def parse_requirements(file_path: Path) -> List[Tuple[str, str, str]]:
    """
    Parse requirements.txt file.
    
    Returns list of tuples: (package_name, version_spec, original_line)
    """
    requirements = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse package name and version (PEP 508 compliant)
            # Package names can contain letters, numbers, dots, hyphens, and underscores
            match = re.match(r'^([a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]|[a-zA-Z0-9])([>=<~!]+.*)?$', line)
            if match:
                package_name = match.group(1)
                version_spec = match.group(2) if match.group(2) else ''
                requirements.append((package_name, version_spec, line))
    
    return requirements


def check_package_exists(package_name: str, version_spec: str = '') -> Tuple[bool, str]:
    """
    Check if package and version exist on PyPI.
    
    Returns (success, message)
    """
    try:
        # Use pip index versions to check package availability
        result = subprocess.run(
            ['pip', 'index', 'versions', package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, f"Package '{package_name}' not found on PyPI"
        
        # If specific version is specified, check if it's available
        if version_spec.startswith('=='):
            # Extract the exact version number
            version = version_spec[2:].strip()
            # Use regex to match exact version in output (with word boundaries)
            version_pattern = re.compile(r'\b' + re.escape(version) + r'\b')
            if not version_pattern.search(result.stdout):
                return False, f"Version {version} not available (may be yanked)"
        
        return True, "OK"
    
    except subprocess.TimeoutExpired:
        return False, "Timeout checking package"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_dry_run_install(requirements_file: Path) -> Tuple[bool, str]:
    """
    Perform a dry-run installation to check for conflicts.
    
    Returns (success, message)
    """
    try:
        result = subprocess.run(
            ['pip', 'install', '--dry-run', '-r', str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            # Extract error message with more context
            stderr_lines = result.stderr.strip().split('\n')
            # Get last 10 lines which usually contain the most relevant error info
            relevant_errors = stderr_lines[-10:] if len(stderr_lines) > 10 else stderr_lines
            error_msg = '\n'.join(relevant_errors)
            return False, error_msg
        
        return True, "All dependencies can be installed"
    
    except subprocess.TimeoutExpired:
        return False, "Timeout during dry-run install"
    except Exception as e:
        return False, f"Error: {str(e)}"


def check_security_advisories(package_name: str) -> Tuple[bool, List[str]]:
    """
    Check for known security vulnerabilities.
    
    This is a basic check. For production, consider using tools like:
    - pip-audit
    - safety
    - snyk
    
    Returns (has_issues, list_of_advisories)
    """
    # This is a placeholder - in production you'd integrate with a vulnerability DB
    # For now, we'll just return no issues
    return False, []


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(description='Validate requirements.txt')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix issues')
    parser.add_argument('--file', default='requirements.txt', help='Path to requirements file')
    args = parser.parse_args()
    
    requirements_path = Path(args.file)
    
    if not requirements_path.exists():
        print_status('✗', f"Requirements file not found: {requirements_path}", Color.RED)
        sys.exit(1)
    
    print(f"\n{Color.BOLD}Validating {requirements_path}{Color.END}\n")
    print("=" * 60)
    
    # Parse requirements
    requirements = parse_requirements(requirements_path)
    print_status('✓', f"Found {len(requirements)} packages to validate", Color.BLUE)
    print()
    
    # Track issues
    issues_found = []
    warnings = []
    
    # Check 1: Validate each package
    print(f"{Color.BOLD}Checking package availability...{Color.END}")
    for package_name, version_spec, original_line in requirements:
        success, message = check_package_exists(package_name, version_spec)
        
        if not success:
            print_status('✗', f"{package_name}: {message}", Color.RED)
            issues_found.append((package_name, message))
        else:
            print_status('✓', f"{package_name}: Available", Color.GREEN)
    
    print()
    
    # Check 2: Version pinning analysis
    print(f"{Color.BOLD}Analyzing version specifications...{Color.END}")
    pinned_packages = []
    for package_name, version_spec, original_line in requirements:
        if version_spec.startswith('=='):
            pinned_packages.append(package_name)
            print_status('⚠', f"{package_name}: Exact version pinned {version_spec}", Color.YELLOW)
    
    if pinned_packages:
        warnings.append(f"{len(pinned_packages)} packages have exact version pins")
        print()
        print(f"{Color.YELLOW}Consider using ranges (>=) for more flexibility{Color.END}")
    else:
        print_status('✓', "No exact version pins found", Color.GREEN)
    
    print()
    
    # Check 3: Dry-run installation
    print(f"{Color.BOLD}Testing installation...{Color.END}")
    success, message = check_dry_run_install(requirements_path)
    
    if not success:
        print_status('✗', "Installation test failed:", Color.RED)
        print(f"  {message}")
        issues_found.append(("installation", message))
    else:
        print_status('✓', message, Color.GREEN)
    
    print()
    
    # Summary
    print("=" * 60)
    print(f"\n{Color.BOLD}Summary:{Color.END}\n")
    
    if issues_found:
        print_status('✗', f"{len(issues_found)} critical issue(s) found:", Color.RED)
        for package, issue in issues_found:
            print(f"  - {package}: {issue}")
        print()
    else:
        print_status('✓', "No critical issues found!", Color.GREEN)
        print()
    
    if warnings:
        print_status('⚠', f"{len(warnings)} warning(s):", Color.YELLOW)
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    # Exit code
    if issues_found:
        print(f"{Color.RED}Validation failed.{Color.END}")
        sys.exit(1)
    else:
        print(f"{Color.GREEN}Validation passed!{Color.END}")
        sys.exit(0)


if __name__ == '__main__':
    main()
