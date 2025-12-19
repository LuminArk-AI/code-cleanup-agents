# Large File Optimization - Future Implementation Guide

This document outlines the structure put in place for handling large files in the future. All Tiger Data references are preserved for potential future use.

## Current State

The application currently processes files by:
- Loading entire file into memory
- Processing all lines sequentially
- Storing full code content in database

This works well for files up to ~5000 lines but may need optimization for larger files.

## Structure Added

### 1. Configuration File (`config.py`)
A new configuration file with commented-out settings for:
- File size limits
- Line count thresholds
- Chunked processing settings
- External storage options
- Progress tracking configuration

**Location**: `config.py`

### 2. File Upload Endpoint (`app.py`)
Added TODO comments for:
- File size validation
- Streaming/chunked reading
- File metadata collection

**Location**: `app.py` - `analyze()` function

### 3. Coordinator (`agents/coordinator.py`)
Added TODO comments for:
- Large file detection
- Chunked storage strategies
- Progress tracking
- Memory-efficient processing

**Location**: `agents/coordinator.py` - `analyze_code()` method

### 4. All Agent Classes
Added TODO comments in:
- `agents/security_scanner.py`
- `agents/code_quality.py`
- `agents/performance_analyzer.py`
- `agents/best_practices.py`

Each includes:
- Chunked processing structure
- Large file threshold checks
- Progress tracking placeholders

## Future Implementation Steps

### Phase 1: Basic Large File Support
1. Uncomment file size limits in `app.py`
2. Add file size validation
3. Add user-friendly error messages

### Phase 2: Chunked Processing
1. Implement `_analyze_chunked()` methods in each agent
2. Process files in 1000-line chunks
3. Aggregate results from chunks

### Phase 3: Streaming & Progress
1. Implement streaming file reading
2. Add progress callbacks
3. Update UI with progress bars

### Phase 4: Advanced Optimizations
1. External storage for very large files
2. Result caching based on file hash
3. Incremental analysis (only changed sections)

## Tiger Data References

All Tiger Data references are preserved:
- `test_connection.py` - "Connected to Tiger Data!" message kept
- Fork URL examples in documentation
- All Agentic Postgres references maintained

These can be reactivated if returning to Tiger Data in the future.

## Configuration Usage

When ready to implement, uncomment and configure settings in `config.py`:

```python
# Example: Enable large file support
LARGE_FILE_LINE_THRESHOLD = 5000
CHUNK_SIZE = 1000
ENABLE_PROGRESS_TRACKING = True
```

Then import in relevant files:
```python
from config import LARGE_FILE_LINE_THRESHOLD, CHUNK_SIZE
```

## Testing Large Files

When implementing, test with:
- Small files (< 1000 lines) - should work as before
- Medium files (1000-5000 lines) - should work, may be slower
- Large files (5000-50000 lines) - will use chunked processing
- Very large files (> 50000 lines) - will use streaming

## Notes

- All current functionality remains unchanged
- No breaking changes introduced
- All optimizations are opt-in via configuration
- Tiger Data compatibility preserved

