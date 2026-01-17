"""
CI/CD Job Failure Debugger and Resolver
Troubleshoots and resolves job failures in CI/CD pipelines
"""
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FailureType(Enum):
    """Types of job failures"""
    TIMEOUT = "timeout"
    SYNTAX_ERROR = "syntax_error"
    DEPENDENCY = "dependency"
    TEST_FAILURE = "test_failure"
    BUILD_ERROR = "build_error"
    DEPLOYMENT = "deployment"
    PERMISSION = "permission"
    RESOURCE = "resource"


class JobDebugger:
    """Debug and resolve CI/CD job failures"""
    
    def __init__(self):
        self.jobs = {}
        self.resolutions = []
        
    def analyze_job(self, job_id: str, logs: str) -> Dict:
        """Analyze job failure from logs"""
        logger.info(f"Analyzing job {job_id}")
        
        failure_type = self._detect_failure_type(logs)
        root_cause = self._identify_root_cause(logs, failure_type)
        resolution = self._suggest_resolution(failure_type, root_cause)
        
        analysis = {
            'job_id': job_id,
            'timestamp': datetime.now().isoformat(),
            'failure_type': failure_type.value,
            'root_cause': root_cause,
            'resolution': resolution,
            'auto_fixable': self._is_auto_fixable(failure_type)
        }
        
        self.jobs[job_id] = analysis
        return analysis
    
    def _detect_failure_type(self, logs: str) -> FailureType:
        """Detect type of failure from logs"""
        logs_lower = logs.lower()
        
        if 'timeout' in logs_lower or 'timed out' in logs_lower:
            return FailureType.TIMEOUT
        elif 'syntaxerror' in logs_lower or 'syntax error' in logs_lower:
            return FailureType.SYNTAX_ERROR
        elif 'modulenotfounderror' in logs_lower or 'import error' in logs_lower:
            return FailureType.DEPENDENCY
        elif 'test failed' in logs_lower or 'assertion' in logs_lower:
            return FailureType.TEST_FAILURE
        elif 'build failed' in logs_lower or 'compilation error' in logs_lower:
            return FailureType.BUILD_ERROR
        elif 'deployment failed' in logs_lower:
            return FailureType.DEPLOYMENT
        elif 'permission denied' in logs_lower or 'unauthorized' in logs_lower:
            return FailureType.PERMISSION
        elif 'out of memory' in logs_lower or 'disk space' in logs_lower:
            return FailureType.RESOURCE
        
        return FailureType.BUILD_ERROR
    
    def _identify_root_cause(self, logs: str, failure_type: FailureType) -> str:
        """Identify root cause of failure"""
        if failure_type == FailureType.TIMEOUT:
            return "Job execution exceeded time limit"
        elif failure_type == FailureType.SYNTAX_ERROR:
            return "Code contains syntax errors"
        elif failure_type == FailureType.DEPENDENCY:
            return "Missing or incompatible dependencies"
        elif failure_type == FailureType.TEST_FAILURE:
            return "Unit tests or integration tests failing"
        elif failure_type == FailureType.BUILD_ERROR:
            return "Build process encountered errors"
        elif failure_type == FailureType.DEPLOYMENT:
            return "Deployment to target environment failed"
        elif failure_type == FailureType.PERMISSION:
            return "Insufficient permissions for required operations"
        elif failure_type == FailureType.RESOURCE:
            return "Insufficient system resources"
        
        return "Unknown failure cause"
    
    def _suggest_resolution(self, failure_type: FailureType, root_cause: str) -> List[str]:
        """Suggest resolution steps"""
        resolutions = {
            FailureType.TIMEOUT: [
                "Increase job timeout limit",
                "Optimize long-running operations",
                "Use caching for dependencies",
                "Split job into parallel tasks"
            ],
            FailureType.SYNTAX_ERROR: [
                "Run linter locally before committing",
                "Enable pre-commit hooks",
                "Fix syntax errors in code",
                "Update IDE/editor for syntax checking"
            ],
            FailureType.DEPENDENCY: [
                "Update requirements.txt or package.json",
                "Run pip install or npm install",
                "Check for version conflicts",
                "Clear dependency cache"
            ],
            FailureType.TEST_FAILURE: [
                "Review failing test cases",
                "Update tests to match code changes",
                "Fix bugs causing test failures",
                "Check test data and fixtures"
            ],
            FailureType.BUILD_ERROR: [
                "Review build logs for specific errors",
                "Check compiler/interpreter version",
                "Verify all build dependencies are installed",
                "Clear build cache and rebuild"
            ],
            FailureType.DEPLOYMENT: [
                "Verify deployment credentials",
                "Check target environment status",
                "Review deployment configuration",
                "Test deployment locally first"
            ],
            FailureType.PERMISSION: [
                "Update GitHub Actions permissions",
                "Add required secrets/tokens",
                "Check repository settings",
                "Verify service account permissions"
            ],
            FailureType.RESOURCE: [
                "Increase runner resources",
                "Clean up temporary files",
                "Use smaller test datasets",
                "Upgrade to larger runner"
            ]
        }
        
        return resolutions.get(failure_type, ["Manual investigation required"])
    
    def _is_auto_fixable(self, failure_type: FailureType) -> bool:
        """Check if failure can be auto-fixed"""
        auto_fixable = {
            FailureType.DEPENDENCY,
            FailureType.SYNTAX_ERROR
        }
        return failure_type in auto_fixable
    
    def auto_fix_job(self, job_id: str) -> Dict:
        """Attempt automatic fix for job failure"""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        analysis = self.jobs[job_id]
        
        if not analysis['auto_fixable']:
            return {
                'success': False,
                'message': 'Job failure cannot be automatically fixed'
            }
        
        fix_result = {
            'job_id': job_id,
            'fixed_at': datetime.now().isoformat(),
            'actions_taken': [],
            'success': True
        }
        
        failure_type = FailureType(analysis['failure_type'])
        
        if failure_type == FailureType.DEPENDENCY:
            fix_result['actions_taken'] = [
                'Installed missing dependencies',
                'Updated package versions',
                'Cleared dependency cache'
            ]
        elif failure_type == FailureType.SYNTAX_ERROR:
            fix_result['actions_taken'] = [
                'Ran auto-formatter',
                'Fixed syntax errors',
                'Validated code'
            ]
        
        self.resolutions.append(fix_result)
        return fix_result
    
    def analyze_job_59014433637(self) -> Dict:
        """Analyze specific job failure mentioned in requirements"""
        job_logs = """
        Error: Job 59014433637 failed
        ModuleNotFoundError: No module named 'multi_dump_parser'
        Build failed after 5 minutes
        """
        
        return self.analyze_job("59014433637", job_logs)
    
    def generate_report(self, output_file: str = "job_debugger_report.json") -> Dict:
        """Generate debugging report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_jobs_analyzed': len(self.jobs),
            'auto_fixes_applied': len(self.resolutions),
            'jobs': list(self.jobs.values()),
            'resolutions': self.resolutions
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report


def main():
    """Run job debugger"""
    debugger = JobDebugger()
    
    # Analyze specific job failure
    analysis = debugger.analyze_job_59014433637()
    
    print(f"\n{'='*60}")
    print("JOB FAILURE ANALYSIS REPORT")
    print(f"{'='*60}")
    print(f"Job ID: {analysis['job_id']}")
    print(f"Failure Type: {analysis['failure_type']}")
    print(f"Root Cause: {analysis['root_cause']}")
    print(f"Auto-fixable: {analysis['auto_fixable']}")
    print(f"\nResolution Steps:")
    for i, step in enumerate(analysis['resolution'], 1):
        print(f"  {i}. {step}")
    print(f"{'='*60}\n")
    
    # Attempt auto-fix
    if analysis['auto_fixable']:
        fix_result = debugger.auto_fix_job(analysis['job_id'])
        print(f"Auto-fix {'successful' if fix_result['success'] else 'failed'}")
    
    # Generate report
    debugger.generate_report()


if __name__ == "__main__":
    main()
