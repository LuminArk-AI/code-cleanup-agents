from sqlalchemy import text, create_engine
from agents.security_scanner import SecurityScanner
from agents.code_quality import CodeQualityAgent
from agents.performance_analyzer import PerformanceAgent
from agents.best_practices import BestPracticesAgent
from concurrent.futures import ThreadPoolExecutor
import os

class Coordinator:
    """Coordinates multiple agents to analyze code"""
    
    def __init__(self, main_engine):
        self.main_engine = main_engine
        
    def analyze_code(self, code: str, filename: str):
        """
        Coordinate analysis across multiple agents in parallel using forks
        
        TODO: Future optimization - Add support for large file handling:
        - Chunked processing for files > 5000 lines
        - Streaming analysis for very large files
        - Progress tracking for long-running analyses
        - Memory-efficient processing
        """
        print(f"\n{'='*60}")
        print(f"🎯 Starting multi-agent analysis of {filename}...")
        print(f"{'='*60}")
        
        # TODO: Future optimization - Calculate file metrics before processing
        # file_size = len(code)
        # line_count = code.count('\n')
        # is_large_file = line_count > 5000  # Threshold for chunked processing
        
        # TODO: Future optimization - For large files, use chunked storage or external storage
        # if is_large_file:
        #     # Store file reference instead of full content
        #     # Use external storage (S3, etc.) for very large files
        #     pass
        
        # Save code submission to main DB
        # TODO: Future optimization - For large files, consider:
        # - Storing only file hash and metadata
        # - Using external storage for code content
        # - Implementing compression for stored code
        with self.main_engine.connect() as conn:
            result = conn.execute(text("""
                INSERT INTO code_submissions (filename, code_content)
                VALUES (:filename, :code)
                RETURNING id
            """), {'filename': filename, 'code': code})
            submission_id = result.fetchone()[0]
            conn.commit()
        
        print(f"📝 Saved submission #{submission_id} to main database")
        
        # Get fork connection strings
        security_fork_url = os.getenv('SECURITY_FORK_URL')
        quality_fork_url = os.getenv('QUALITY_FORK_URL')
        performance_fork_url = os.getenv('PERFORMANCE_FORK_URL')
        best_practices_fork_url = os.getenv('BEST_PRACTICES_FORK_URL')
        
        # Use forks if configured
        if security_fork_url and quality_fork_url:
            print(f"\n{'='*60}")
            print("🔀 USING DATABASE FORKS FOR PARALLEL EXECUTION!")
            print(f"{'='*60}")
            print(f"🔒 Security Agent → security_fork-db-60626")
            print(f"✨ Quality Agent → quality_fork-db-60626")
            
            if performance_fork_url:
                print(f"⚡ Performance Agent → performance_fork-db-60626")
            else:
                print(f"⚡ Performance Agent → main-db-60626 (no fork configured)")
                performance_fork_url = os.getenv('DATABASE_URL')
            
            if best_practices_fork_url:
                print(f"📋 Best Practices Agent → best_practices_fork-db-60626")
            else:
                print(f"📋 Best Practices Agent → main-db-60626 (no fork configured)")
                best_practices_fork_url = os.getenv('DATABASE_URL')
            
            print(f"{'='*60}\n")
            
            # Convert to postgresql+psycopg:// for psycopg3 (Python 3.13 compatible)
            def convert_to_psycopg3(url):
                if url.startswith('postgres://'):
                    return url.replace('postgres://', 'postgresql+psycopg://', 1)
                elif url.startswith('postgresql://') and '+psycopg' not in url:
                    return url.replace('postgresql://', 'postgresql+psycopg://', 1)
                return url
            
            security_fork_url = convert_to_psycopg3(security_fork_url)
            quality_fork_url = convert_to_psycopg3(quality_fork_url)
            if performance_fork_url:
                performance_fork_url = convert_to_psycopg3(performance_fork_url)
            if best_practices_fork_url:
                best_practices_fork_url = convert_to_psycopg3(best_practices_fork_url)
            
            # Create engines for forks
            security_engine = create_engine(security_fork_url)
            quality_engine = create_engine(quality_fork_url)
            performance_engine = create_engine(performance_fork_url)
            best_practices_engine = create_engine(best_practices_fork_url)
            
            # Run agents in parallel
            # TODO: Future optimization - For large files, consider:
            # - Dynamic worker allocation based on file size
            # - Chunked agent processing (process file in chunks per agent)
            # - Progress callbacks for long-running analyses
            with ThreadPoolExecutor(max_workers=4) as executor:
                print("🔒 Security Agent working...")
                security_future = executor.submit(
                    self._run_security_agent, 
                    security_engine, 
                    code, 
                    filename, 
                    submission_id
                )
                
                print("✨ Quality Agent working...")
                quality_future = executor.submit(
                    self._run_quality_agent, 
                    quality_engine, 
                    code, 
                    filename, 
                    submission_id
                )
                
                print("⚡ Performance Agent working...")
                performance_future = executor.submit(
                    self._run_performance_agent,
                    performance_engine,
                    code,
                    filename,
                    submission_id
                )
                
                print("📋 Best Practices Agent working...")
                best_practices_future = executor.submit(
                    self._run_best_practices_agent,
                    best_practices_engine,
                    code,
                    filename,
                    submission_id
                )
                
                # Wait for all agents to complete
                security_count, security_issues = security_future.result()
                quality_count, quality_issues = quality_future.result()
                performance_count, performance_issues = performance_future.result()
                best_practices_count, best_practices_issues = best_practices_future.result()
            
            print(f"\n{'='*60}")
            print("✅ ALL FOUR AGENTS COMPLETED IN PARALLEL!")
            print(f"{'='*60}")
            
        else:
            print("\n⚠️  Fork URLs not fully configured, running on main DB sequentially...")
            
            # Fallback: Run on main DB
            security_agent = SecurityScanner(self.main_engine)
            security_issues = security_agent.scan(code, filename)
            security_count = security_agent.save_findings(security_issues, submission_id)
            
            quality_agent = CodeQualityAgent(self.main_engine)
            quality_issues = quality_agent.analyze(code, filename)
            quality_count = quality_agent.save_findings(quality_issues, submission_id)
            
            performance_agent = PerformanceAgent(self.main_engine)
            performance_issues = performance_agent.analyze(code, filename)
            performance_count = performance_agent.save_findings(performance_issues, submission_id)
            
            best_practices_agent = BestPracticesAgent(self.main_engine)
            best_practices_issues = best_practices_agent.analyze(code, filename)
            best_practices_count = best_practices_agent.save_findings(best_practices_issues, submission_id)
        
        # Merge results back to main DB
        print("🔄 Merging findings from all agents to main database...")
        self._merge_findings_to_main(submission_id, security_issues, quality_issues, performance_issues, best_practices_issues)
        
        # Compile results
        results = {
            'submission_id': submission_id,
            'filename': filename,
            'security': {
                'count': security_count,
                'issues': security_issues
            },
            'quality': {
                'count': quality_count,
                'issues': quality_issues
            },
            'performance': {
                'count': performance_count,
                'issues': performance_issues
            },
            'best_practices': {
                'count': best_practices_count,
                'issues': best_practices_issues
            },
            'total_issues': security_count + quality_count + performance_count + best_practices_count
        }
        
        print(f"\n{'='*60}")
        print(f"✅ Analysis complete! Found {results['total_issues']} total issues")
        print(f"   🔒 Security: {security_count}")
        print(f"   ✨ Quality: {quality_count}")
        print(f"   ⚡ Performance: {performance_count}")
        print(f"   📋 Best Practices: {best_practices_count}")
        print(f"{'='*60}\n")
        
        return results
    
    def _run_security_agent(self, fork_engine, code, filename, submission_id):
        """Run security agent on its dedicated fork"""
        agent = SecurityScanner(fork_engine)
        issues = agent.scan(code, filename)
        count = agent.save_findings(issues, submission_id)
        print(f"   🔒 Security Agent completed - Found {count} issues")
        return count, issues
    
    def _run_quality_agent(self, fork_engine, code, filename, submission_id):
        """Run quality agent on its dedicated fork"""
        agent = CodeQualityAgent(fork_engine)
        issues = agent.analyze(code, filename)
        count = agent.save_findings(issues, submission_id)
        print(f"   ✨ Quality Agent completed - Found {count} issues")
        return count, issues
    
    def _run_performance_agent(self, fork_engine, code, filename, submission_id):
        """Run performance agent on its dedicated fork"""
        agent = PerformanceAgent(fork_engine)
        issues = agent.analyze(code, filename)
        count = agent.save_findings(issues, submission_id)
        print(f"   ⚡ Performance Agent completed - Found {count} issues")
        return count, issues
    
    def _run_best_practices_agent(self, fork_engine, code, filename, submission_id):
        """Run best practices agent on its dedicated fork"""
        agent = BestPracticesAgent(fork_engine)
        issues = agent.analyze(code, filename)
        count = agent.save_findings(issues, submission_id)
        print(f"   📋 Best Practices Agent completed - Found {count} issues")
        return count, issues
    
    def _merge_findings_to_main(self, submission_id, security_issues, quality_issues, performance_issues, best_practices_issues):
        """Merge findings from forks back to main database"""
        with self.main_engine.connect() as conn:
            # Create merged_findings table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS merged_findings (
                    id SERIAL PRIMARY KEY,
                    submission_id INTEGER,
                    agent_type TEXT,
                    issue_type TEXT,
                    line_number INTEGER,
                    severity TEXT,
                    description TEXT,
                    suggested_fix TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Merge security findings
            for issue in security_issues:
                conn.execute(text("""
                    INSERT INTO merged_findings 
                    (submission_id, agent_type, issue_type, line_number, severity, description, suggested_fix)
                    VALUES (:sub_id, 'security', :issue, :line, :severity, :desc, :fix)
                """), {
                    'sub_id': submission_id,
                    'issue': issue['issue'],
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'desc': issue['code'],
                    'fix': issue['fix']
                })
            
            # Merge quality findings
            for issue in quality_issues:
                conn.execute(text("""
                    INSERT INTO merged_findings 
                    (submission_id, agent_type, issue_type, line_number, severity, description, suggested_fix)
                    VALUES (:sub_id, 'quality', :issue, :line, :severity, :desc, :fix)
                """), {
                    'sub_id': submission_id,
                    'issue': issue['issue'],
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'desc': issue['code'],
                    'fix': issue['fix']
                })
            
            # Merge performance findings
            for issue in performance_issues:
                conn.execute(text("""
                    INSERT INTO merged_findings 
                    (submission_id, agent_type, issue_type, line_number, severity, description, suggested_fix)
                    VALUES (:sub_id, 'performance', :issue, :line, :severity, :desc, :fix)
                """), {
                    'sub_id': submission_id,
                    'issue': issue['issue'],
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'desc': issue['code'],
                    'fix': issue['fix']
                })
            
            # Merge best practices findings
            for issue in best_practices_issues:
                conn.execute(text("""
                    INSERT INTO merged_findings 
                    (submission_id, agent_type, issue_type, line_number, severity, description, suggested_fix)
                    VALUES (:sub_id, 'best_practices', :issue, :line, :severity, :desc, :fix)
                """), {
                    'sub_id': submission_id,
                    'issue': issue['issue'],
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'desc': issue['code'],
                    'fix': issue['fix']
                })
            
            conn.commit()
        
        print(f"   ✅ Merged all findings to main database")