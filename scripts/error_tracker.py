#!/usr/bin/env python3
"""
Error Tracking System
Centralized error logging with categorization, root cause analysis, and alerting
"""

import os
import sys
import json
import traceback
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import logging
import re

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ErrorCategory:
    """Error category definitions"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ErrorType:
    """Error type classifications"""
    SYNTAX_ERROR = "SYNTAX_ERROR"
    IMPORT_ERROR = "IMPORT_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    API_ERROR = "API_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    PERMISSION_ERROR = "PERMISSION_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class ErrorTracker:
    """Centralized error tracking and analysis system"""

    def __init__(self, base_path: str = None, error_db_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.error_db_path = error_db_path or os.path.join(self.base_path, 'logs', 'error_tracking.json')
        self.error_db = self._load_error_database()
        self.session_errors = []
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')

    def _load_error_database(self) -> Dict:
        """Load existing error database"""
        if os.path.exists(self.error_db_path):
            try:
                with open(self.error_db_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Could not load error database: {e}")
                return self._create_empty_database()
        return self._create_empty_database()

    def _create_empty_database(self) -> Dict:
        """Create empty error database structure"""
        return {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'errors': [],
            'patterns': {},
            'statistics': {
                'total_errors': 0,
                'by_category': {},
                'by_type': {},
                'by_source': {}
            }
        }

    def track_error(
        self,
        error: Exception = None,
        category: str = ErrorCategory.ERROR,
        error_type: str = ErrorType.UNKNOWN_ERROR,
        message: str = None,
        source: str = None,
        context: Dict = None,
        auto_categorize: bool = True
    ) -> str:
        """
        Track an error occurrence

        Args:
            error: Exception object (optional)
            category: Error category (CRITICAL, ERROR, WARNING, INFO)
            error_type: Type of error
            message: Error message
            source: Source file/module where error occurred
            context: Additional context information
            auto_categorize: Automatically categorize error based on exception type

        Returns:
            Error ID (hash)
        """
        # Extract information from exception if provided
        if error:
            if auto_categorize:
                category, error_type = self._categorize_exception(error)
            message = message or str(error)

            # Get traceback
            tb = traceback.extract_tb(error.__traceback__)
            if tb:
                source = source or tb[-1].filename
                context = context or {}
                context['line_number'] = tb[-1].lineno
                context['function'] = tb[-1].name
                context['traceback'] = ''.join(traceback.format_tb(error.__traceback__))

        # Generate error ID based on type and message
        error_id = self._generate_error_id(error_type, message, source)

        # Create error record
        error_record = {
            'id': error_id,
            'timestamp': datetime.now().isoformat(),
            'category': category,
            'type': error_type,
            'message': message,
            'source': source,
            'context': context or {},
            'resolved': False,
            'resolution': None,
            'occurrences': 1,
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat()
        }

        # Check if this error has been seen before
        existing_error = self._find_existing_error(error_id)
        if existing_error:
            existing_error['occurrences'] += 1
            existing_error['last_seen'] = datetime.now().isoformat()
            existing_error['category'] = max(existing_error['category'], category, key=self._severity_rank)
            error_record = existing_error
        else:
            self.error_db['errors'].append(error_record)

        # Add to session errors
        self.session_errors.append(error_record)

        # Update statistics
        self._update_statistics(error_record)

        # Detect patterns
        self._detect_patterns()

        # Send alerts if necessary
        if category == ErrorCategory.CRITICAL:
            self._send_alert(error_record)

        # Save database
        self._save_error_database()

        logger.log(
            self._category_to_log_level(category),
            f"[{error_type}] {message} (ID: {error_id[:8]})"
        )

        return error_id

    def _categorize_exception(self, error: Exception) -> tuple:
        """Automatically categorize exception"""
        error_class = type(error).__name__

        # Map exception types to categories and types
        critical_exceptions = {
            'SystemExit', 'KeyboardInterrupt', 'MemoryError', 'RecursionError'
        }

        if error_class in critical_exceptions:
            return ErrorCategory.CRITICAL, ErrorType.RUNTIME_ERROR

        if isinstance(error, SyntaxError):
            return ErrorCategory.CRITICAL, ErrorType.SYNTAX_ERROR
        elif isinstance(error, ImportError):
            return ErrorCategory.ERROR, ErrorType.IMPORT_ERROR
        elif isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorCategory.ERROR, ErrorType.NETWORK_ERROR
        elif isinstance(error, PermissionError):
            return ErrorCategory.ERROR, ErrorType.PERMISSION_ERROR
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorCategory.WARNING, ErrorType.VALIDATION_ERROR
        elif 'API' in error_class or 'HTTP' in error_class:
            return ErrorCategory.ERROR, ErrorType.API_ERROR
        elif 'Database' in error_class or 'SQL' in error_class:
            return ErrorCategory.CRITICAL, ErrorType.DATABASE_ERROR
        else:
            return ErrorCategory.ERROR, ErrorType.RUNTIME_ERROR

    def _generate_error_id(self, error_type: str, message: str, source: str) -> str:
        """Generate unique error ID"""
        # Normalize message to group similar errors
        normalized = re.sub(r'\d+', 'N', message or '')  # Replace numbers
        normalized = re.sub(r'0x[0-9a-fA-F]+', '0xHEX', normalized)  # Replace hex addresses
        normalized = re.sub(r'/[^\s]+', '/PATH', normalized)  # Replace paths

        hash_input = f"{error_type}:{normalized}:{source or 'unknown'}"
        return hashlib.md5(hash_input.encode()).hexdigest()

    def _find_existing_error(self, error_id: str) -> Optional[Dict]:
        """Find existing error by ID"""
        for error in self.error_db['errors']:
            if error['id'] == error_id and not error.get('resolved', False):
                return error
        return None

    def _severity_rank(self, category: str) -> int:
        """Get severity ranking for comparison"""
        ranks = {
            ErrorCategory.CRITICAL: 4,
            ErrorCategory.ERROR: 3,
            ErrorCategory.WARNING: 2,
            ErrorCategory.INFO: 1
        }
        return ranks.get(category, 0)

    def _category_to_log_level(self, category: str) -> int:
        """Convert error category to logging level"""
        levels = {
            ErrorCategory.CRITICAL: logging.CRITICAL,
            ErrorCategory.ERROR: logging.ERROR,
            ErrorCategory.WARNING: logging.WARNING,
            ErrorCategory.INFO: logging.INFO
        }
        return levels.get(category, logging.INFO)

    def _update_statistics(self, error_record: Dict) -> None:
        """Update error statistics"""
        stats = self.error_db['statistics']
        stats['total_errors'] = len(self.error_db['errors'])

        # By category
        category = error_record['category']
        stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

        # By type
        error_type = error_record['type']
        stats['by_type'][error_type] = stats['by_type'].get(error_type, 0) + 1

        # By source
        source = error_record.get('source', 'unknown')
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

    def _detect_patterns(self) -> None:
        """Detect error patterns and trends"""
        # Get recent errors (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_errors = [
            e for e in self.error_db['errors']
            if datetime.fromisoformat(e['last_seen']) > cutoff_time
        ]

        # Pattern 1: Repeated errors
        error_counts = Counter(e['id'] for e in recent_errors)
        repeated_errors = {
            eid: count for eid, count in error_counts.items() if count >= 5
        }

        if repeated_errors:
            self.error_db['patterns']['repeated_errors'] = {
                'detected': datetime.now().isoformat(),
                'errors': repeated_errors,
                'description': 'Errors occurring 5+ times in 24 hours'
            }

        # Pattern 2: Error bursts (many errors in short time)
        if len(recent_errors) >= 10:
            time_windows = defaultdict(int)
            for error in recent_errors:
                # Group by 10-minute windows
                timestamp = datetime.fromisoformat(error['last_seen'])
                window = timestamp.replace(minute=(timestamp.minute // 10) * 10, second=0, microsecond=0)
                time_windows[window.isoformat()] += 1

            burst_windows = {
                window: count for window, count in time_windows.items() if count >= 5
            }

            if burst_windows:
                self.error_db['patterns']['error_bursts'] = {
                    'detected': datetime.now().isoformat(),
                    'windows': burst_windows,
                    'description': 'High error rate (5+ errors in 10 minutes)'
                }

        # Pattern 3: Related errors (same source, similar time)
        source_groups = defaultdict(list)
        for error in recent_errors:
            source_groups[error.get('source', 'unknown')].append(error)

        cascading_sources = {
            source: len(errors) for source, errors in source_groups.items()
            if len(errors) >= 3 and len(set(e['type'] for e in errors)) >= 2
        }

        if cascading_sources:
            self.error_db['patterns']['cascading_failures'] = {
                'detected': datetime.now().isoformat(),
                'sources': cascading_sources,
                'description': 'Multiple error types from same source'
            }

    def analyze_root_cause(self, error_id: str) -> Dict[str, Any]:
        """Perform root cause analysis on an error"""
        error = self._find_existing_error(error_id)
        if not error:
            error = next((e for e in self.error_db['errors'] if e['id'] == error_id), None)

        if not error:
            return {'error': 'Error not found'}

        analysis = {
            'error_id': error_id,
            'error_type': error['type'],
            'category': error['category'],
            'occurrences': error.get('occurrences', 1),
            'duration': self._calculate_duration(error),
            'potential_causes': [],
            'related_errors': [],
            'suggested_fixes': []
        }

        # Identify potential causes based on error type
        if error['type'] == ErrorType.IMPORT_ERROR:
            analysis['potential_causes'].append('Missing dependency or package not installed')
            analysis['suggested_fixes'].append('Run: pip install <package_name>')
            analysis['suggested_fixes'].append('Check requirements.txt')

        elif error['type'] == ErrorType.CONFIGURATION_ERROR:
            analysis['potential_causes'].append('Invalid or missing configuration')
            analysis['suggested_fixes'].append('Verify config files in config/ directory')
            analysis['suggested_fixes'].append('Check .env file for missing variables')

        elif error['type'] == ErrorType.API_ERROR:
            analysis['potential_causes'].append('API endpoint unreachable or invalid credentials')
            analysis['suggested_fixes'].append('Verify API keys in .env file')
            analysis['suggested_fixes'].append('Check network connectivity')
            analysis['suggested_fixes'].append('Review API documentation')

        elif error['type'] == ErrorType.PERMISSION_ERROR:
            analysis['potential_causes'].append('Insufficient file or directory permissions')
            analysis['suggested_fixes'].append('Check file permissions: ls -la')
            analysis['suggested_fixes'].append('Grant appropriate permissions: chmod')

        # Find related errors (same source or type)
        related = [
            e for e in self.error_db['errors']
            if e['id'] != error_id and (
                e['source'] == error['source'] or e['type'] == error['type']
            )
        ]
        analysis['related_errors'] = [
            {'id': e['id'][:8], 'type': e['type'], 'message': e['message'][:50]}
            for e in related[:5]
        ]

        return analysis

    def _calculate_duration(self, error: Dict) -> str:
        """Calculate how long an error has been occurring"""
        first_seen = datetime.fromisoformat(error['first_seen'])
        last_seen = datetime.fromisoformat(error['last_seen'])
        duration = last_seen - first_seen

        if duration.total_seconds() < 60:
            return f"{int(duration.total_seconds())} seconds"
        elif duration.total_seconds() < 3600:
            return f"{int(duration.total_seconds() / 60)} minutes"
        elif duration.total_seconds() < 86400:
            return f"{int(duration.total_seconds() / 3600)} hours"
        else:
            return f"{duration.days} days"

    def mark_resolved(self, error_id: str, resolution: str) -> bool:
        """Mark an error as resolved"""
        error = self._find_existing_error(error_id)
        if not error:
            error = next((e for e in self.error_db['errors'] if e['id'] == error_id), None)

        if error:
            error['resolved'] = True
            error['resolution'] = resolution
            error['resolved_at'] = datetime.now().isoformat()
            self._save_error_database()
            logger.info(f"Error {error_id[:8]} marked as resolved: {resolution}")
            return True

        return False

    def get_active_errors(self, category: str = None, error_type: str = None) -> List[Dict]:
        """Get all active (unresolved) errors"""
        active = [e for e in self.error_db['errors'] if not e.get('resolved', False)]

        if category:
            active = [e for e in active if e['category'] == category]

        if error_type:
            active = [e for e in active if e['type'] == error_type]

        # Sort by severity and occurrences
        active.sort(
            key=lambda x: (self._severity_rank(x['category']), x.get('occurrences', 1)),
            reverse=True
        )

        return active

    def get_error_report(self) -> Dict[str, Any]:
        """Generate comprehensive error report"""
        active_errors = self.get_active_errors()

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_errors': len(self.error_db['errors']),
                'active_errors': len(active_errors),
                'resolved_errors': len([e for e in self.error_db['errors'] if e.get('resolved', False)]),
                'critical': len([e for e in active_errors if e['category'] == ErrorCategory.CRITICAL]),
                'errors': len([e for e in active_errors if e['category'] == ErrorCategory.ERROR]),
                'warnings': len([e for e in active_errors if e['category'] == ErrorCategory.WARNING])
            },
            'statistics': self.error_db['statistics'],
            'patterns': self.error_db.get('patterns', {}),
            'top_errors': []
        }

        # Get top errors by occurrence
        top_errors = sorted(active_errors, key=lambda x: x.get('occurrences', 1), reverse=True)[:10]
        report['top_errors'] = [
            {
                'id': e['id'][:8],
                'type': e['type'],
                'category': e['category'],
                'message': e['message'][:100],
                'occurrences': e.get('occurrences', 1),
                'source': e.get('source', 'unknown')
            }
            for e in top_errors
        ]

        return report

    def _send_alert(self, error_record: Dict) -> None:
        """Send alert for critical errors"""
        if not self.slack_webhook_url:
            logger.warning("Slack webhook URL not configured, skipping alert")
            return

        try:
            import requests

            alert_message = {
                'text': f"🚨 CRITICAL ERROR DETECTED",
                'blocks': [
                    {
                        'type': 'header',
                        'text': {
                            'type': 'plain_text',
                            'text': '🚨 Critical Error Alert'
                        }
                    },
                    {
                        'type': 'section',
                        'fields': [
                            {'type': 'mrkdwn', 'text': f"*Type:*\n{error_record['type']}"},
                            {'type': 'mrkdwn', 'text': f"*Category:*\n{error_record['category']}"},
                            {'type': 'mrkdwn', 'text': f"*Source:*\n{error_record.get('source', 'Unknown')}"},
                            {'type': 'mrkdwn', 'text': f"*Occurrences:*\n{error_record.get('occurrences', 1)}"}
                        ]
                    },
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f"*Message:*\n```{error_record['message'][:500]}```"
                        }
                    }
                ]
            }

            response = requests.post(
                self.slack_webhook_url,
                json=alert_message,
                timeout=10
            )

            if response.status_code == 200:
                logger.info("Alert sent to Slack successfully")
            else:
                logger.error(f"Failed to send Slack alert: {response.status_code}")

        except Exception as e:
            logger.error(f"Error sending alert: {e}")

    def _save_error_database(self) -> None:
        """Save error database to file"""
        try:
            # Ensure logs directory exists
            os.makedirs(os.path.dirname(self.error_db_path), exist_ok=True)

            self.error_db['last_updated'] = datetime.now().isoformat()

            with open(self.error_db_path, 'w') as f:
                json.dump(self.error_db, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save error database: {e}")

    def export_errors(self, output_file: str, format: str = 'json') -> None:
        """Export errors to file"""
        errors = self.get_active_errors()

        if format == 'json':
            with open(output_file, 'w') as f:
                json.dump(errors, f, indent=2)
        elif format == 'csv':
            import csv
            with open(output_file, 'w', newline='') as f:
                if errors:
                    writer = csv.DictWriter(f, fieldnames=errors[0].keys())
                    writer.writeheader()
                    writer.writerows(errors)

        logger.info(f"Exported {len(errors)} errors to {output_file}")


# Global error tracker instance
_global_tracker = None


def get_tracker() -> ErrorTracker:
    """Get global error tracker instance"""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ErrorTracker()
    return _global_tracker


def track_error(error: Exception, **kwargs) -> str:
    """Convenience function to track error using global tracker"""
    return get_tracker().track_error(error=error, **kwargs)


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Error Tracking System')
    parser.add_argument('--report', action='store_true', help='Generate error report')
    parser.add_argument('--analyze', type=str, help='Analyze error by ID')
    parser.add_argument('--export', type=str, help='Export errors to file')
    parser.add_argument('--format', type=str, default='json', choices=['json', 'csv'], help='Export format')
    parser.add_argument('--clear-resolved', action='store_true', help='Clear resolved errors')

    args = parser.parse_args()

    tracker = get_tracker()

    if args.report:
        report = tracker.get_error_report()
        print(json.dumps(report, indent=2))

    if args.analyze:
        analysis = tracker.analyze_root_cause(args.analyze)
        print(json.dumps(analysis, indent=2))

    if args.export:
        tracker.export_errors(args.export, format=args.format)

    if args.clear_resolved:
        tracker.error_db['errors'] = [e for e in tracker.error_db['errors'] if not e.get('resolved', False)]
        tracker._save_error_database()
        print("Cleared resolved errors")


if __name__ == '__main__':
    main()
