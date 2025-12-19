# Git Integration Feature

## ✅ What's Been Implemented

### 1. Git Analyzer Module (`agents/git_analyzer.py`)
- Repository cloning (HTTPS/SSH)
- Branch support
- File discovery (all code files or changed files only)
- Repository statistics
- Automatic cleanup of temporary directories

### 2. Repository Analysis Endpoint
- **POST `/analyze/repo`** - Analyze entire Git repositories
- Supports:
  - Repository URL (HTTPS or SSH)
  - Optional branch specification
  - Option to analyze only changed files (diff-based)

### 3. Enhanced Coordinator
- `analyze_repository()` method for multi-file processing
- Processes all files in repository sequentially
- Aggregates results across all files
- Provides repository-level statistics

### 4. Updated UI
- Mode toggle: Switch between "Single File" and "Repository" analysis
- Repository input form with:
  - Repository URL field
  - Branch selector (optional)
  - "Analyze only changed files" checkbox
- Enhanced results display showing file paths for repository analysis

## 🚀 How to Use

### Web Interface
1. Go to the main page
2. Click "Repository" mode toggle
3. Enter repository URL: `https://github.com/username/repo.git`
4. (Optional) Enter branch name
5. (Optional) Check "Analyze only changed files"
6. Click "Analyze Repository"

### API Usage
```python
import requests

response = requests.post('http://localhost:5000/analyze/repo', json={
    'repo_url': 'https://github.com/username/repo.git',
    'branch': 'develop',  # optional
    'analyze_changed_only': False  # optional
})

results = response.json()
```

## 📊 What This Enables

### Before (Single File)
- ❌ Had to upload files one by one
- ❌ No repository context
- ❌ Manual process for multiple files

### After (Repository Analysis)
- ✅ Analyze entire repositories at once
- ✅ Understand codebase structure
- ✅ Automated multi-file processing
- ✅ Diff-based analysis (only changed files)

## 🔄 Comparison with GitHub Actions

### Now You Can:
- ✅ Analyze entire repositories (like GitHub Actions)
- ✅ Process multiple files automatically
- ✅ Get repository-level statistics
- ✅ Analyze specific branches
- ✅ Focus on changed files only

### Still Missing (Future Enhancements):
- ⏳ CI/CD integration (webhooks)
- ⏳ PR comment integration
- ⏳ Automated analysis on push
- ⏳ Private repository authentication
- ⏳ Commit history analysis
- ⏳ Branch comparison
- ⏳ Background job processing (for large repos)

## 🎯 Next Steps to Compete with GitHub Actions

### Phase 1: CI/CD Integration (High Priority)
- GitHub webhook support
- Auto-analyze on push
- PR comment integration
- GitLab CI integration

### Phase 2: Background Processing
- Celery/RQ for async jobs
- Job queue for large repositories
- Progress tracking
- Email/Slack notifications

### Phase 3: Advanced Features
- Private repo authentication
- Commit history analysis
- Branch comparison
- Custom rule sets per repository
- Team workspaces

## 📝 Notes

- Currently supports **public repositories only**
- Uses shallow clone (`--depth 1`) for faster cloning
- Temporary directories are automatically cleaned up
- Large repositories may take time (consider background jobs)
- All Tiger Data references preserved for future use

## 🔧 Configuration

No additional configuration needed! Just ensure:
- Git is installed on the system
- Network access to repository URLs
- Sufficient disk space for temporary clones

