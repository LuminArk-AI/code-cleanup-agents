import re
from typing import List, Dict
from sqlalchemy import text


class BestPracticesAgent:
    """Analyzes code against language-specific best practices and coding standards"""
    
    def __init__(self, engine):
        self.engine = engine
        
    def analyze(self, code: str, filename: str) -> List[Dict]:
        """Analyze code for best practice violations"""
        issues = []
        lines = code.split('\n')
        
        # Detect language
        language = self._detect_language(filename)
        
        # Python-specific best practices
        if language == 'python':
            issues.extend(self._check_python_best_practices(lines))
        
        # General best practices (all languages)
        issues.extend(self._check_general_best_practices(lines, code))
        
        return issues
    
    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename"""
        ext = filename.split('.')[-1].lower()
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'java': 'java',
            'go': 'go',
            'rb': 'ruby',
            'cpp': 'cpp',
            'c': 'c'
        }
        return lang_map.get(ext, 'unknown')
    
    def _check_python_best_practices(self, lines: List[str]) -> List[Dict]:
        """Check Python-specific best practices"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Check for print statements (use logging instead)
            if 'print(' in stripped and not stripped.startswith('#'):
                if 'debug' not in stripped.lower() and '__main__' not in ''.join(lines):
                    issues.append({
                        'type': 'best_practices',
                        'issue': 'Print statement in production code',
                        'line': line_num,
                        'code': stripped,
                        'severity': 'LOW',
                        'fix': 'Use logging module instead of print() for production code'
                    })
            
            # Check for bare except clauses
            if re.match(r'\s*except\s*:', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Bare except clause catches all exceptions',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'MEDIUM',
                    'fix': 'Specify exception types (e.g., except ValueError:) or use except Exception:'
                })
            
            # Check for mutable default arguments
            if 'def ' in stripped and '=' in stripped:
                if re.search(r'=\s*\[\s*\]|=\s*\{\s*\}', stripped):
                    issues.append({
                        'type': 'best_practices',
                        'issue': 'Mutable default argument',
                        'line': line_num,
                        'code': stripped,
                        'severity': 'HIGH',
                        'fix': 'Use None as default and initialize inside function: def func(arg=None): arg = arg or []'
                    })
            
            # Check for pass statements that could be replaced
            if stripped == 'pass' and line_num > 1:
                prev_line = lines[line_num - 2].strip() if line_num > 1 else ''
                if 'except' not in prev_line and 'class' not in prev_line:
                    issues.append({
                        'type': 'best_practices',
                        'issue': 'Unnecessary pass statement',
                        'line': line_num,
                        'code': stripped,
                        'severity': 'LOW',
                        'fix': 'Consider removing or adding a comment explaining why it\'s empty'
                    })
            
            # Check for lambda assignments (use def instead)
            if re.search(r'^\s*\w+\s*=\s*lambda\s', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Lambda assignment should be a function',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'MEDIUM',
                    'fix': 'Use def instead of assigning lambda to a variable'
                })
            
            # Check for type() comparisons (use isinstance instead)
            if re.search(r'type\s*\([^)]+\)\s*==', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Using type() for type checking',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'MEDIUM',
                    'fix': 'Use isinstance() instead of type() == for type checking'
                })
            
            # Check for == True or == False comparisons
            if re.search(r'==\s*(True|False)\b', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Explicit boolean comparison',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'LOW',
                    'fix': 'Use "if variable:" instead of "if variable == True:"'
                })
            
            # Check for len() in conditionals
            if re.search(r'if\s+len\s*\([^)]+\)\s*[><=]', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Using len() in conditional',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'LOW',
                    'fix': 'Use "if collection:" instead of "if len(collection) > 0:"'
                })
            
            # Check for import * (wildcard imports)
            if re.search(r'from\s+\w+\s+import\s+\*', stripped):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Wildcard import',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'MEDIUM',
                    'fix': 'Import specific items or use "import module" instead of "from module import *"'
                })
            
            # Check for multiple statements on one line
            if ';' in stripped and not stripped.startswith('#'):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Multiple statements on one line',
                    'line': line_num,
                    'code': stripped,
                    'severity': 'LOW',
                    'fix': 'Put each statement on its own line for better readability'
                })
        
        return issues
    
    def _check_general_best_practices(self, lines: List[str], code: str) -> List[Dict]:
        """Check general best practices applicable to all languages"""
        issues = []
        
        # Check for TODO/FIXME comments
        for line_num, line in enumerate(lines, 1):
            if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line, re.IGNORECASE):
                issues.append({
                    'type': 'best_practices',
                    'issue': 'TODO/FIXME comment found',
                    'line': line_num,
                    'code': line.strip(),
                    'severity': 'LOW',
                    'fix': 'Address the TODO or create a tracked issue for it'
                })
        
        # Check for magic numbers (hardcoded numbers that aren't 0, 1, -1)
        for line_num, line in enumerate(lines, 1):
            # Skip comments and strings
            if '#' in line:
                line = line.split('#')[0]
            
            # Find numeric literals that aren't 0, 1, -1, or in common patterns
            if re.search(r'\b(?!0\b|1\b|-1\b)\d{2,}\b', line):
                if 'range' not in line and 'sleep' not in line:
                    issues.append({
                        'type': 'best_practices',
                        'issue': 'Magic number detected',
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'LOW',
                        'fix': 'Define magic numbers as named constants for better maintainability'
                    })
        
        # Check for excessive nesting (more than 4 levels)
        max_indent = 0
        for line_num, line in enumerate(lines, 1):
            if line.strip():
                indent_level = (len(line) - len(line.lstrip())) // 4
                if indent_level > max_indent:
                    max_indent = indent_level
                
                if indent_level > 4:
                    issues.append({
                        'type': 'best_practices',
                        'issue': f'Deeply nested code ({indent_level} levels)',
                        'line': line_num,
                        'code': line.strip(),
                        'severity': 'MEDIUM',
                        'fix': 'Refactor to reduce nesting (extract methods, use early returns)'
                    })
                    break  # Only report once
        
        # Check for commented-out code
        comment_block_size = 0
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('#') and len(line.strip()) > 3:
                # Check if it looks like commented code (has operators, keywords, etc.)
                if re.search(r'[=+\-*/\(\){}[\]]|def |class |import |if |for |while ', line):
                    comment_block_size += 1
                else:
                    comment_block_size = 0
            else:
                comment_block_size = 0
            
            if comment_block_size >= 3:
                issues.append({
                    'type': 'best_practices',
                    'issue': 'Large block of commented-out code',
                    'line': line_num - 2,
                    'code': 'Multiple lines of commented code',
                    'severity': 'LOW',
                    'fix': 'Remove commented code (use version control instead)'
                })
                break  # Only report once
        
        # Check for inconsistent naming (mixing camelCase and snake_case)
        camel_case_count = len(re.findall(r'\b[a-z]+[A-Z][a-zA-Z]*\b', code))
        snake_case_count = len(re.findall(r'\b[a-z]+_[a-z]+\b', code))
        
        if camel_case_count > 0 and snake_case_count > 0 and min(camel_case_count, snake_case_count) > 3:
            issues.append({
                'type': 'best_practices',
                'issue': 'Inconsistent naming convention',
                'line': 1,
                'code': f'Mixed camelCase ({camel_case_count}) and snake_case ({snake_case_count})',
                'severity': 'LOW',
                'fix': 'Use consistent naming convention throughout (Python: snake_case)'
            })
        
        # Check for very long functions (already caught by quality agent, but with different threshold)
        function_lengths = {}
        current_function = None
        function_start = 0
        
        for line_num, line in enumerate(lines, 1):
            if re.match(r'\s*def\s+(\w+)', line):
                if current_function:
                    function_lengths[current_function] = line_num - function_start
                
                match = re.match(r'\s*def\s+(\w+)', line)
                current_function = match.group(1)
                function_start = line_num
            elif current_function and line and not line[0].isspace() and 'def ' not in line:
                function_lengths[current_function] = line_num - function_start
                current_function = None
        
        for func_name, length in function_lengths.items():
            if length > 100:
                issues.append({
                    'type': 'best_practices',
                    'issue': f'Function "{func_name}" is very long ({length} lines)',
                    'line': 1,
                    'code': f'Function exceeds 100 lines',
                    'severity': 'MEDIUM',
                    'fix': 'Break down into smaller, focused functions following Single Responsibility Principle'
                })
        
        return issues
    
    def save_findings(self, issues: List[Dict], submission_id: int):
        """Save findings to database"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS best_practices_findings (
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
                    INSERT INTO best_practices_findings 
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

