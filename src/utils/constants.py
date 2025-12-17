"""
LVL-CODES: Constants and Enumerations
================================================================================
This module defines all constants, enumerations, and configuration values
used throughout the sales target management system.

Constants are organized by category for easy maintenance and reference.

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from enum import Enum
from typing import Dict, List

# ============================================================================
# DATABASE CONSTANTS
# ============================================================================

# Table names in the data warehouse
class TableNames:
    """Data warehouse table names"""
    SALES_TRANSACTIONS = "fact_sales"
    PRODUCTS = "dim_products"
    GEOGRAPHY = "dim_geography"
    CHANNELS = "dim_channels"
    CALENDAR = "dim_calendar"
    INVENTORY = "fact_inventory"
    RETURNS = "fact_returns"
    PROMOTIONS = "fact_promotions"
    TARGETS = "fact_targets"
    FORECASTS = "fact_forecasts"


# Column names for dimension tables
class ColumnNames:
    """Standard column names across tables"""
    # Primary keys
    DATE = "date"
    SKU_ID = "sku_id"
    PRODUCT_ID = "product_id"
    REGION_ID = "region_id"
    CHANNEL_ID = "channel_id"
    STORE_ID = "store_id"

    # Product attributes
    CATEGORY = "category"
    SUBGROUP = "subgroup"
    SKU_NAME = "sku_name"
    BRAND = "brand"

    # Geographic attributes
    REGION = "region"
    TERRITORY = "territory"
    STATE = "state"
    CITY = "city"

    # Sales metrics
    SALES_AMOUNT = "sales_amount"
    SALES_QUANTITY = "sales_quantity"
    RETURNS_AMOUNT = "returns_amount"
    RETURNS_QUANTITY = "returns_quantity"
    NET_SALES = "net_sales"

    # Inventory metrics
    STOCK_QUANTITY = "stock_quantity"
    STOCK_VALUE = "stock_value"
    DAYS_OF_SUPPLY = "days_of_supply"


# ============================================================================
# TIME PERIODS
# ============================================================================

class TimePeriod:
    """Time period constants for aggregations"""
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"
    QUARTERLY = "Q"
    YEARLY = "Y"


# Standard date formats
class DateFormats:
    """Date format strings"""
    STANDARD = "%Y-%m-%d"
    DISPLAY = "%B %d, %Y"
    MONTH_YEAR = "%Y-%m"
    YEAR_ONLY = "%Y"
    DATETIME = "%Y-%m-%d %H:%M:%S"


# ============================================================================
# PRODUCT CATEGORIES
# ============================================================================

class ProductCategory(Enum):
    """Product category enumeration"""
    DOG_FOOD = "Dog Food"
    CAT_FOOD = "Cat Food"
    TREATS = "Treats"
    SUPPLEMENTS = "Supplements"
    ACCESSORIES = "Accessories"
    OTHER = "Other"


class ProductSubGroup(Enum):
    """Product sub-group enumeration (examples)"""
    # Dog Food
    DRY_DOG_FOOD = "Dry Dog Food"
    WET_DOG_FOOD = "Wet Dog Food"
    GRAIN_FREE_DOG = "Grain-Free Dog Food"
    ORGANIC_DOG = "Organic Dog Food"

    # Cat Food
    DRY_CAT_FOOD = "Dry Cat Food"
    WET_CAT_FOOD = "Wet Cat Food"
    GRAIN_FREE_CAT = "Grain-Free Cat Food"
    ORGANIC_CAT = "Organic Cat Food"

    # Treats
    DOG_TREATS = "Dog Treats"
    CAT_TREATS = "Cat Treats"
    DENTAL_CHEWS = "Dental Chews"

    # Supplements
    VITAMINS = "Vitamins"
    JOINT_SUPPORT = "Joint Support"
    DIGESTIVE_HEALTH = "Digestive Health"


# ============================================================================
# GEOGRAPHIC REGIONS
# ============================================================================

class Region(Enum):
    """Geographic regions"""
    NORTHEAST = "Northeast"
    SOUTHEAST = "Southeast"
    MIDWEST = "Midwest"
    WEST = "West"
    SOUTHWEST = "Southwest"


# ============================================================================
# SALES CHANNELS
# ============================================================================

class Channel(Enum):
    """Sales channel enumeration"""
    RETAIL = "Retail"
    ECOMMERCE = "E-commerce"
    WHOLESALE = "Wholesale"
    DISTRIBUTION = "Distribution"


# ============================================================================
# MODEL TYPES
# ============================================================================

class ModelType(Enum):
    """Forecasting model types"""
    SARIMA = "sarima"
    PROPHET = "prophet"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    RANDOM_FOREST = "random_forest"
    ENSEMBLE = "ensemble"


# ============================================================================
# TARGET SETTINGS
# ============================================================================

# Default growth targets
DEFAULT_MINIMUM_NET_GROWTH = 0.16  # 16%
DEFAULT_TARGET_YEAR = 2026
DEFAULT_BASE_YEAR = 2025

# Variance thresholds
VARIANCE_ALERT_THRESHOLD = 0.10  # ±10% triggers alert
VARIANCE_CRITICAL_THRESHOLD = 0.20  # ±20% critical variance

# Rolling forecast settings
ROLLING_FORECAST_WINDOW_MONTHS = 12
MIN_HISTORY_MONTHS = 24  # Minimum data history required


# ============================================================================
# INVENTORY CONSTANTS
# ============================================================================

# Stock thresholds
STOCKOUT_RISK_THRESHOLD = 0.15  # 15% probability
SAFETY_STOCK_MULTIPLIER = 1.5   # 1.5x standard deviation
SERVICE_LEVEL_TARGET = 0.95     # 95% service level

# Lead times (in days)
SUPPLIER_LEAD_TIME = 14
WAREHOUSE_LEAD_TIME = 3
DISTRIBUTION_LEAD_TIME = 7
TOTAL_LEAD_TIME = SUPPLIER_LEAD_TIME + WAREHOUSE_LEAD_TIME + DISTRIBUTION_LEAD_TIME

# Reorder points
REORDER_POINT_DAYS = 30  # Days of supply for reorder


# ============================================================================
# DATA QUALITY THRESHOLDS
# ============================================================================

# Minimum data completeness percentage
MIN_DATA_COMPLETENESS = 0.95  # 95%

# Maximum allowed duplicate percentage
MAX_DUPLICATE_PERCENTAGE = 0.01  # 1%

# Outlier detection (z-score)
OUTLIER_Z_SCORE_THRESHOLD = 3.0

# Missing value imputation
MAX_MISSING_FOR_IMPUTATION = 0.05  # Max 5% missing to impute


# ============================================================================
# MODEL PERFORMANCE THRESHOLDS
# ============================================================================

# Acceptable model performance metrics
MIN_R2_SCORE = 0.70              # Minimum R² of 0.70
MAX_MAPE = 0.15                  # Maximum 15% MAPE
MAX_RMSE_RATIO = 0.20            # RMSE should be <20% of mean

# Model retraining triggers
PERFORMANCE_DROP_THRESHOLD = 0.10  # Retrain if performance drops >10%
MIN_DAYS_BETWEEN_RETRAINING = 7    # Don't retrain more than weekly


# ============================================================================
# OPTIMIZATION PARAMETERS
# ============================================================================

# Solver settings
MAX_OPTIMIZATION_ITERATIONS = 10000
OPTIMIZATION_TOLERANCE = 0.0001
OPTIMIZATION_TIMEOUT_SECONDS = 300  # 5 minutes

# Constraint relaxation
CONSTRAINT_VIOLATION_PENALTY = 1000.0  # Penalty for violating hard constraints


# ============================================================================
# SCENARIO ANALYSIS
# ============================================================================

# Monte Carlo simulation
MONTE_CARLO_SIMULATIONS = 10000
CONFIDENCE_LEVELS = [0.10, 0.25, 0.50, 0.75, 0.90]  # P10, P25, P50, P75, P90

# Predefined scenarios
SCENARIO_BEST_CASE_GROWTH = 0.22   # 22%
SCENARIO_BASE_CASE_GROWTH = 0.16   # 16%
SCENARIO_WORST_CASE_GROWTH = 0.10  # 10%


# ============================================================================
# CACHING SETTINGS
# ============================================================================

# Cache TTL (time to live) in seconds
CACHE_TTL_SHORT = 300       # 5 minutes
CACHE_TTL_MEDIUM = 3600     # 1 hour
CACHE_TTL_LONG = 86400      # 24 hours
CACHE_TTL_VERY_LONG = 604800  # 1 week


# ============================================================================
# LOGGING SETTINGS
# ============================================================================

# Log levels
LOG_LEVEL_DEBUG = "DEBUG"
LOG_LEVEL_INFO = "INFO"
LOG_LEVEL_WARNING = "WARNING"
LOG_LEVEL_ERROR = "ERROR"
LOG_LEVEL_CRITICAL = "CRITICAL"

# Log formats
LOG_FORMAT_DETAILED = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
LOG_FORMAT_SIMPLE = "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"


# ============================================================================
# API SETTINGS
# ============================================================================

# Rate limiting
API_RATE_LIMIT_PER_MINUTE = 100
API_RATE_LIMIT_BURST = 10

# Pagination
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000


# ============================================================================
# DASHBOARD SETTINGS
# ============================================================================

# Refresh intervals (in seconds)
DASHBOARD_REFRESH_INTERVAL = 300  # 5 minutes
KPI_REFRESH_INTERVAL = 60         # 1 minute
CHART_ANIMATION_DURATION = 500    # milliseconds

# Color schemes for visualizations
COLOR_SCHEMES = {
    "performance": {
        "excellent": "#2ecc71",  # Green
        "good": "#3498db",       # Blue
        "warning": "#f39c12",    # Orange
        "critical": "#e74c3c"    # Red
    },
    "categories": [
        "#3498db", "#2ecc71", "#f39c12", "#e74c3c",
        "#9b59b6", "#1abc9c", "#34495e", "#16a085"
    ],
    "sequential": "Blues",
    "diverging": "RdYlGn"
}


# ============================================================================
# FILE PATHS
# ============================================================================

# Default paths (relative to project root)
PATH_CONFIG = "./config/"
PATH_DATA = "./data/"
PATH_MODELS = "./models/saved_models/"
PATH_LOGS = "./logs/"
PATH_REPORTS = "./reports/"
PATH_BACKUPS = "./backups/"


# ============================================================================
# ERROR MESSAGES
# ============================================================================

class ErrorMessages:
    """Standard error messages"""
    DB_CONNECTION_FAILED = "Failed to connect to database"
    INSUFFICIENT_DATA = "Insufficient historical data for modeling"
    MODEL_TRAINING_FAILED = "Model training failed"
    OPTIMIZATION_FAILED = "Target optimization failed to converge"
    INVALID_CONFIGURATION = "Invalid configuration parameters"
    DATA_VALIDATION_FAILED = "Data validation checks failed"


# ============================================================================
# SUCCESS MESSAGES
# ============================================================================

class SuccessMessages:
    """Standard success messages"""
    DB_CONNECTION_SUCCESS = "Successfully connected to database"
    MODEL_TRAINED = "Model trained successfully"
    TARGETS_ALLOCATED = "Targets allocated successfully"
    REPORT_GENERATED = "Report generated successfully"
    DATA_LOADED = "Data loaded successfully"


# ============================================================================
# FEATURE NAMES
# ============================================================================

# Standard feature names for ML models
TEMPORAL_FEATURES = [
    "year", "month", "quarter", "day_of_week", "day_of_month",
    "day_of_year", "week_of_year", "is_weekend", "is_month_start",
    "is_month_end", "is_quarter_start", "is_quarter_end"
]

# Lag features (days)
LAG_PERIODS = [1, 7, 14, 30, 90, 365]

# Rolling window sizes (days)
ROLLING_WINDOWS = [7, 14, 30, 90]


# ============================================================================
# HOLIDAYS (US-centric, customize as needed)
# ============================================================================

# Major holidays that impact pet food sales
MAJOR_HOLIDAYS = [
    "New Year's Day",
    "Valentine's Day",
    "Easter",
    "Memorial Day",
    "Independence Day",
    "Labor Day",
    "Thanksgiving",
    "Black Friday",
    "Cyber Monday",
    "Christmas"
]

# Pet-specific observance days
PET_HOLIDAYS = [
    {"name": "National Pet Day", "date": "04-11"},
    {"name": "National Dog Day", "date": "08-26"},
    {"name": "National Cat Day", "date": "10-29"},
    {"name": "National Puppy Day", "date": "03-23"}
]


# ============================================================================
# VALIDATION RULES
# ============================================================================

class ValidationRules:
    """Data validation rules"""
    # Sales amount must be positive
    MIN_SALES_AMOUNT = 0.0
    MAX_SALES_AMOUNT = 1000000.0  # $1M per transaction (flag for review)

    # Quantity must be positive
    MIN_QUANTITY = 0
    MAX_QUANTITY = 10000  # Units per transaction

    # Return rate cannot exceed 100%
    MIN_RETURN_RATE = 0.0
    MAX_RETURN_RATE = 1.0

    # Stock quantity
    MIN_STOCK = 0
    MAX_STOCK = 1000000  # Units

    # Date ranges
    MIN_DATE = "2020-01-01"  # No data before 2020
    MAX_DATE = "2030-12-31"  # No forecasts beyond 2030


# ============================================================================
# HELPER DICTIONARIES
# ============================================================================

# Month name to number mapping
MONTH_NAME_TO_NUMBER: Dict[str, int] = {
    "January": 1, "February": 2, "March": 3, "April": 4,
    "May": 5, "June": 6, "July": 7, "August": 8,
    "September": 9, "October": 10, "November": 11, "December": 12
}

# Quarter to months mapping
QUARTER_TO_MONTHS: Dict[int, List[int]] = {
    1: [1, 2, 3],
    2: [4, 5, 6],
    3: [7, 8, 9],
    4: [10, 11, 12]
}

# Day of week names
DAY_NAMES: List[str] = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]


# ============================================================================
# METRIC CALCULATIONS
# ============================================================================

class MetricFormulas:
    """Formulas for calculated metrics (as strings for documentation)"""
    NET_SALES = "gross_sales - returns"
    NET_GROWTH = "(current_net_sales - baseline_net_sales) / baseline_net_sales"
    VARIANCE = "actual - target"
    VARIANCE_PERCENT = "(actual - target) / target"
    TARGET_ACHIEVEMENT = "actual / target"
    FORECAST_ACCURACY = "1 - abs(actual - forecast) / actual"
    RETURN_RATE = "returns / gross_sales"
    INVENTORY_TURNOVER = "cost_of_goods_sold / average_inventory"
    DAYS_OF_SUPPLY = "stock_quantity / average_daily_sales"


# ============================================================================
# EXPORT FORMATS
# ============================================================================

class ExportFormat(Enum):
    """Supported export formats for reports"""
    CSV = "csv"
    EXCEL = "xlsx"
    JSON = "json"
    PDF = "pdf"
    HTML = "html"


# ============================================================================
# END OF CONSTANTS
# ============================================================================
