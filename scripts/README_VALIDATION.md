# Requirements Validation Script

## Overview
Automated validation tool for `requirements.txt` to prevent dependency issues before they cause workflow failures.

## Features
- ✅ Checks package availability on PyPI
- ✅ Detects yanked package versions
- ✅ Validates version specifiers
- ✅ Tests installation compatibility
- ⚠️ Warns about exact version pins
- 📊 Provides detailed reports

## Usage

### Basic Validation
```bash
python scripts/validate_requirements.py
```

### Specify Custom Requirements File
```bash
python scripts/validate_requirements.py --file path/to/requirements.txt
```

### Output Example
```
Validating requirements.txt

============================================================
✓ Found 20 packages to validate

Checking package availability...
✓ urllib3: Available
✓ requests: Available
✓ pytest: Available
...

Analyzing version specifications...
⚠ requests: Exact version pinned ==2.31.0

Testing installation...
✓ All dependencies can be installed

============================================================

Summary:

✓ No critical issues found!

⚠ 1 warning(s):
  - 1 packages have exact version pins

Validation passed!
```

## What It Checks

### 1. Package Availability
- Verifies each package exists on PyPI
- Checks if specific versions are available
- Detects yanked versions that can't be installed

### 2. Version Specifications
- Analyzes version pinning strategies
- Warns about exact version pins (==)
- Recommends using ranges (>=) for flexibility

### 3. Installation Test
- Performs dry-run installation
- Detects dependency conflicts
- Validates all packages can be resolved together

## Exit Codes
- `0` - All checks passed
- `1` - Critical issues found

## Integration with CI/CD

### GitHub Actions
Add to your workflow:

```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Validate requirements
  run: python scripts/validate_requirements.py
```

Complete workflow example:

```yaml
name: Validate Requirements

on:
  pull_request:
    paths:
      - 'requirements.txt'
  push:
    branches:
      - main

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install validation dependencies
        run: pip install --upgrade pip
      
      - name: Validate requirements.txt
        run: python scripts/validate_requirements.py
```

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
python scripts/validate_requirements.py
if [ $? -ne 0 ]; then
    echo "Requirements validation failed. Fix issues before committing."
    exit 1
fi
```

## Best Practices

### DO ✅
- Use version ranges (>=) for flexibility
- Run validation before committing changes
- Keep dependencies updated regularly
- Review PyPI changelog before updates

### DON'T ❌
- Pin exact versions unless necessary
- Use yanked package versions
- Skip validation for "minor" changes
- Mix incompatible version constraints

## Troubleshooting

### Package Not Found
If a package shows as "not found":
1. Check spelling of package name
2. Verify package exists on PyPI
3. Check if package was renamed or removed

### Version Not Available
If a specific version isn't available:
1. Check if version was yanked
2. Review package changelog for migration guide
3. Update to latest stable version

### Installation Conflicts
If dry-run fails:
1. Review error message for conflicting packages
2. Check version constraints
3. Update conflicting packages together

## Related Documentation
- [Workflow Error Fix Guide](../docs/WORKFLOW_ERROR_FIX_2026_01_13.md)
- [GitHub Actions Workflow](.github/workflows/agent-x5-master-automation.yml)
- [Requirements.txt](../requirements.txt)

## Contributing
When adding new dependencies:
1. Run validation script first
2. Use `>=` for version specs when possible
3. Document why exact versions are needed
4. Test in isolation before committing

---
**Created**: January 13, 2026  
**Maintainer**: GitHub Copilot Agent  
**Version**: 1.0.0
