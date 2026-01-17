"""
Path Traversal Vulnerability Scanner and Remediation System
Scans codebase for path traversal vulnerabilities and provides automatic fixes
"""
import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PathTraversalScanner:
    """Detects and fixes path traversal vulnerabilities"""
    
    VULNERABLE_PATTERNS = [
        # Direct path operations without validation
        (r'open\(["\']?([^"\']+)["\']?\s*,?\s*["\']?[rwa]', 'File open without path validation'),
        (r'os\.path\.join\([^)]*\.\.[^)]*\)', 'Potential path traversal with ..'),
        (r'Path\([^)]*\.\.[^)]*\)', 'Path object with potential traversal'),
        (r'with\s+open\([^)]*user_input[^)]*\)', 'User input in file operations'),
        (r'\.\./', 'Hardcoded path traversal sequence'),
        (r'\.\.[/\\]', 'Path traversal pattern'),
        (r'os\.system\([^)]*\+[^)]*\)', 'Command injection via path'),
        (r'subprocess\.(call|run|Popen)\([^)]*\+[^)]*\)', 'Subprocess with concatenated paths'),
    ]
    
    SAFE_PATTERNS = [
        'os.path.abspath',
        'os.path.realpath',
        'Path.resolve()',
        'secure_filename',
        'validate_path',
    ]
    
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.vulnerabilities = []
        self.fixed_files = []
        
    def scan_directory(self, extensions: List[str] = None) -> List[Dict]:
        """Scan directory for path traversal vulnerabilities"""
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.php', '.rb']
        
        logger.info(f"Scanning {self.root_dir} for path traversal vulnerabilities...")
        
        for ext in extensions:
            for file_path in self.root_dir.rglob(f'*{ext}'):
                if self._should_skip_file(file_path):
                    continue
                self._scan_file(file_path)
        
        logger.info(f"Found {len(self.vulnerabilities)} potential vulnerabilities")
        return self.vulnerabilities
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Skip test files, node_modules, venv, etc."""
        skip_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.pytest_cache', 'test-results'}
        return any(skip_dir in file_path.parts for skip_dir in skip_dirs)
    
    def _scan_file(self, file_path: Path):
        """Scan individual file for vulnerabilities"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            for line_num, line in enumerate(lines, 1):
                # Skip if line uses safe patterns
                if any(safe in line for safe in self.SAFE_PATTERNS):
                    continue
                
                # Check for vulnerable patterns
                for pattern, description in self.VULNERABLE_PATTERNS:
                    if re.search(pattern, line):
                        self.vulnerabilities.append({
                            'file': str(file_path),
                            'line': line_num,
                            'code': line.strip(),
                            'vulnerability': description,
                            'severity': self._assess_severity(line, pattern),
                            'timestamp': datetime.now().isoformat()
                        })
        except Exception as e:
            logger.warning(f"Error scanning {file_path}: {e}")
    
    def _assess_severity(self, line: str, pattern: str) -> str:
        """Assess vulnerability severity"""
        if 'user_input' in line.lower() or 'request' in line.lower():
            return 'CRITICAL'
        elif '..' in line:
            return 'HIGH'
        elif 'os.system' in line or 'subprocess' in line:
            return 'HIGH'
        return 'MEDIUM'
    
    def generate_report(self, output_file: str = None) -> Dict:
        """Generate vulnerability report"""
        report = {
            'scan_date': datetime.now().isoformat(),
            'root_directory': str(self.root_dir),
            'total_vulnerabilities': len(self.vulnerabilities),
            'severity_breakdown': self._count_by_severity(),
            'vulnerabilities': self.vulnerabilities,
            'recommendations': self._generate_recommendations()
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def _count_by_severity(self) -> Dict[str, int]:
        """Count vulnerabilities by severity"""
        counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        for vuln in self.vulnerabilities:
            counts[vuln['severity']] = counts.get(vuln['severity'], 0) + 1
        return counts
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations"""
        return [
            "1. Always validate and sanitize file paths before use",
            "2. Use os.path.abspath() and os.path.realpath() to resolve paths",
            "3. Implement allowlist-based path validation",
            "4. Never concatenate user input directly into file paths",
            "5. Use secure_filename() for user-provided filenames",
            "6. Restrict file operations to specific directories",
            "7. Implement proper error handling for file operations",
            "8. Use Path.resolve() for modern Python path handling"
        ]
    
    def auto_fix_vulnerabilities(self, backup: bool = True) -> List[str]:
        """Attempt automatic fixes for common vulnerabilities"""
        logger.info("Starting automatic vulnerability remediation...")
        
        file_groups = {}
        for vuln in self.vulnerabilities:
            file_path = vuln['file']
            if file_path not in file_groups:
                file_groups[file_path] = []
            file_groups[file_path].append(vuln)
        
        for file_path, vulns in file_groups.items():
            if self._fix_file(file_path, vulns, backup):
                self.fixed_files.append(file_path)
        
        logger.info(f"Fixed {len(self.fixed_files)} files")
        return self.fixed_files
    
    def _fix_file(self, file_path: str, vulnerabilities: List[Dict], backup: bool) -> bool:
        """Fix vulnerabilities in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if backup:
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Apply fixes
            fixed_content = self._apply_fixes(content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info(f"Fixed {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to fix {file_path}: {e}")
            return False
    
    def _apply_fixes(self, content: str) -> str:
        """Apply security fixes to content"""
        # Add path validation helper if not present
        if 'def validate_path' not in content:
            validation_code = '''
import os
from pathlib import Path

def validate_path(user_path: str, base_dir: str) -> str:
    """Validate and sanitize file path to prevent traversal"""
    # Resolve to absolute path
    abs_base = os.path.abspath(base_dir)
    abs_user = os.path.abspath(os.path.join(abs_base, user_path))
    
    # Ensure path is within base directory
    if not abs_user.startswith(abs_base):
        raise ValueError("Path traversal detected")
    
    return abs_user

'''
            content = validation_code + content
        
        # Replace unsafe patterns with safe alternatives
        fixes = [
            (r'open\(([^)]+)\)', r'open(validate_path(\1, BASE_DIR))'),
            (r'Path\(([^)]+)\)\.open', r'Path(validate_path(\1, BASE_DIR)).open'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        return content


def main():
    """Run path traversal scanner"""
    scanner = PathTraversalScanner('/home/runner/work/Private-Claude/Private-Claude')
    
    # Scan for vulnerabilities
    vulnerabilities = scanner.scan_directory()
    
    # Generate report
    report = scanner.generate_report('security_scan_report.json')
    
    # Print summary
    print(f"\n{'='*60}")
    print("PATH TRAVERSAL VULNERABILITY SCAN REPORT")
    print(f"{'='*60}")
    print(f"Total Vulnerabilities Found: {report['total_vulnerabilities']}")
    print(f"\nSeverity Breakdown:")
    for severity, count in report['severity_breakdown'].items():
        print(f"  {severity}: {count}")
    print(f"\n{'='*60}\n")
    
    return report


if __name__ == "__main__":
    main()
