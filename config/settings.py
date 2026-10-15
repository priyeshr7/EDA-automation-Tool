"""
Configuration settings for EDA Automation Tool
"""

# File upload settings
MAX_FILE_SIZE_MB = 200
SUPPORTED_FILE_TYPES = ['csv', 'xlsx', 'xls', 'json']

# Data processing settings
DEFAULT_MISSING_VALUE_STRATEGY = 'drop'
OUTLIER_DETECTION_METHODS = ['iqr', 'zscore']
CORRELATION_THRESHOLD = 0.7

# Visualization settings
DEFAULT_CHART_HEIGHT = 400
DEFAULT_CHART_WIDTH = 600
COLOR_PALETTE = 'viridis'

# Export settings
EXPORT_FORMATS = ['csv', 'xlsx', 'png', 'pdf', 'svg']
DEFAULT_DPI = 300

# Performance settings
CACHE_TTL = 3600  # 1 hour in seconds
MAX_ROWS_PREVIEW = 1000