import re
from typing import List, Dict
from sqlalchemy import text

class CodeQualityAgent:
    """Analyzes code quality and suggests improvements"""
    
    def __init__(self, engine):
        self.engine = engine
        
    def analyze(self, code: str, filename: str) -> List[Dict]:
        """Analyze code quality and return issues"""
        issues = []
        lines = code.split('\n')
        
        # Check for long functions
        in_function = False
        func_start = 0
        func_name = ""
        
        for line_num, line in enumerate(lines, 1):
            # Detect function start
            func_match = re.match(r'\s*def\s+(\w+)\s*\(', line)
            if func_match:
                in_function = True
                func_start = line_num
                func_name = func_match.group(1)
            
            # Detect function end (next function or end of indentation)
            elif in_function and line and not line[0].isspace() and line_num > func_start:
                func_length = line_num - func_start
                if func_length > 50:
                    issues.append({
                        'type': 'quality',
                        'issue': f'Long function: {func_name}()',
                        'line': func_start,
                        'code': f'Function is {func_length} lines long',
                        'severity': 'MEDIUM',
                        'fix': 'Break into smaller, focused functions'
                    })
                in_function = False
        
        # Check for long lines
        for line_num, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append({
                    'type': 'quality',
                    'issue': 'Line too long',
                    'line': line_num,
                    'code': line[:80] + '...',
                    'severity': 'LOW',
                    'fix': 'Break into multiple lines (PEP 8: max 79-120 chars)'
                })
        
        # Check for missing docstrings
        for line_num, line in enumerate(lines, 1):
            if re.match(r'\s*def\s+\w+\s*\(', line):
                # Check if next non-empty line is a docstring
                next_lines = lines[line_num:line_num+3]
                has_docstring = any('"""' in l or "'''" in l for l in next_lines)
                if not has_docstring:
                    issues.append({
                        'type': 'quality',
                        'issue': 'Missing docstring',
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'LOW',
                        'fix': 'Add docstring to explain function purpose'
                    })
        
        # Check for duplicate code (simplified)
        line_counts = {}
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if len(stripped) > 20 and not stripped.startswith('#'):
                if stripped in line_counts:
                    line_counts[stripped].append(line_num)
                else:
                    line_counts[stripped] = [line_num]
        
        for line_text, line_nums in line_counts.items():
            if len(line_nums) > 2:
                issues.append({
                    'type': 'quality',
                    'issue': 'Duplicate code detected',
                    'line': line_nums[0],
                    'code': f'Repeated {len(line_nums)} times: {line_text[:50]}...',
                    'severity': 'MEDIUM',
                    'fix': 'Extract into a reusable function'
                })
        
        return issues
    
    def save_findings(self, issues: List[Dict], submission_id: int):
        """Save findings to database"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS quality_findings (
                    id SERIAL PRIMARY KEY,
                    submission_id INTEGER,
                    issue_type TEXT,
                    line_number INTEGER,
                    severity TEXT,
                    description TEXT,
                    suggested_fix TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            for issue in issues:
                conn.execute(text("""
                    INSERT INTO quality_findings 
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
