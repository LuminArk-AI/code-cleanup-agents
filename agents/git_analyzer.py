"""
Git Integration Module for Repository-Level Analysis

This module enables analyzing entire Git repositories, not just single files.
Supports cloning, diff analysis, and multi-file processing.
"""

import os
import subprocess
import tempfile
import shutil
from typing import List, Dict, Optional
from pathlib import Path


class GitAnalyzer:
    """Handles Git repository operations for code analysis"""
    
    def __init__(self):
        self.temp_dir = None
    
    def clone_repository(self, repo_url: str, branch: Optional[str] = None) -> str:
        """
        Clone a Git repository to a temporary directory
        
        Args:
            repo_url: Git repository URL (HTTPS or SSH)
            branch: Optional branch name (defaults to default branch)
            
        Returns:
            Path to cloned repository directory
        """
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp(prefix='code_analysis_')
        
        try:
            # Build git clone command
            cmd = ['git', 'clone', '--depth', '1', repo_url, self.temp_dir]
            
            if branch:
                cmd.extend(['--branch', branch])
            
            # Clone repository
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Git clone failed: {result.stderr}")
            
            return self.temp_dir
            
        except subprocess.TimeoutExpired:
            self.cleanup()
            raise Exception("Git clone timed out after 5 minutes")
        except Exception as e:
            self.cleanup()
            raise Exception(f"Failed to clone repository: {str(e)}")
    
    def get_changed_files(self, repo_path: str, base_branch: str = 'main') -> List[str]:
        """
        Get list of changed files compared to base branch
        
        Args:
            repo_path: Path to repository
            base_branch: Branch to compare against
            
        Returns:
            List of changed file paths
        """
        try:
            # Get diff of changed files
            result = subprocess.run(
                ['git', 'diff', '--name-only', base_branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                # If branch doesn't exist, return all files
                return self.get_all_code_files(repo_path)
            
            changed_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            return changed_files
            
        except Exception as e:
            # Fallback to all files if diff fails
            return self.get_all_code_files(repo_path)
    
    def get_all_code_files(self, repo_path: str, extensions: List[str] = None) -> List[str]:
        """
        Get all code files in repository
        
        Args:
            repo_path: Path to repository
            extensions: List of file extensions to include (default: .py, .js, .java, .cpp, .c, .rb)
            
        Returns:
            List of file paths relative to repo root
        """
        if extensions is None:
            extensions = ['.py', '.js', '.java', '.cpp', '.c', '.rb', '.ts', '.go', '.rs']
        
        code_files = []
        repo_path_obj = Path(repo_path)
        
        # Common directories to ignore
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 
                      'dist', 'build', '.pytest_cache', '.mypy_cache', 'target'}
        
        for ext in extensions:
            for file_path in repo_path_obj.rglob(f'*{ext}'):
                # Skip ignored directories
                if any(ignore_dir in file_path.parts for ignore_dir in ignore_dirs):
                    continue
                
                # Get relative path
                relative_path = file_path.relative_to(repo_path_obj)
                code_files.append(str(relative_path))
        
        return sorted(code_files)
    
    def read_file(self, repo_path: str, file_path: str) -> str:
        """
        Read file content from repository
        
        Args:
            repo_path: Path to repository root
            file_path: Relative path to file
            
        Returns:
            File content as string
        """
        full_path = os.path.join(repo_path, file_path)
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def get_file_stats(self, repo_path: str) -> Dict:
        """
        Get repository statistics
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with repository statistics
        """
        code_files = self.get_all_code_files(repo_path)
        total_lines = 0
        total_size = 0
        
        for file_path in code_files:
            full_path = os.path.join(repo_path, file_path)
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    total_lines += content.count('\n')
                    total_size += len(content)
            except:
                pass
        
        return {
            'total_files': len(code_files),
            'total_lines': total_lines,
            'total_size': total_size,
            'files': code_files
        }
    
    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass
            self.temp_dir = None
    
    def __del__(self):
        """Cleanup on deletion"""
        self.cleanup()

