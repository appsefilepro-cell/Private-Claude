#!/usr/bin/env python3
"""
E2B Sandbox Environment Setup Script
Initializes and configures the E2B sandbox environment
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
import shutil


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def check_dependencies() -> bool:
    """Check required dependencies"""
    print_header("Checking Dependencies")

    packages = {
        "aiohttp": "aiohttp",
        "psutil": "psutil",
    }

    missing = []
    for name, package in packages.items():
        try:
            __import__(name)
            print(f"✓ {package} installed")
        except ImportError:
            print(f"✗ {package} NOT installed")
            missing.append(package)

    if missing:
        print(f"\nInstalling missing packages: {', '.join(missing)}")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"ERROR: Failed to install dependencies")
            print(result.stderr)
            return False
        print("✓ Dependencies installed")

    return True


def create_directories() -> bool:
    """Create required directories"""
    print_header("Creating Directories")

    directories = [
        "/home/user/Private-Claude/scripts",
        "/home/user/Private-Claude/config",
        "/home/user/Private-Claude/logs",
        "/tmp/e2b_uploads",
        "/tmp/e2b_downloads",
    ]

    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ {directory}")

    return True


def setup_environment() -> bool:
    """Setup environment variables"""
    print_header("Setting Up Environment")

    env_file = Path("/home/user/Private-Claude/config/.env")
    env_example = Path("/home/user/Private-Claude/config/.env.example")

    if env_file.exists():
        print("✓ .env file already exists")
        return True

    if env_example.exists():
        print("Creating .env from .env.example")
        shutil.copy(env_example, env_file)
        print("✓ .env created (configure API keys in this file)")

        # Check if API key is provided via environment
        api_key = os.getenv("E2B_API_KEY", "").strip()
        if api_key and api_key != "e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773":
            with open(env_file, 'r') as f:
                content = f.read()
            content = content.replace(
                "E2B_API_KEY=e2b_fcc08e8c733b3eab00bdb3ad5857f5966afc2773",
                f"E2B_API_KEY={api_key}"
            )
            with open(env_file, 'w') as f:
                f.write(content)
            print("✓ API key configured from environment")

        return True
    else:
        print("✗ .env.example not found")
        return False


def verify_configuration() -> bool:
    """Verify configuration files"""
    print_header("Verifying Configuration")

    config_files = {
        "/home/user/Private-Claude/config/e2b_sandbox_templates.json": "Sandbox Templates",
        "/home/user/Private-Claude/config/.env.example": "Environment Example",
    }

    all_valid = True
    for config_file, description in config_files.items():
        path = Path(config_file)
        if path.exists():
            try:
                if config_file.endswith('.json'):
                    with open(path, 'r') as f:
                        json.load(f)
                print(f"✓ {description} ({config_file})")
            except Exception as e:
                print(f"✗ {description} - Invalid: {e}")
                all_valid = False
        else:
            print(f"✗ {description} - Not found: {config_file}")
            all_valid = False

    return all_valid


def verify_scripts() -> bool:
    """Verify Python scripts"""
    print_header("Verifying Scripts")

    scripts = {
        "/home/user/Private-Claude/scripts/e2b_sandbox_manager.py": "Sandbox Manager",
        "/home/user/Private-Claude/scripts/e2b_lifecycle.py": "Lifecycle Manager",
    }

    all_valid = True
    for script_path, description in scripts.items():
        path = Path(script_path)
        if path.exists():
            if os.access(path, os.X_OK):
                print(f"✓ {description} (executable)")
            else:
                print(f"⚠ {description} (not executable, fixing...)")
                os.chmod(path, 0o755)
                print(f"✓ {description} (now executable)")

            # Try to import to check for syntax errors
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("module", script_path)
                module = importlib.util.module_from_spec(spec)
                # Don't execute, just check syntax
                with open(script_path, 'r') as f:
                    compile(f.read(), script_path, 'exec')
                print(f"  ✓ Syntax valid")
            except Exception as e:
                print(f"  ✗ Syntax error: {e}")
                all_valid = False
        else:
            print(f"✗ {description} - Not found: {script_path}")
            all_valid = False

    return all_valid


def test_imports() -> bool:
    """Test module imports"""
    print_header("Testing Imports")

    sys.path.insert(0, '/home/user/Private-Claude/scripts')

    try:
        print("Importing aiohttp... ", end="")
        import aiohttp
        print("✓")
    except ImportError as e:
        print(f"✗ {e}")
        return False

    try:
        print("Importing psutil... ", end="")
        import psutil
        print("✓")
    except ImportError as e:
        print(f"✗ {e}")
        return False

    try:
        print("Importing e2b_sandbox_manager... ", end="")
        from e2b_sandbox_manager import E2BSandboxManager
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        return False

    try:
        print("Importing e2b_lifecycle... ", end="")
        from e2b_lifecycle import LifecycleManager
        print("✓")
    except Exception as e:
        print(f"✗ {e}")
        return False

    return True


def show_quick_start() -> None:
    """Show quick start guide"""
    print_header("Quick Start Guide")

    guide = """
1. Create a Python sandbox:
   python3 /home/user/Private-Claude/scripts/e2b_sandbox_manager.py create \\
     --template python

2. Execute code in sandbox:
   python3 /home/user/Private-Claude/scripts/e2b_sandbox_manager.py exec \\
     --sandbox-id <sandbox_id> \\
     --language python \\
     --code "print('Hello E2B')"

3. Check sandbox status:
   python3 /home/user/Private-Claude/scripts/e2b_sandbox_manager.py status

4. Create automated lifecycle:
   python3 /home/user/Private-Claude/scripts/e2b_lifecycle.py create-lifecycle \\
     --sandbox-id test_sbx \\
     --template python \\
     --timeout 300 \\
     --script "print('Running in E2B')"

5. Create automated workflow:
   python3 /home/user/Private-Claude/scripts/e2b_lifecycle.py create-workflow \\
     --name my-workflow \\
     --trigger manual \\
     --template python

6. Available templates:
   - python: Python 3.11 with data science libraries
   - nodejs: Node.js 18 with npm ecosystem
   - general: Multi-language environment (Python, Node.js, bash)
   - minimal: Lightweight Alpine Linux environment

Environment Configuration:
   - Copy /home/user/Private-Claude/config/.env.example to .env
   - Update API keys and settings as needed
   - Export variables: export $(cat .env | xargs)

Documentation:
   - /home/user/Private-Claude/config/e2b_sandbox_templates.json
   - Full template and configuration specifications
"""
    print(guide)


def main():
    """Run setup"""
    print("\n" + "=" * 60)
    print("  E2B Sandbox Environment Setup")
    print("=" * 60)

    steps = [
        ("Checking dependencies", check_dependencies),
        ("Creating directories", create_directories),
        ("Setting up environment", setup_environment),
        ("Verifying configuration", verify_configuration),
        ("Verifying scripts", verify_scripts),
        ("Testing imports", test_imports),
    ]

    results = []
    for description, step_func in steps:
        try:
            result = step_func()
            results.append((description, result))
        except Exception as e:
            print(f"\n✗ ERROR in {description}: {e}")
            results.append((description, False))

    # Summary
    print_header("Setup Summary")
    all_passed = True
    for description, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {description}")
        if not result:
            all_passed = False

    # Quick start
    if all_passed:
        show_quick_start()
        print("\n✓ Setup completed successfully!")
        return 0
    else:
        print("\n✗ Setup completed with errors. Please review above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
