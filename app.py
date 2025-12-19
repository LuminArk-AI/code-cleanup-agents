import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from sqlalchemy import create_engine
from agents.coordinator import Coordinator
from agents.semantic_search import SemanticSearch

load_dotenv()

app = Flask(__name__)

# Connect to database
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")
# Convert to postgresql+psycopg:// for psycopg3 (Python 3.13 compatible)
# Handle both postgres:// and postgresql:// formats
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql+psycopg://', 1)
elif database_url.startswith('postgresql://') and '+psycopg' not in database_url:
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
engine = create_engine(database_url)

# Initialize semantic search
semantic_search = SemanticSearch(engine)

@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests to prevent 404 errors"""
    return '', 204  # No Content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Future optimization - Add file size limits for large file handling
    # MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default
    # file.seek(0, os.SEEK_END)
    # file_size = file.tell()
    # file.seek(0)
    # if file_size > MAX_FILE_SIZE:
    #     return jsonify({'error': f'File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB'}), 400
    
    # Read file content
    # TODO: Future optimization - For very large files, implement streaming/chunked reading
    # For now, read entire file into memory
    code = file.read().decode('utf-8')
    filename = file.filename
    
    # TODO: Future optimization - Add file metadata (size, line count, etc.)
    # file_metadata = {
    #     'size': len(code),
    #     'lines': code.count('\n'),
    #     'encoding': 'utf-8'
    # }
    
    # Run analysis
    coordinator = Coordinator(engine)
    results = coordinator.analyze_code(code, filename)
    
    return jsonify(results)

@app.route('/analyze/repo', methods=['POST'])
def analyze_repo():
    """Analyze entire Git repository"""
    data = request.json
    
    if not data or 'repo_url' not in data:
        return jsonify({'error': 'repo_url is required'}), 400
    
    repo_url = data.get('repo_url')
    branch = data.get('branch', None)
    analyze_changed_only = data.get('analyze_changed_only', False)
    
    if not repo_url:
        return jsonify({'error': 'repo_url cannot be empty'}), 400
    
    try:
        coordinator = Coordinator(engine)
        results = coordinator.analyze_repository(
            repo_url=repo_url,
            branch=branch,
            analyze_changed_only=analyze_changed_only
        )
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def status():
    """Show system status and fork information"""
    return render_template('status.html', 
        main_db=os.getenv('DATABASE_URL') is not None,
        security_fork=os.getenv('SECURITY_FORK_URL') is not None,
        quality_fork=os.getenv('QUALITY_FORK_URL') is not None,
        performance_fork=os.getenv('PERFORMANCE_FORK_URL') is not None
    )

@app.route('/search', methods=['GET'])
def search_page():
    """Render search interface"""
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search code submissions"""
    data = request.json
    query = data.get('query', '')
    threshold = data.get('threshold', 0.2)
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        results = semantic_search.search(query, threshold=threshold)
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/similar/<int:code_id>', methods=['GET'])
def find_similar(code_id):
    """Find similar code submissions"""
    try:
        results = semantic_search.find_similar_code(code_id)
        return jsonify({
            'code_id': code_id,
            'similar': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pattern', methods=['POST'])
def pattern_search():
    """Search by regex pattern"""
    data = request.json
    pattern = data.get('pattern', '')
    
    if not pattern:
        return jsonify({'error': 'Pattern is required'}), 400
    
    try:
        results = semantic_search.search_by_pattern(pattern)
        return jsonify({
            'pattern': pattern,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment)
    port = int(os.getenv('PORT', 5000))
    # Run in production mode
    app.run(host='0.0.0.0', port=port, debug=False)
