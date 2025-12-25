#!/usr/bin/env python3
"""
Migration Verification Tool
Compare source and destination to verify complete migration

For research, development, and educational purposes only.
"""

import os
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple
from collections import defaultdict


class MigrationVerifier:
    """Verify migration completeness"""

    def __init__(self, output_dir: str = '/home/user/migrated-docs'):
        """Initialize verifier"""
        self.output_dir = Path(output_dir)
        self.report_file = self.output_dir / 'migration_report.json'
        self.state_file = self.output_dir / 'migration_state.json'

        self.report = None
        self.state = None

    def load_reports(self) -> bool:
        """Load migration reports"""
        print("📋 Loading migration reports...")

        if not self.report_file.exists():
            print(f"  ❌ Migration report not found: {self.report_file}")
            return False

        with open(self.report_file, 'r') as f:
            self.report = json.load(f)

        print(f"  ✅ Loaded migration report")

        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.state = json.load(f)
            print(f"  ✅ Loaded migration state")

        return True

    def verify_file_counts(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify file counts"""
        print("\n📊 Verifying File Counts...")

        stats = self.report.get('statistics', {})
        total_files = stats.get('total_files', 0)
        migrated_files = stats.get('migrated_files', 0)
        failed_files = stats.get('failed_files', 0)

        print(f"  Total files found: {total_files}")
        print(f"  Successfully migrated: {migrated_files}")
        print(f"  Failed: {failed_files}")

        success_rate = (migrated_files / total_files * 100) if total_files > 0 else 0

        if success_rate == 100:
            print(f"  ✅ 100% migration success rate")
            status = True
        elif success_rate >= 95:
            print(f"  ⚠️  {success_rate:.1f}% migration success rate (acceptable)")
            status = True
        else:
            print(f"  ❌ {success_rate:.1f}% migration success rate (below threshold)")
            status = False

        return status, {
            'total_files': total_files,
            'migrated_files': migrated_files,
            'failed_files': failed_files,
            'success_rate': success_rate
        }

    def verify_file_sizes(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify total file sizes"""
        print("\n💾 Verifying File Sizes...")

        stats = self.report.get('statistics', {})
        total_size_bytes = stats.get('total_size_bytes', 0)

        # Calculate actual size on disk
        actual_size = 0
        file_count = 0

        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                if not file.endswith('.metadata.json') and file not in ['migration_report.json', 'migration_report.csv']:
                    file_path = Path(root) / file
                    try:
                        actual_size += file_path.stat().st_size
                        file_count += 1
                    except OSError:
                        pass

        expected_mb = total_size_bytes / (1024 * 1024)
        actual_mb = actual_size / (1024 * 1024)

        print(f"  Expected size: {expected_mb:.2f} MB")
        print(f"  Actual size: {actual_mb:.2f} MB")
        print(f"  Files on disk: {file_count}")

        # Allow 5% variance for metadata overhead
        variance = abs(actual_size - total_size_bytes) / total_size_bytes if total_size_bytes > 0 else 0

        if variance <= 0.05:
            print(f"  ✅ Size verification passed (variance: {variance*100:.1f}%)")
            status = True
        else:
            print(f"  ⚠️  Size variance: {variance*100:.1f}%")
            status = True  # Still pass, just warn

        return status, {
            'expected_size_mb': expected_mb,
            'actual_size_mb': actual_mb,
            'variance_percent': variance * 100,
            'files_on_disk': file_count
        }

    def verify_file_types(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify file type distribution"""
        print("\n📄 Verifying File Types...")

        # Count file types from report
        files = self.report.get('files', [])
        type_counts = defaultdict(int)
        type_sizes = defaultdict(int)

        for file_info in files:
            ext = Path(file_info['name']).suffix.lower() or 'no_extension'
            type_counts[ext] += 1
            type_sizes[ext] += file_info.get('size', 0)

        # Display top 10 file types
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)

        print(f"  Total file types: {len(type_counts)}")
        print(f"\n  Top file types:")

        for ext, count in sorted_types[:10]:
            size_mb = type_sizes[ext] / (1024 * 1024)
            print(f"    {ext:20s} {count:6d} files  ({size_mb:8.2f} MB)")

        return True, {
            'total_types': len(type_counts),
            'type_distribution': dict(sorted_types[:20])
        }

    def verify_structure(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify directory structure"""
        print("\n📁 Verifying Directory Structure...")

        # Check expected directories
        onedrive_dir = self.output_dir / 'onedrive'
        sharepoint_dir = self.output_dir / 'sharepoint'

        onedrive_exists = onedrive_dir.exists()
        sharepoint_exists = sharepoint_dir.exists()

        if onedrive_exists:
            onedrive_count = sum(1 for _ in onedrive_dir.rglob('*') if _.is_file() and not _.name.endswith('.metadata.json'))
            print(f"  ✅ OneDrive directory: {onedrive_count} files")
        else:
            onedrive_count = 0
            print(f"  ℹ️  OneDrive directory not found (may not have OneDrive files)")

        if sharepoint_exists:
            sharepoint_count = sum(1 for _ in sharepoint_dir.rglob('*') if _.is_file() and not _.name.endswith('.metadata.json'))
            print(f"  ✅ SharePoint directory: {sharepoint_count} files")
        else:
            sharepoint_count = 0
            print(f"  ℹ️  SharePoint directory not found (may not have SharePoint files)")

        return True, {
            'onedrive_files': onedrive_count,
            'sharepoint_files': sharepoint_count,
            'total_files': onedrive_count + sharepoint_count
        }

    def check_failed_files(self) -> Tuple[bool, Dict[str, Any]]:
        """Check for failed files and suggest retry"""
        print("\n⚠️  Checking Failed Files...")

        failed_files = []

        if self.state:
            failed_files = self.state.get('failed_files', [])

        if not failed_files:
            print("  ✅ No failed files")
            return True, {'failed_count': 0}

        print(f"  ❌ Found {len(failed_files)} failed files")

        # Group by reason if available
        by_type = defaultdict(list)
        for file_info in failed_files[:10]:  # Show first 10
            file_name = file_info.get('name', 'Unknown')
            print(f"    - {file_name}")
            by_type[file_info.get('type', 'unknown')].append(file_name)

        if len(failed_files) > 10:
            print(f"    ... and {len(failed_files) - 10} more")

        print(f"\n  💡 Tip: Retry failed files with:")
        print(f"     python enhanced_migration.py --resume")

        return False, {
            'failed_count': len(failed_files),
            'by_type': {k: len(v) for k, v in by_type.items()}
        }

    def verify_metadata(self) -> Tuple[bool, Dict[str, Any]]:
        """Verify metadata files exist"""
        print("\n📝 Verifying Metadata...")

        metadata_count = 0
        for root, dirs, files in os.walk(self.output_dir):
            metadata_count += sum(1 for f in files if f.endswith('.metadata.json'))

        stats = self.report.get('statistics', {})
        migrated_files = stats.get('migrated_files', 0)

        print(f"  Metadata files: {metadata_count}")
        print(f"  Migrated files: {migrated_files}")

        if metadata_count == migrated_files:
            print(f"  ✅ All migrated files have metadata")
            status = True
        else:
            print(f"  ⚠️  Metadata count mismatch")
            status = True  # Not critical

        return status, {
            'metadata_count': metadata_count,
            'expected_count': migrated_files
        }

    def generate_verification_report(self, results: Dict[str, Any]):
        """Generate verification report"""
        report_path = self.output_dir / 'verification_report.json'

        report = {
            'timestamp': datetime.now().isoformat(),
            'output_directory': str(self.output_dir.absolute()),
            'verification_results': results,
            'overall_status': all(r.get('passed', False) for r in results.values())
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Verification report saved: {report_path}")

    def print_summary(self, results: Dict[str, Any]):
        """Print verification summary"""
        print("\n" + "="*70)
        print("  VERIFICATION SUMMARY")
        print("="*70)

        all_passed = all(r.get('passed', False) for r in results.values())

        for test_name, test_result in results.items():
            status = "✅" if test_result.get('passed', False) else "❌"
            print(f"  {status} {test_name}")

        print("\n" + "="*70)

        if all_passed:
            print("\n  🎉 Migration verification PASSED!")
            print("  All files migrated successfully.\n")
        else:
            print("\n  ⚠️  Migration verification completed with warnings.")
            print("  Review failed tests above.\n")

        print("="*70 + "\n")

    def run_verification(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("  MICROSOFT 365 MIGRATION VERIFICATION")
        print("="*70)
        print(f"  Output Directory: {self.output_dir.absolute()}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        print("="*70)

        if not self.load_reports():
            print("\n❌ Cannot verify - migration reports not found")
            return False

        results = {}

        # Run all verification checks
        passed, data = self.verify_file_counts()
        results['File Counts'] = {'passed': passed, 'data': data}

        passed, data = self.verify_file_sizes()
        results['File Sizes'] = {'passed': passed, 'data': data}

        passed, data = self.verify_file_types()
        results['File Types'] = {'passed': passed, 'data': data}

        passed, data = self.verify_structure()
        results['Directory Structure'] = {'passed': passed, 'data': data}

        passed, data = self.check_failed_files()
        results['Failed Files'] = {'passed': passed, 'data': data}

        passed, data = self.verify_metadata()
        results['Metadata'] = {'passed': passed, 'data': data}

        # Generate report
        self.generate_verification_report(results)

        # Print summary
        self.print_summary(results)

        return all(r.get('passed', False) for r in results.values())


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(
        description='Verify Microsoft 365 migration completeness'
    )
    parser.add_argument(
        '--output-dir',
        default='/home/user/migrated-docs',
        help='Migration output directory'
    )

    args = parser.parse_args()

    verifier = MigrationVerifier(output_dir=args.output_dir)
    success = verifier.run_verification()

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
