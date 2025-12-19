import re
from typing import List, Dict
from sqlalchemy import text

class PerformanceAgent:
    """Analyzes code for performance issues and optimization opportunities"""
    
    def __init__(self, engine):
        self.engine = engine
        
    def analyze(self, code: str, filename: str) -> List[Dict]:
        """
        Analyzes code for performance issues and optimization opportunities
        
        TODO: Future optimization - For large files:
        - Use incremental parsing (process sections)
        - Implement pattern caching
        - Add progress tracking for long analyses
        - Optimize regex patterns for large codebases
        """
        issues = []
        lines = code.split('\n')
        
        # TODO: Future optimization - Chunked processing for large files
        # LARGE_FILE_THRESHOLD = 5000
        # if len(lines) > LARGE_FILE_THRESHOLD:
        #     return self._analyze_chunked(code, filename)
        
        # Check for N+1 query patterns
        for line_num, line in enumerate(lines, 1):
            if 'for ' in line.lower():
                for offset in range(1, 5):
                    if line_num + offset <= len(lines):
                        next_line = lines[line_num + offset - 1]
                        if any(pattern in next_line.lower() for pattern in ['execute', 'query', 'select', 'fetch']):
                            issues.append({
                                'type': 'performance',
                                'issue': 'Potential N+1 query problem',
                                'line': line_num,
                                'code': line.strip(),
                                'severity': 'HIGH',
                                'fix': 'Move query outside loop or use batch query with JOIN'
                            })
                            break
        
        # Check for missing database indexes (heuristic)
        for line_num, line in enumerate(lines, 1):
            if 'where' in line.lower() and any(op in line.lower() for op in ['=', 'in', 'like']):
                if 'where id' not in line.lower() and 'execute' in line.lower():
                    issues.append({
                        'type': 'performance',
                        'issue': 'Query might benefit from index',
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'MEDIUM',
                        'fix': 'Consider adding database index on queried columns'
                    })
        
        # Check for SELECT * usage
        for line_num, line in enumerate(lines, 1):
            if re.search(r'select\s+\*\s+from', line, re.IGNORECASE):
                issues.append({
                    'type': 'performance',
                    'issue': 'SELECT * fetches unnecessary data',
                    'line': line_num,
                    'code': line.strip(),
                    'severity': 'MEDIUM',
                    'fix': 'Specify only needed columns instead of SELECT *'
                })
        
        # Check for nested loops (O(n²) complexity warning)
        indent_levels = []
        for line_num, line in enumerate(lines, 1):
            if 'for ' in line:
                indent = len(line) - len(line.lstrip())
                indent_levels.append((line_num, indent))
                
                for prev_line, prev_indent in indent_levels[:-1]:
                    if indent > prev_indent and line_num - prev_line < 20:
                        issues.append({
                            'type': 'performance',
                            'issue': 'Nested loop detected (O(n²) complexity)',
                            'line': line_num,
                            'code': line.strip(),
                            'severity': 'MEDIUM',
                            'fix': 'Consider using set/dict lookup or algorithm optimization'
                        })
                        break
        
        # Check for missing connection pooling patterns
        connection_opens = 0
        for line_num, line in enumerate(lines, 1):
            if 'connect(' in line.lower():
                connection_opens += 1
        
        if connection_opens > 1:
            issues.append({
                'type': 'performance',
                'issue': f'Multiple connection calls detected ({connection_opens})',
                'line': 1,
                'code': f'Found {connection_opens} separate connection calls',
                'severity': 'HIGH',
                'fix': 'Use connection pooling or context manager to reuse connections'
            })
        
        # Check for large data loading without pagination
        for line_num, line in enumerate(lines, 1):
            if re.search(r'fetchall\(\)', line, re.IGNORECASE):
                issues.append({
                    'type': 'performance',
                    'issue': 'fetchall() loads all rows into memory',
                    'line': line_num,
                    'code': line.strip(),
                    'severity': 'MEDIUM',
                    'fix': 'Use pagination (LIMIT/OFFSET) or fetchmany() for large datasets'
                })
        
        # Check for string concatenation in loops
        for line_num, line in enumerate(lines, 1):
            if '+=' in line and 'str' in line.lower():
                for check_line in range(max(0, line_num - 10), line_num):
                    if check_line < len(lines):
                        if 'for ' in lines[check_line - 1] or 'while ' in lines[check_line - 1]:
                            issues.append({
                                'type': 'performance',
                                'issue': 'String concatenation in loop',
                                'line': line_num,
                                'code': line.strip(),
                                'severity': 'LOW',
                                'fix': 'Use list.append() then "".join() for better performance'
                            })
                            break
        
        # Check for inefficient list operations
        for line_num, line in enumerate(lines, 1):
            if '.append(' in line:
                for check_line in range(max(0, line_num - 3), line_num):
                    if check_line < len(lines):
                        if 'for ' in lines[check_line - 1]:
                            issues.append({
                                'type': 'performance',
                                'issue': 'Consider list comprehension',
                                'line': line_num,
                                'code': line.strip(),
                                'severity': 'LOW',
                                'fix': 'List comprehensions are faster than append in loops'
                            })
                            break
        
        return issues
    
    def save_findings(self, issues: List[Dict], submission_id: int):
        """Save findings to database"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS performance_findings (
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
                    INSERT INTO performance_findings 
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
