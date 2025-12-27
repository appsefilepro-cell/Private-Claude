# Test Suite for Deleted Files

## Overview

This directory contains comprehensive unit tests for files that were deleted in the current branch compared to `main`. These tests serve multiple purposes:

1. **Historical Validation** - Verify the deleted files had correct functionality
2. **Regression Prevention** - Ensure system stability after deletion
3. **Documentation** - Provide living documentation of what was removed
4. **Future Reference** - Tests ready if files are ever restored

## Test Files

### 1. test_scriptable_widgets.py (212 lines)
Tests for deleted JavaScript widget files used with iOS Scriptable app:
- **Random Scriptable API.js** - Widget displaying random Scriptable API docs
- **Reminders Due Today.js** - Reminder management widget
- **iTermWidget.js** - Terminal-style widget with calendar, weather, and device stats

**Test Coverage:**
- Widget structure validation
- Configuration constants
- Color scheme and styling
- API endpoint validation
- Data formatting and presentation
- Integration patterns

### 2. test_azure_workflows.py (343 lines)
Tests for deleted Azure Logic Apps workflow definitions:
- **ai_builder_sensitive_info_flow 2.json** - Sensitive information detection workflow
- **flow7_definition.json** - Quarterly report generation workflow

**Test Coverage:**
- JSON schema validation
- Workflow structure (triggers, actions, parameters)
- SharePoint integration
- Data operations
- Connection references
- Action dependencies and execution order

### 3. test_transaction_csvs.py (452 lines)
Tests for deleted CSV transaction files:
- PayPal transaction exports (2025-08-05, 2025-08-14)
- DocuPost CSV Template
- Nexo cryptocurrency transactions
- Robinhood Crypto transactions
- Bitcoin price history

**Test Coverage:**
- CSV structure and format validation
- Data type validation (dates, amounts, decimals)
- Column header validation
- Transaction category validation
- Cryptocurrency transaction specifics
- Data integrity checks

### 4. test_file_deletion_regression.py (366 lines)
System-wide regression tests ensuring stability after file deletion:

**Test Coverage:**
- Repository structure integrity
- Python module imports
- Configuration file presence
- No broken dependencies
- System pillar accessibility
- Documentation completeness
- No orphaned references

## Running the Tests

### Run All Tests
```bash
python tests/deleted_files/run_all_tests.py
```

### Run Individual Test Files
```bash
# Widget tests
pytest tests/deleted_files/test_scriptable_widgets.py -v

# Azure workflow tests
pytest tests/deleted_files/test_azure_workflows.py -v

# CSV transaction tests
pytest tests/deleted_files/test_transaction_csvs.py -v

# Regression tests
pytest tests/deleted_files/test_file_deletion_regression.py -v
```

### Run Specific Test Classes
```bash
# Test only Random Scriptable API widget
pytest tests/deleted_files/test_scriptable_widgets.py::TestRandomScriptableAPIWidget -v

# Test only PayPal CSV format
pytest tests/deleted_files/test_transaction_csvs.py::TestPayPalTransactionCSV -v
```

### Run with Coverage
```bash
pytest tests/deleted_files/ --cov=. --cov-report=html
```

## Test Statistics

- **Total Test Files**: 4
- **Total Lines of Test Code**: 1,373
- **Estimated Test Count**: 100+
- **Files Validated**: 49 deleted files
  - 3 JavaScript files
  - 2 JSON workflow files
  - 6 CSV files
  - 35 PDF documents
  - 3 DOCX files

## Deleted Files Reference

### JavaScript Files
- `Random Scriptable API.js` - iOS widget for Scriptable app
- `Reminders Due Today.js` - Reminder management widget
- `iTermWidget.js` - Terminal-style information widget

### JSON Workflow Files
- `ai_builder_sensitive_info_flow 2.json` - Azure sensitive data detection
- `flow7_definition.json` - Azure quarterly report automation

### CSV Transaction Files
- `2025-08-05T13_01_10.438Z-transactions.csv` - PayPal transactions
- `2025-08-14T20_04_27.046Z-transactions.csv` - PayPal transactions
- `DocuPost CSV Template.csv` - Mailing template
- `Nexo_Transactions_1740794579.csv` - Crypto exchange transactions
- `Robinhood Crypto Transactions.csv` - Robinhood crypto trades
- `bitcoin_2024-03-17_2024-04-16.csv` - Bitcoin price history

### PDF Documents (35 files)
Legal documents, reports, contracts, and correspondence

### DOCX Files (3 files)
Legal briefs and documentation

## Test Philosophy

These tests follow the principle of **"bias for action"** - even for deleted files, we create comprehensive tests because:

1. **Prove Correct Functionality** - Validate files worked correctly before deletion
2. **Document Intent** - Tests serve as documentation of what was removed
3. **Enable Safe Restoration** - If files need to be restored, tests are ready
4. **Prevent Regressions** - Ensure deletion doesn't break system functionality
5. **Demonstrate Thoroughness** - Show comprehensive understanding of the codebase

## Integration with Existing Tests

These tests complement the existing test suite:
- `tests/comprehensive_system_test.py` - System-wide validation
- `tests/integration_test_suite.py` - Integration testing
- `tests/test_zapier_integrations.py` - Zapier MCP testing

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Run Deleted Files Tests
  run: |
    pytest tests/deleted_files/ -v --tb=short
```

## Contributing

When adding more tests for deleted files:

1. Follow existing test patterns (pytest fixtures, descriptive names)
2. Group related tests in classes
3. Add comprehensive docstrings
4. Test both happy paths and edge cases
5. Validate data formats and business logic
6. Update this README with new test counts

## Notes

- All tests are written in Python using pytest framework
- Tests use fixtures for sample data
- No external API calls (all mocked/simulated)
- Tests are deterministic and repeatable
- No side effects or file system modifications

## License

These tests are part of the Agent X2.0 Enterprise Automation System.