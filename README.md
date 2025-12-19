# Code Cleanup Agents

A modern, multi-agent code analysis platform powered by Agentic Postgres that automatically scans code for security vulnerabilities, quality issues, performance problems, and best practice violations.

## 🚀 Features

### Multi-Agent Analysis
- **🔒 Security Agent**: Detects hardcoded secrets, SQL injection vulnerabilities, and security risks
- **✨ Quality Agent**: Identifies code quality issues, duplicates, and maintainability problems
- **⚡ Performance Agent**: Finds N+1 queries, inefficient loops, and optimization opportunities
- **📋 Best Practices Agent**: Checks coding standards, naming conventions, and language-specific idioms

### Parallel Processing with Database Forks
- Utilizes **Agentic Postgres** database forks for true parallel execution
- Each agent runs on its dedicated database fork simultaneously
- Results are automatically merged back to the main database

### Git Repository Analysis
- **Analyze entire Git repositories** - Clone and analyze all files in a repo
- Support for public repositories (HTTPS/SSH)
- Analyze specific branches
- Option to analyze only changed files (diff-based)
- Multi-file parallel processing

### Semantic Code Search
- Natural language code search using PostgreSQL `pg_trgm` extension
- Fuzzy matching for code content and filenames
- Find similar code patterns across your codebase

### Modern Web Interface
- Clean, modern SaaS-style UI built with Flask
- Real-time analysis progress tracking
- Interactive issue browsing with severity badges
- Responsive design for all devices

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+ with `pg_trgm` extension
- Agentic Postgres account (for database forks)
- pip (Python package manager)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LuminArk-AI/code-cleanup-agents.git
   cd code-cleanup-agents
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask sqlalchemy python-dotenv gitpython
   ```
   
   Or use the requirements file:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   # Main database connection
   DATABASE_URL=postgresql://user:password@host:port/database
   
   # Database forks for parallel processing (optional but recommended)
   SECURITY_FORK_URL=postgresql://user:password@host:port/security_fork-db-60626
   QUALITY_FORK_URL=postgresql://user:password@host:port/quality_fork-db-60626
   PERFORMANCE_FORK_URL=postgresql://user:password@host:port/performance_fork-db-60626
   BEST_PRACTICES_FORK_URL=postgresql://user:password@host:port/best_practices_fork-db-60626
   ```

5. **Initialize the database**
   
   Run the connection test to create required tables:
   ```bash
   python test_connection.py
   ```

## 🎯 Usage

### Web Interface

Start the Flask development server:
```bash
python app.py
```

Then open your browser to `http://localhost:5000`

**Features:**
- **Single File Analysis**: Upload individual code files
- **Repository Analysis**: Analyze entire Git repositories
  - Enter repository URL (HTTPS or SSH)
  - Optional: Specify branch name
  - Option to analyze only changed files
- View real-time analysis progress
- Browse issues by category and severity
- Search your codebase semantically

**Repository Analysis Example:**
1. Click "Repository" mode toggle
2. Enter: `https://github.com/username/repo.git`
3. (Optional) Specify branch: `develop`
4. (Optional) Check "Analyze only changed files"
5. Click "Analyze Repository"

### Command Line Interface

Analyze a code file directly:
```bash
python main.py
```

This will analyze `data/bad_code.py` and print results to the console.

### Programmatic Usage

```python
from sqlalchemy import create_engine
from agents.coordinator import Coordinator

# Connect to database
engine = create_engine('postgresql://user:password@host:port/database')

# Initialize coordinator
coordinator = Coordinator(engine)

# Analyze code
with open('your_code.py', 'r') as f:
    code = f.read()

results = coordinator.analyze_code(code, 'your_code.py')

# Access results
print(f"Total issues: {results['total_issues']}")
print(f"Security issues: {results['security']['count']}")
print(f"Quality issues: {results['quality']['count']}")
```

## 🏗️ Architecture

### Multi-Agent System

```
Code Upload
    ↓
Coordinator
    ↓
    ├──→ Security Agent (Fork 1)
    ├──→ Quality Agent (Fork 2)
    ├──→ Performance Agent (Fork 3)
    └──→ Best Practices Agent (Fork 4)
    ↓
Merge Results
    ↓
Display Results
```

