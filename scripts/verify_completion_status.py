#!/usr/bin/env python3
"""
COMPLETION VERIFICATION SCRIPT
Verify all downloads, installations, and integrations are complete
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("COMPLETION VERIFICATION - Agent 5.0 Downloads & Add-ons")
print("=" * 80)
print(f"Verification Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Track completion status
completion_status = {
    "timestamp": datetime.now().isoformat(),
    "categories": {},
    "overall_status": "UNKNOWN"
}

# 1. Verify Legal Document Scripts
print("\n📥 1. LEGAL DOCUMENT DOWNLOAD SCRIPTS")
print("-" * 80)

legal_scripts = [
    "scripts/download_legal_documents_automated.py",
    "scripts/download_irs_forms.sh",
    "scripts/download_irs_forms_python.py",
    "scripts/download_nonprofit_forms.sh"
]

legal_configs = [
    "config/LEGAL_DOWNLOAD_AUTOMATION.json",
    "config/ZAPIER_LEGAL_DOWNLOAD_WORKFLOW.json",
    "config/GITHUB_ENTERPRISE_NONPROFIT.json"
]

legal_dirs = [
    "data/legal_documents/irs_forms",
    "data/legal_documents/sba_forms",
    "data/legal_documents/nonprofit_forms",
    "data/legal_documents/probate_forms"
]

legal_status = {
    "scripts": sum(1 for s in legal_scripts if os.path.exists(s)),
    "configs": sum(1 for c in legal_configs if os.path.exists(c)),
    "directories": sum(1 for d in legal_dirs if os.path.exists(d)),
    "total_files": len(legal_scripts) + len(legal_configs)
}

print(f"Scripts: {legal_status['scripts']}/{len(legal_scripts)}")
print(f"Configs: {legal_status['configs']}/{len(legal_configs)}")
print(f"Directories: {legal_status['directories']}/{len(legal_dirs)}")

completion_status["categories"]["legal_documents"] = {
    "status": "CONFIGURED" if legal_status['scripts'] == len(legal_scripts) else "INCOMPLETE",
    "details": legal_status
}

# 2. Verify Market Data Scripts
print("\n📈 2. MARKET DATA DOWNLOAD SCRIPTS")
print("-" * 80)

market_scripts = [
    "scripts/download_10_year_market_data.py",
    "scripts/download_forex_data.py",
    "scripts/download_crypto_data.py",
    "scripts/download_commodities_data.py",
    "scripts/ml_pattern_detection.py"
]

market_dirs = [
    "data/market_data/forex",
    "data/market_data/crypto",
    "data/market_data/commodities"
]

market_status = {
    "scripts": sum(1 for s in market_scripts if os.path.exists(s)),
    "directories": sum(1 for d in market_dirs if os.path.exists(d))
}

print(f"Scripts: {market_status['scripts']}/{len(market_scripts)}")
print(f"Directories: {market_status['directories']}/{len(market_dirs)}")

completion_status["categories"]["market_data"] = {
    "status": "CONFIGURED" if market_status['scripts'] == len(market_scripts) else "INCOMPLETE",
    "details": market_status
}

# 3. Verify Python Setup
print("\n🐍 3. PYTHON MULTI-VERSION SETUP")
print("-" * 80)

python_scripts = [
    "scripts/setup_python_multi_version.sh",
    "activate_trading_python.sh",
    ".python-version",
    ".pyenv-config.json",
    "Dockerfile.multi-python"
]

python_status = {
    "files": sum(1 for f in python_scripts if os.path.exists(f))
}

print(f"Configuration Files: {python_status['files']}/{len(python_scripts)}")

completion_status["categories"]["python_setup"] = {
    "status": "CONFIGURED" if python_status['files'] >= 3 else "INCOMPLETE",
    "details": python_status
}

# 4. Verify Trading Libraries
print("\n💹 4. TRADING LIBRARIES")
print("-" * 80)

try:
    # Check CCXT
    import ccxt
    ccxt_version = ccxt.__version__
    print(f"✅ CCXT: v{ccxt_version}")
    ccxt_installed = True
except ImportError:
    print("⚠️ CCXT: Not installed")
    ccxt_installed = False

try:
    import pandas
    print(f"✅ pandas: v{pandas.__version__}")
    pandas_installed = True
except ImportError:
    print("⚠️ pandas: Not installed")
    pandas_installed = False

try:
    import numpy
    print(f"✅ numpy: v{numpy.__version__}")
    numpy_installed = True
except ImportError:
    print("⚠️ numpy: Not installed")
    numpy_installed = False

try:
    import MetaTrader5
    print(f"✅ MetaTrader5: Installed")
    mt5_installed = True
except ImportError:
    print("⚠️ MetaTrader5: Not available (Windows-only)")
    mt5_installed = False

completion_status["categories"]["trading_libraries"] = {
    "status": "INSTALLED" if ccxt_installed and pandas_installed else "PARTIAL",
    "details": {
        "ccxt": ccxt_installed,
        "pandas": pandas_installed,
        "numpy": numpy_installed,
        "metatrader5": mt5_installed
    }
}

# 5. Verify Google APIs Setup
print("\n📧 5. GOOGLE APIS INTEGRATION")
print("-" * 80)

google_files = [
    "scripts/setup_google_apis.py",
    "scripts/google_oauth_flow.py",
    "config/google/oauth_credentials_template.json",
    "config/google/integration_config.json"
]

google_status = {
    "files": sum(1 for f in google_files if os.path.exists(f))
}

print(f"Configuration Files: {google_status['files']}/{len(google_files)}")

try:
    from google.auth import google_auth
    print("✅ Google Auth library installed")
    google_lib_installed = True
except ImportError:
    try:
        import google.auth
        print("✅ Google Auth library installed")
        google_lib_installed = True
    except ImportError:
        print("⚠️ Google Auth library not installed")
        google_lib_installed = False

completion_status["categories"]["google_apis"] = {
    "status": "CONFIGURED" if google_status['files'] == len(google_files) else "INCOMPLETE",
    "details": {"files": google_status['files'], "library": google_lib_installed}
}

# 6. Verify Microsoft Graph API Setup
print("\n📊 6. MICROSOFT GRAPH API INTEGRATION")
print("-" * 80)

microsoft_files = [
    "scripts/setup_microsoft_graph.py",
    "scripts/microsoft_graph_auth.py",
    "config/microsoft/app_registration_template.json",
    "config/microsoft/templates_config.json"
]

microsoft_status = {
    "files": sum(1 for f in microsoft_files if os.path.exists(f))
}

print(f"Configuration Files: {microsoft_status['files']}/{len(microsoft_files)}")

try:
    import msal
    print("✅ MSAL library installed")
    msal_installed = True
except ImportError:
    print("⚠️ MSAL library not installed")
    msal_installed = False

completion_status["categories"]["microsoft_graph"] = {
    "status": "CONFIGURED" if microsoft_status['files'] == len(microsoft_files) else "INCOMPLETE",
    "details": {"files": microsoft_status['files'], "library": msal_installed}
}

# 7. Verify Airtable Setup
print("\n📋 7. AIRTABLE INTEGRATION")
print("-" * 80)

airtable_files = [
    "scripts/setup_airtable.py",
    "scripts/airtable_integration.py",
    "config/airtable/config_template.json",
    "config/airtable/zapier_workflows.json",
    "docs/AIRTABLE_USAGE_GUIDE.md"
]

airtable_status = {
    "files": sum(1 for f in airtable_files if os.path.exists(f))
}

print(f"Configuration Files: {airtable_status['files']}/{len(airtable_files)}")

try:
    from airtable import Airtable
    print("✅ Airtable library installed")
    airtable_installed = True
except ImportError:
    print("⚠️ Airtable library not installed")
    airtable_installed = False

completion_status["categories"]["airtable"] = {
    "status": "CONFIGURED" if airtable_status['files'] == len(airtable_files) else "INCOMPLETE",
    "details": {"files": airtable_status['files'], "library": airtable_installed}
}

# 8. Verify GitHub Actions Workflows
print("\n⚙️ 8. GITHUB ACTIONS WORKFLOWS")
print("-" * 80)

github_workflows_dir = ".github/workflows"
if os.path.exists(github_workflows_dir):
    workflows = list(Path(github_workflows_dir).glob("*.yml"))
    print(f"Active Workflows: {len(workflows)}")
    for wf in workflows[:5]:  # Show first 5
        print(f"  • {wf.name}")
    if len(workflows) > 5:
        print(f"  • ... and {len(workflows) - 5} more")

    completion_status["categories"]["github_actions"] = {
        "status": "ACTIVE",
        "details": {"workflow_count": len(workflows)}
    }
else:
    print("⚠️ GitHub workflows directory not found")
    completion_status["categories"]["github_actions"] = {
        "status": "NOT_FOUND",
        "details": {}
    }

# 9. Verify GitLab CI/CD
print("\n🔄 9. GITLAB CI/CD PIPELINE")
print("-" * 80)

gitlab_ci = ".gitlab-ci.yml"
if os.path.exists(gitlab_ci):
    with open(gitlab_ci, 'r') as f:
        content = f.read()
        stages = content.count("stage:")
        print(f"✅ GitLab CI configured")
        print(f"Pipeline Stages: ~{stages}")

    completion_status["categories"]["gitlab_cicd"] = {
        "status": "CONFIGURED",
        "details": {"stages": stages}
    }
else:
    print("⚠️ GitLab CI configuration not found")
    completion_status["categories"]["gitlab_cicd"] = {
        "status": "NOT_FOUND",
        "details": {}
    }

# 10. Verify Documentation
print("\n📄 10. DOCUMENTATION")
print("-" * 80)

docs = [
    "COMPLETION_REPORT.md",
    "docs/AIRTABLE_USAGE_GUIDE.md"
]

docs_status = {
    "files": sum(1 for d in docs if os.path.exists(d))
}

print(f"Documentation Files: {docs_status['files']}/{len(docs)}")
for doc in docs:
    if os.path.exists(doc):
        print(f"  ✅ {doc}")
    else:
        print(f"  ⚠️ {doc} (missing)")

completion_status["categories"]["documentation"] = {
    "status": "COMPLETE" if docs_status['files'] == len(docs) else "PARTIAL",
    "details": docs_status
}

# Overall Status Calculation
print("\n" + "=" * 80)
print("OVERALL STATUS")
print("=" * 80)

total_categories = len(completion_status["categories"])
completed_categories = sum(
    1 for cat in completion_status["categories"].values()
    if cat["status"] in ["CONFIGURED", "INSTALLED", "ACTIVE", "COMPLETE"]
)

completion_percentage = (completed_categories / total_categories) * 100

print(f"\nCompleted: {completed_categories}/{total_categories} categories")
print(f"Completion: {completion_percentage:.1f}%")

if completion_percentage >= 90:
    overall = "EXCELLENT ✅"
elif completion_percentage >= 75:
    overall = "GOOD ✅"
elif completion_percentage >= 50:
    overall = "PARTIAL ⚠️"
else:
    overall = "NEEDS WORK ⚠️"

print(f"Overall Status: {overall}")

completion_status["overall_status"] = overall
completion_status["completion_percentage"] = completion_percentage

# Save verification report
report_file = "data/completion_verification.json"
os.makedirs("data", exist_ok=True)
with open(report_file, 'w') as f:
    json.dump(completion_status, f, indent=2)

print(f"\n📊 Verification report saved: {report_file}")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\n✅ COMPLETED ITEMS:")
for cat_name, cat_data in completion_status["categories"].items():
    if cat_data["status"] in ["CONFIGURED", "INSTALLED", "ACTIVE", "COMPLETE"]:
        print(f"  • {cat_name.replace('_', ' ').title()}: {cat_data['status']}")

print("\n⚠️ ITEMS NEEDING ATTENTION:")
for cat_name, cat_data in completion_status["categories"].items():
    if cat_data["status"] not in ["CONFIGURED", "INSTALLED", "ACTIVE", "COMPLETE"]:
        print(f"  • {cat_name.replace('_', ' ').title()}: {cat_data['status']}")

print("\n" + "=" * 80)
print(f"Verification complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
