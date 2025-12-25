#!/usr/bin/env python3
"""
Comprehensive System Test Runner
Tests all major systems and generates detailed test report
"""

import os
import sys
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveSystemTester:
    """Comprehensive system tester for all components"""

    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        }

    def run_test(self, test_name: str, test_func, critical: bool = True) -> bool:
        """
        Run a single test and record results

        Args:
            test_name: Name of the test
            test_func: Function to execute
            critical: Whether failure should stop testing

        Returns:
            True if test passed, False otherwise
        """
        logger.info(f"\n{'='*70}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*70}")

        test_result = {
            'name': test_name,
            'critical': critical,
            'start_time': datetime.now().isoformat()
        }

        try:
            result = test_func()
            test_result['status'] = 'PASSED' if result else 'FAILED'
            test_result['passed'] = result

            if result:
                logger.info(f"✅ {test_name}: PASSED")
                self.test_results['summary']['passed'] += 1
            else:
                logger.error(f"❌ {test_name}: FAILED")
                self.test_results['summary']['failed'] += 1

        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            logger.error(traceback.format_exc())
            test_result['status'] = 'ERROR'
            test_result['error'] = str(e)
            test_result['traceback'] = traceback.format_exc()
            test_result['passed'] = False
            self.test_results['summary']['failed'] += 1

        test_result['end_time'] = datetime.now().isoformat()
        self.test_results['tests'].append(test_result)
        self.test_results['summary']['total'] += 1

        return test_result.get('passed', False)

    def test_python_syntax(self) -> bool:
        """Test all Python files for syntax errors"""
        logger.info("Checking Python files for syntax errors...")

        python_files = list(self.base_path.rglob('*.py'))
        errors = []

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError as e:
                errors.append(f"{py_file}: {e}")

        if errors:
            logger.error(f"Found {len(errors)} syntax errors:")
            for error in errors:
                logger.error(f"  - {error}")
            return False

        logger.info(f"✅ All {len(python_files)} Python files have valid syntax")
        return True

    def test_imports(self) -> bool:
        """Test critical imports"""
        logger.info("Testing critical imports...")

        critical_imports = [
            ('os', 'Standard Library'),
            ('sys', 'Standard Library'),
            ('json', 'Standard Library'),
            ('pathlib', 'Standard Library'),
            ('datetime', 'Standard Library'),
            ('requests', 'Third Party'),
            ('dotenv', 'Third Party - python-dotenv'),
        ]

        optional_imports = [
            ('ccxt', 'Trading - CCXT'),
            ('reportlab', 'PDF Generation'),
            ('docx', 'Document Generation - python-docx'),
            ('tqdm', 'Progress Bars'),
        ]

        all_passed = True

        for module_name, description in critical_imports:
            try:
                __import__(module_name)
                logger.info(f"✅ {module_name} ({description})")
            except ImportError:
                logger.error(f"❌ CRITICAL: {module_name} not available ({description})")
                all_passed = False

        logger.info("\nOptional imports:")
        for module_name, description in optional_imports:
            try:
                __import__(module_name)
                logger.info(f"✅ {module_name} ({description})")
            except ImportError:
                logger.warning(f"⚠️  {module_name} not available ({description})")

        return all_passed

    def test_configuration_files(self) -> bool:
        """Test that configuration files exist and are valid JSON"""
        logger.info("Testing configuration files...")

        config_files = [
            'config/agent_5_config.json',
            'config/trading_bot_24_7_config.json',
            'config/e2b_webhook_config.json',
        ]

        all_valid = True

        for config_file in config_files:
            config_path = self.base_path / config_file
            if not config_path.exists():
                logger.warning(f"⚠️  Config file not found: {config_file}")
                continue

            try:
                with open(config_path, 'r') as f:
                    json.load(f)
                logger.info(f"✅ {config_file} - Valid JSON")
            except json.JSONDecodeError as e:
                logger.error(f"❌ {config_file} - Invalid JSON: {e}")
                all_valid = False

        return all_valid

    def test_directory_structure(self) -> bool:
        """Test that required directories exist"""
        logger.info("Testing directory structure...")

        required_dirs = [
            'config',
            'scripts',
            'logs',
            'pillar-a-trading',
            'legal-automation',
            'system-integration',
            'cfo-suite',
        ]

        all_exist = True

        for dir_name in required_dirs:
            dir_path = self.base_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                logger.info(f"✅ {dir_name}/")
            else:
                logger.error(f"❌ {dir_name}/ - Missing")
                all_exist = False

        return all_exist

    def test_legal_automation(self) -> bool:
        """Test legal automation system"""
        logger.info("Testing legal automation system...")

        try:
            # Check master orchestrator exists
            orchestrator_path = self.base_path / 'legal-automation' / 'master_legal_orchestrator.py'
            if not orchestrator_path.exists():
                logger.error("Master legal orchestrator not found")
                return False

            # Check PDF automation
            pdf_automation_path = self.base_path / 'legal-automation' / 'pdf_form_automation.py'
            if not pdf_automation_path.exists():
                logger.error("PDF automation not found")
                return False

            logger.info("✅ Legal automation system files present")
            return True

        except Exception as e:
            logger.error(f"Legal automation test failed: {e}")
            return False

    def test_trading_bot(self) -> bool:
        """Test trading bot system"""
        logger.info("Testing trading bot system...")

        try:
            # Check bot runner
            bot_path = self.base_path / 'pillar-a-trading' / 'bot_24_7_runner.py'
            if not bot_path.exists():
                logger.error("Trading bot runner not found")
                return False

            # Check backtesting engine
            backtest_path = self.base_path / 'pillar-a-trading' / 'backtesting' / 'backtesting_engine.py'
            if not backtest_path.exists():
                logger.warning("⚠️  Backtesting engine not found")

            logger.info("✅ Trading bot system files present")
            return True

        except Exception as e:
            logger.error(f"Trading bot test failed: {e}")
            return False

    def test_cfo_suite(self) -> bool:
        """Test CFO suite integration"""
        logger.info("Testing CFO suite...")

        try:
            pillars = [
                'pillar1_financial_operations.py',
                'pillar2_legal_operations.py',
                'pillar3_trading_operations.py',
                'pillar4_business_intelligence.py',
            ]

            cfo_dir = self.base_path / 'cfo-suite'
            all_present = True

            for pillar in pillars:
                pillar_path = cfo_dir / pillar
                if pillar_path.exists():
                    logger.info(f"✅ {pillar}")
                else:
                    logger.error(f"❌ {pillar} - Missing")
                    all_present = False

            return all_present

        except Exception as e:
            logger.error(f"CFO suite test failed: {e}")
            return False

    def test_system_integration(self) -> bool:
        """Test system integration components"""
        logger.info("Testing system integration...")

        try:
            integration_dir = self.base_path / 'system-integration'

            # Check E2B integration
            e2b_dir = integration_dir / 'e2b'
            if e2b_dir.exists():
                logger.info("✅ E2B integration directory present")
            else:
                logger.warning("⚠️  E2B integration directory not found")

            # Check migration tools
            migration_path = integration_dir / 'enhanced_migration.py'
            if migration_path.exists():
                logger.info("✅ Enhanced migration tool present")
            else:
                logger.warning("⚠️  Enhanced migration tool not found")

            return True

        except Exception as e:
            logger.error(f"System integration test failed: {e}")
            return False

    def test_webhook_configs(self) -> bool:
        """Test webhook configurations"""
        logger.info("Testing webhook configurations...")

        # Count webhook placeholders
        placeholder_count = 0
        webhook_files = [
            'config/e2b_webhook_config.json',
            'config/zapier_connector.json',
            'ZAPIER_WORKFLOWS_COMPLETE.json',
        ]

        for webhook_file in webhook_files:
            webhook_path = self.base_path / webhook_file
            if not webhook_path.exists():
                continue

            try:
                with open(webhook_path, 'r') as f:
                    content = f.read()
                    if 'xxxxx' in content.lower() or 'placeholder' in content.lower():
                        placeholder_count += 1
                        logger.warning(f"⚠️  {webhook_file} contains placeholders")
            except:
                pass

        if placeholder_count > 0:
            logger.warning(f"Found {placeholder_count} files with webhook placeholders")
            logger.warning("Consider using webhook validator to replace placeholders")

        return True  # Not critical

    def test_log_directories(self) -> bool:
        """Test that log directories exist and are writable"""
        logger.info("Testing log directories...")

        log_dirs = [
            'logs',
            'logs/trading_bot',
            'logs/legal-automation',
            'logs/system',
        ]

        all_good = True

        for log_dir in log_dirs:
            log_path = self.base_path / log_dir
            log_path.mkdir(parents=True, exist_ok=True)

            # Test write permission
            test_file = log_path / '.test_write'
            try:
                test_file.write_text('test')
                test_file.unlink()
                logger.info(f"✅ {log_dir}/ - Writable")
            except Exception as e:
                logger.error(f"❌ {log_dir}/ - Not writable: {e}")
                all_good = False

        return all_good

    def generate_test_report(self) -> Path:
        """Generate comprehensive test report"""
        report_path = self.base_path / 'logs' / f"system_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        return report_path

    def run_all_tests(self) -> bool:
        """Run all system tests"""
        logger.info("\n" + "="*70)
        logger.info("COMPREHENSIVE SYSTEM TEST SUITE")
        logger.info("="*70 + "\n")

        # Run all tests
        tests = [
            ("Python Syntax Check", self.test_python_syntax, True),
            ("Critical Imports", self.test_imports, True),
            ("Configuration Files", self.test_configuration_files, False),
            ("Directory Structure", self.test_directory_structure, True),
            ("Legal Automation", self.test_legal_automation, False),
            ("Trading Bot", self.test_trading_bot, False),
            ("CFO Suite", self.test_cfo_suite, False),
            ("System Integration", self.test_system_integration, False),
            ("Webhook Configurations", self.test_webhook_configs, False),
            ("Log Directories", self.test_log_directories, True),
        ]

        all_critical_passed = True

        for test_name, test_func, critical in tests:
            passed = self.run_test(test_name, test_func, critical)

            if not passed and critical:
                all_critical_passed = False
                logger.error(f"CRITICAL TEST FAILED: {test_name}")

        # Generate report
        report_path = self.generate_test_report()

        # Print summary
        logger.info("\n" + "="*70)
        logger.info("TEST SUMMARY")
        logger.info("="*70)
        logger.info(f"Total Tests: {self.test_results['summary']['total']}")
        logger.info(f"Passed: {self.test_results['summary']['passed']}")
        logger.info(f"Failed: {self.test_results['summary']['failed']}")
        logger.info(f"Skipped: {self.test_results['summary']['skipped']}")

        pass_rate = (self.test_results['summary']['passed'] / self.test_results['summary']['total'] * 100) if self.test_results['summary']['total'] > 0 else 0
        logger.info(f"Pass Rate: {pass_rate:.1f}%")

        logger.info(f"\nDetailed report: {report_path}")
        logger.info("="*70 + "\n")

        if all_critical_passed:
            logger.info("✅ All critical tests passed!")
            return True
        else:
            logger.error("❌ Some critical tests failed - review report for details")
            return False


def main():
    """Main execution"""
    tester = ComprehensiveSystemTester()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
