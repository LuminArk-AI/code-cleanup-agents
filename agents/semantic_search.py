from sqlalchemy import text
from typing import List, Dict


class SemanticSearch:
    """Semantic code search using PostgreSQL pg_trgm for fuzzy matching"""
    
    def __init__(self, engine):
        self.engine = engine
        self._setup_extension()
    
    def _setup_extension(self):
        """Enable pg_trgm extension and create indexes"""
        with self.engine.connect() as conn:
            try:
                # Enable pg_trgm extension
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
                
                # Create trigram index on code content for fast similarity search
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS code_content_trgm_idx 
                    ON code_submissions 
                    USING gin (code_content gin_trgm_ops)
                """))
                
                # Create trigram index on filename
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS filename_trgm_idx 
                    ON code_submissions 
                    USING gin (filename gin_trgm_ops)
                """))
                
                conn.commit()
                print("✅ Semantic search extensions enabled")
            except Exception as e:
                print(f"⚠️  pg_trgm setup: {e}")
    
    def search(self, query: str, threshold: float = 0.2, limit: int = 10) -> List[Dict]:
        """
        Search code using fuzzy text matching
        
        Args:
            query: Search query (e.g., "authentication logic", "database connection")
            threshold: Minimum similarity score (0-1)
            limit: Maximum number of results
        
        Returns:
            List of matching code submissions with similarity scores
        """
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    id,
                    filename,
                    code_content,
                    similarity(code_content, :query) as content_score,
                    similarity(filename, :query) as filename_score,
                    GREATEST(
                        similarity(code_content, :query),
                        similarity(filename, :query)
                    ) as combined_score,
                    uploaded_at
                FROM code_submissions
                WHERE 
                    similarity(code_content, :query) > :threshold
                    OR similarity(filename, :query) > :threshold
                ORDER BY combined_score DESC
                LIMIT :limit
            """), {
                'query': query, 
                'threshold': threshold,
                'limit': limit
            })
            
            return [
                {
                    'id': row.id,
                    'filename': row.filename,
                    'snippet': self._extract_snippet(row.code_content, query),
                    'content_score': float(row.content_score),
                    'filename_score': float(row.filename_score),
                    'score': float(row.combined_score),
                    'uploaded_at': row.uploaded_at.isoformat() if row.uploaded_at else None
                }
                for row in results
            ]
    
    def _extract_snippet(self, content: str, query: str, context_lines: int = 3) -> str:
        """Extract relevant snippet from code"""
        lines = content.split('\n')
        query_lower = query.lower()
        
        # Find best matching lines
        best_lines = []
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in query_lower.split()):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                best_lines.extend(lines[start:end])
                if len(best_lines) >= 10:
                    break
        
        if best_lines:
            return '\n'.join(best_lines[:10])
        
        # Fallback: return first few lines
        return '\n'.join(lines[:10])
    
    def find_similar_code(self, code_id: int, threshold: float = 0.3, limit: int = 5) -> List[Dict]:
        """Find code submissions similar to a given submission"""
        with self.engine.connect() as conn:
            # Get the original code
            original = conn.execute(text("""
                SELECT code_content FROM code_submissions WHERE id = :id
            """), {'id': code_id}).fetchone()
            
            if not original:
                return []
            
            # Find similar code
            results = conn.execute(text("""
                SELECT 
                    id,
                    filename,
                    code_content,
                    similarity(code_content, :content) as score,
                    uploaded_at
                FROM code_submissions
                WHERE 
                    id != :id
                    AND similarity(code_content, :content) > :threshold
                ORDER BY score DESC
                LIMIT :limit
            """), {
                'id': code_id,
                'content': original.code_content,
                'threshold': threshold,
                'limit': limit
            })
            
            return [
                {
                    'id': row.id,
                    'filename': row.filename,
                    'score': float(row.score),
                    'uploaded_at': row.uploaded_at.isoformat() if row.uploaded_at else None
                }
                for row in results
            ]
    
    def search_by_pattern(self, pattern: str, limit: int = 10) -> List[Dict]:
        """Search using PostgreSQL regex patterns"""
        with self.engine.connect() as conn:
            results = conn.execute(text("""
                SELECT 
                    id,
                    filename,
                    code_content,
                    uploaded_at
                FROM code_submissions
                WHERE code_content ~* :pattern
                ORDER BY uploaded_at DESC
                LIMIT :limit
            """), {'pattern': pattern, 'limit': limit})
            
            return [
                {
                    'id': row.id,
                    'filename': row.filename,
                    'snippet': self._extract_snippet(row.code_content, pattern),
                    'uploaded_at': row.uploaded_at.isoformat() if row.uploaded_at else None
                }
                for row in results
            ]