### Database Schema

The system creates the following tables:

- `code_submissions`: Stores uploaded code files
- `security_findings`: Security agent results
- `quality_findings`: Quality agent results
- `performance_findings`: Performance agent results
- `best_practices_findings`: Best practices agent results
- `merged_findings`: Consolidated results from all agents

### Agents

#### Security Scanner
- Hardcoded credentials (passwords, API keys, tokens)
- SQL injection vulnerabilities
- Unsafe eval() usage
- Missing input validation

#### Code Quality Agent
- Code duplication
- Long functions
- Missing documentation
- Complex code structures

#### Performance Agent
- N+1 query problems
- Inefficient loops
- Missing connection pooling
- SELECT * queries

#### Best Practices Agent
- Language-specific best practices
- Naming conventions
- Code organization
- Anti-patterns

## 🔍 Semantic Search

The platform includes a powerful semantic search feature:

```python
from agents.semantic_search import SemanticSearch

search = SemanticSearch(engine)

# Search by natural language
results = search.search("authentication logic", threshold=0.2)

# Find similar code
similar = search.find_similar_code(code_id=1)

# Pattern-based search
pattern_results = search.search_by_pattern(r"password\s*=")
```

## 🧪 Testing

### Test Database Connection
```bash
python test_connection.py
```

### Test Fork Configuration
```bash
python test_forks.py
```

### Test Complete System
```bash
python test_complete_system.py
```

## 📁 Project Structure

```
code-cleanup-agents/
├── agents/
│   ├── __init__.py
│   ├── coordinator.py          # Coordinates all agents
│   ├── security_scanner.py     # Security analysis
│   ├── code_quality.py         # Quality analysis
│   ├── performance_analyzer.py # Performance analysis
│   ├── best_practices.py       # Best practices analysis
│   └── semantic_search.py      # Semantic search engine
├── templates/
│   ├── index.html              # Main analysis interface
│   ├── search.html             # Semantic search interface
│   └── status.html             # System status page
├── data/
│   └── bad_code.py             # Sample code for testing
├── app.py                      # Flask web application
├── main.py                     # CLI entry point
├── test_connection.py          # Database connection test
├── test_forks.py               # Fork configuration test
└── test_complete_system.py    # Full system test
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | Main PostgreSQL connection string | Yes |
| `SECURITY_FORK_URL` | Security agent fork connection | No (recommended) |
| `QUALITY_FORK_URL` | Quality agent fork connection | No (recommended) |
| `PERFORMANCE_FORK_URL` | Performance agent fork connection | No |
| `BEST_PRACTICES_FORK_URL` | Best practices agent fork connection | No |

### Supported File Types

- Python (`.py`)
- JavaScript (`.js`)
- Java (`.java`)
- C++ (`.cpp`)
- C (`.c`)
- Ruby (`.rb`)

## 🚀 Performance

With database forks enabled, all four agents run in parallel, significantly reducing analysis time:

- **Sequential**: ~4x agent execution time
- **Parallel (with forks)**: ~1x agent execution time (fastest agent)

## 📊 API Endpoints

### Web Interface
- `GET /` - Main analysis interface
- `GET /search` - Semantic search interface
- `GET /status` - System status page

### API Endpoints
- `POST /analyze` - Analyze uploaded code file
- `POST /api/search` - Semantic code search
- `GET /api/similar/<code_id>` - Find similar code
- `POST /api/pattern` - Pattern-based search

## 🐛 Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check connection string format
- Ensure database exists and is accessible

### Fork Configuration
- Verify fork URLs are correct
- Check Agentic Postgres account status
- Run `test_forks.py` to diagnose issues

### Extension Errors
- Ensure `pg_trgm` extension is available
- Check PostgreSQL version (12+ required)
- Verify database user has CREATE EXTENSION permission

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Database powered by [PostgreSQL](https://www.postgresql.org/)
- Parallel processing enabled by [Agentic Postgres](https://agenticpostgres.com/)
- Semantic search uses PostgreSQL `pg_trgm` extension

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

**Repository**: [https://github.com/LuminArk-AI/code-cleanup-agents](https://github.com/LuminArk-AI/code-cleanup-agents)

---

**Made with ❤️ for cleaner, safer code**

