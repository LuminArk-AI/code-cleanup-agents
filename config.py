"""
Configuration file for Code Cleanup Agents

TODO: Future optimization settings for large file handling
These can be enabled when implementing large file support
"""

# File size limits (in bytes)
# TODO: Uncomment and configure when implementing large file support
# MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB default
# MAX_FILE_SIZE_LARGE = 100 * 1024 * 1024  # 100MB for chunked processing

# Line count thresholds
# TODO: Uncomment when implementing chunked processing
# LARGE_FILE_LINE_THRESHOLD = 5000  # Files with more lines use chunked processing
# VERY_LARGE_FILE_LINE_THRESHOLD = 50000  # Files with more lines use streaming

# Processing configuration
# TODO: Future optimization settings
# CHUNK_SIZE = 1000  # Lines per chunk for chunked processing
# STREAM_BUFFER_SIZE = 8192  # Bytes for streaming file reads
# ENABLE_PROGRESS_TRACKING = True  # Track progress for long-running analyses
# ENABLE_CACHING = True  # Cache analysis results based on file hash

# Database optimization
# TODO: Future optimization - For large files
# USE_EXTERNAL_STORAGE = False  # Store large files externally (S3, etc.)
# EXTERNAL_STORAGE_THRESHOLD = 1 * 1024 * 1024  # 1MB - files larger stored externally
# COMPRESS_STORED_CODE = False  # Compress code content in database

# Agent processing
# TODO: Future optimization
# PARALLEL_CHUNK_PROCESSING = True  # Process chunks in parallel
# MAX_PARALLEL_CHUNKS = 4  # Maximum chunks processed simultaneously
# PROGRESS_UPDATE_INTERVAL = 0.1  # Seconds between progress updates

