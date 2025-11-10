import re
from typing import List, Dict
from sqlalchemy import text

class SecurityScanner:
    """Scans code for common security vulnerabilities"""
    
    def __init__(self, engine):
        self.engine = engine
        
    def scan(self, code: str, filename: str) -> List[Dict]:
        """Scan code and return list of security issues"""
        issues = []
        
        # Check for hardcoded secrets
        secret_patterns = [
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Hardcoded API key'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'Hardcoded token'),
            (r'aws[_-]?access[_-]?key', 'AWS credentials'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, issue_type in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'type': 'security',
                        'issue': issue_type,
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'HIGH',
                        'fix': 'Use environment variables or secret management system'
                    })
        
        # Check for SQL injection vulnerabilities
        sql_patterns = [
            (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', 'SQL injection via f-string'),
            (r'execute\s*\(\s*["\'].*%s.*["\'].*%', 'SQL injection via string formatting'),
            (r'execute\s*\(\s*.+\s*\+\s*.+\)', 'SQL injection via concatenation'),
            (r'cursor\.execute\s*\([^,]+\+', 'SQL injection in cursor.execute'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, issue_type in sql_patterns:
                if re.search(pattern, line):
                    issues.append({
                        'type': 'security',
                        'issue': issue_type,
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'CRITICAL',
                        'fix': 'Use parameterized queries with placeholders'
                    })
        
        # Check for eval/exec usage
        dangerous_funcs = ['eval', 'exec', '__import__']
        for line_num, line in enumerate(code.split('\n'), 1):
            for func in dangerous_funcs:
                if re.search(rf'\b{func}\s*\(', line):
                    issues.append({
                        'type': 'security',
                        'issue': f'Dangerous function: {func}()',
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'HIGH',
                        'fix': f'Avoid using {func}() - find safer alternatives'
                    })
        
        return issues
    
    def save_findings(self, issues: List[Dict], submission_id: int):
        """Save findings to the database"""
        with self.engine.connect() as conn:
            for issue in issues:
                conn.execute(text("""
                    INSERT INTO security_findings 
                    (submission_id, issue_type, line_number, severity, description, suggested_fix)
                    VALUES (:sub_id, :issue, :line, :severity, :desc, :fix)
                """), {
                    'sub_id': submission_id,
                    'issue': issue['issue'],
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'desc': issue['code'],
                    'fix': issue['fix']
                })
            conn.commit()
        
        return len(issues)