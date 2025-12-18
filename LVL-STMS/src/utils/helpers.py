"""
LVL-CODES: Helper Functions and Utilities
================================================================================
This module provides common utility functions used throughout the application.
Functions are organized by category for easy discovery.

Categories:
    - Date/Time utilities
    - Data validation
    - Metric calculations
    - File operations
    - Configuration loading
    - Data transformations

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

import os
import yaml
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from src.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)

# Load environment variables
load_dotenv()


# ============================================================================
# CONFIGURATION LOADING
# ============================================================================

def load_config(config_name: str, config_dir: str = "./config/") -> Dict[str, Any]:
    """
    Load a YAML configuration file.

    This function loads configuration files and resolves environment variable
    references in the format ${VAR_NAME:default_value}.

    Args:
        config_name: Name of the config file (with or without .yaml extension)
        config_dir: Directory containing configuration files

    Returns:
        Dictionary containing configuration data

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML

    Example:
        >>> config = load_config("database")
        >>> db_host = config["data_warehouse"]["host"]
    """
    # Add .yaml extension if not present
    if not config_name.endswith(".yaml") and not config_name.endswith(".yml"):
        config_name = f"{config_name}.yaml"

    config_path = Path(config_dir) / config_name

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f)

        # Resolve environment variables
        resolved_config = _resolve_env_vars(config_data)

        logger.debug(f"Loaded configuration from {config_path}")
        return resolved_config

    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML configuration: {e}")
        raise


def _resolve_env_vars(data: Any) -> Any:
    """
    Recursively resolve environment variable references in configuration.

    Supports format: ${VAR_NAME:default_value}

    Args:
        data: Configuration data (dict, list, or primitive)

    Returns:
        Configuration with resolved environment variables
    """
    if isinstance(data, dict):
        return {key: _resolve_env_vars(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_resolve_env_vars(item) for item in data]
    elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
        # Extract variable name and default value
        var_expr = data[2:-1]  # Remove ${ and }

        if ":" in var_expr:
            var_name, default_value = var_expr.split(":", 1)
        else:
            var_name = var_expr
            default_value = None

        # Get from environment
        value = os.getenv(var_name, default_value)

        # Try to convert to appropriate type
        if value is not None:
            # Try boolean
            if value.lower() in ("true", "false"):
                return value.lower() == "true"
            # Try integer
            try:
                return int(value)
            except ValueError:
                pass
            # Try float
            try:
                return float(value)
            except ValueError:
                pass

        return value
    else:
        return data


# ============================================================================
# DATE/TIME UTILITIES
# ============================================================================

def get_date_range(
    start_date: Union[str, datetime],
    end_date: Union[str, datetime],
    freq: str = "D"
) -> pd.DatetimeIndex:
    """
    Generate a date range between two dates.

    Args:
        start_date: Start date (string or datetime)
        end_date: End date (string or datetime)
        freq: Frequency string ('D'=daily, 'W'=weekly, 'M'=monthly, etc.)

    Returns:
        Pandas DatetimeIndex of dates

    Example:
        >>> dates = get_date_range("2026-01-01", "2026-12-31")
        >>> len(dates)  # 365 days
    """
    if isinstance(start_date, str):
        start_date = pd.to_datetime(start_date)
    if isinstance(end_date, str):
        end_date = pd.to_datetime(end_date)

    return pd.date_range(start=start_date, end=end_date, freq=freq)


def get_fiscal_year(date: Union[str, datetime], fiscal_year_start: int = 1) -> int:
    """
    Get fiscal year for a given date.

    Args:
        date: Date to check
        fiscal_year_start: Month number when fiscal year starts (1-12)

    Returns:
        Fiscal year

    Example:
        >>> get_fiscal_year("2026-03-15", fiscal_year_start=4)  # FY starting in April
        2026  # If after April, FY 2026; if before, FY 2025
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)

    if date.month >= fiscal_year_start:
        return date.year
    else:
        return date.year - 1


def is_business_day(date: Union[str, datetime]) -> bool:
    """
    Check if a date is a business day (Monday-Friday).

    Args:
        date: Date to check

    Returns:
        True if business day, False otherwise
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)

    return date.weekday() < 5  # 0-4 are Monday-Friday


def add_business_days(date: Union[str, datetime], days: int) -> datetime:
    """
    Add business days to a date (skipping weekends).

    Args:
        date: Starting date
        days: Number of business days to add

    Returns:
        New date after adding business days

    Example:
        >>> add_business_days("2026-01-02", 5)  # Friday + 5 business days = next Friday
    """
    if isinstance(date, str):
        date = pd.to_datetime(date)

    business_days_added = 0
    current_date = date

    while business_days_added < days:
        current_date += timedelta(days=1)
        if is_business_day(current_date):
            business_days_added += 1

    return current_date


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    date_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None
) -> Tuple[bool, List[str]]:
    """
    Validate a DataFrame meets expected requirements.

    Args:
        df: DataFrame to validate
        required_columns: Columns that must be present
        date_columns: Columns that should contain dates
        numeric_columns: Columns that should contain numeric data

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> valid, errors = validate_dataframe(
        >>>     df,
        >>>     required_columns=["date", "sales"],
        >>>     numeric_columns=["sales"]
        >>> )
        >>> if not valid:
        >>>     print(f"Validation errors: {errors}")
    """
    errors = []

    # Check if DataFrame is empty
    if df.empty:
        errors.append("DataFrame is empty")
        return False, errors

    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")

    # Validate date columns
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        pd.to_datetime(df[col])
                    except Exception:
                        errors.append(f"Column '{col}' cannot be converted to datetime")

    # Validate numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    errors.append(f"Column '{col}' is not numeric")

    is_valid = len(errors) == 0
    return is_valid, errors


def check_data_completeness(df: pd.DataFrame, threshold: float = 0.95) -> Dict[str, float]:
    """
    Check data completeness for each column.

    Args:
        df: DataFrame to check
        threshold: Minimum completeness threshold (0-1)

    Returns:
        Dictionary mapping column names to completeness ratios

    Example:
        >>> completeness = check_data_completeness(df, threshold=0.95)
        >>> for col, ratio in completeness.items():
        >>>     if ratio < 0.95:
        >>>         print(f"Column {col} only {ratio:.1%} complete")
    """
    completeness = {}

    for column in df.columns:
        non_null_count = df[column].notna().sum()
        total_count = len(df)
        ratio = non_null_count / total_count if total_count > 0 else 0
        completeness[column] = ratio

        if ratio < threshold:
            logger.warning(
                f"Column '{column}' is only {ratio:.1%} complete (threshold: {threshold:.1%})"
            )

    return completeness


def detect_outliers(
    series: pd.Series,
    method: str = "zscore",
    threshold: float = 3.0
) -> pd.Series:
    """
    Detect outliers in a numeric series.

    Args:
        series: Pandas Series to check
        method: Method to use ('zscore' or 'iqr')
        threshold: Threshold for outlier detection
            - For zscore: number of standard deviations (default: 3.0)
            - For IQR: multiplier for IQR (default: 1.5)

    Returns:
        Boolean Series indicating outliers

    Example:
        >>> outliers = detect_outliers(df["sales"], method="zscore")
        >>> df[outliers]  # View outlier rows
    """
    if method == "zscore":
        # Z-score method
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold

    elif method == "iqr":
        # Interquartile range method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return (series < lower_bound) | (series > upper_bound)

    else:
        raise ValueError(f"Unknown outlier detection method: {method}")


# ============================================================================
# METRIC CALCULATIONS
# ============================================================================

def calculate_growth_rate(
    current: float,
    previous: float,
    as_percentage: bool = False
) -> float:
    """
    Calculate growth rate between two values.

    Args:
        current: Current period value
        previous: Previous period value
        as_percentage: If True, return as percentage (e.g., 16.5 for 16.5%)

    Returns:
        Growth rate (decimal or percentage)

    Example:
        >>> calculate_growth_rate(116, 100, as_percentage=True)
        16.0  # 16% growth
    """
    if previous == 0:
        logger.warning("Previous value is zero, cannot calculate growth rate")
        return np.nan

    growth = (current - previous) / previous

    if as_percentage:
        return growth * 100
    else:
        return growth


def calculate_cagr(
    ending_value: float,
    beginning_value: float,
    num_periods: float
) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Args:
        ending_value: Final value
        beginning_value: Initial value
        num_periods: Number of periods (typically years)

    Returns:
        CAGR as a decimal

    Example:
        >>> cagr = calculate_cagr(150, 100, 3)  # 100 to 150 in 3 years
        >>> print(f"CAGR: {cagr:.1%}")
    """
    if beginning_value <= 0:
        raise ValueError("Beginning value must be positive")
    if num_periods <= 0:
        raise ValueError("Number of periods must be positive")

    cagr = (ending_value / beginning_value) ** (1 / num_periods) - 1
    return cagr


def calculate_variance(actual: float, target: float) -> Dict[str, float]:
    """
    Calculate variance between actual and target.

    Args:
        actual: Actual value
        target: Target value

    Returns:
        Dictionary with absolute and percentage variance

    Example:
        >>> variance = calculate_variance(actual=110, target=100)
        >>> print(f"Variance: {variance['percentage']:.1%}")
    """
    absolute_variance = actual - target
    percentage_variance = (actual - target) / target if target != 0 else np.nan

    return {
        "absolute": absolute_variance,
        "percentage": percentage_variance
    }


# ============================================================================
# DATA TRANSFORMATIONS
# ============================================================================

def aggregate_to_period(
    df: pd.DataFrame,
    date_column: str,
    period: str,
    agg_dict: Dict[str, Union[str, List[str]]]
) -> pd.DataFrame:
    """
    Aggregate data to a specific time period.

    Args:
        df: DataFrame with time series data
        date_column: Name of the date column
        period: Period to aggregate to ('D', 'W', 'M', 'Q', 'Y')
        agg_dict: Dictionary of {column: aggregation_function}

    Returns:
        Aggregated DataFrame

    Example:
        >>> monthly = aggregate_to_period(
        >>>     df,
        >>>     date_column="date",
        >>>     period="M",
        >>>     agg_dict={"sales": "sum", "quantity": "sum"}
        >>> )
    """
    df = df.copy()

    # Ensure date column is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column])

    # Set date as index
    df = df.set_index(date_column)

    # Aggregate
    aggregated = df.resample(period).agg(agg_dict)

    # Reset index
    aggregated = aggregated.reset_index()

    return aggregated


def pivot_by_dimensions(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: str,
    values: str,
    aggfunc: str = "sum"
) -> pd.DataFrame:
    """
    Create a pivot table with specified dimensions.

    Args:
        df: Source DataFrame
        index: Column(s) for pivot table index
        columns: Column for pivot table columns
        values: Column with values to aggregate
        aggfunc: Aggregation function

    Returns:
        Pivot table DataFrame

    Example:
        >>> pivot = pivot_by_dimensions(
        >>>     df,
        >>>     index="date",
        >>>     columns="category",
        >>>     values="sales",
        >>>     aggfunc="sum"
        >>> )
    """
    pivot_table = pd.pivot_table(
        df,
        index=index,
        columns=columns,
        values=values,
        aggfunc=aggfunc,
        fill_value=0
    )

    return pivot_table


# ============================================================================
# FILE OPERATIONS
# ============================================================================

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        path: Directory path

    Returns:
        Path object

    Example:
        >>> output_dir = ensure_directory("./output/reports")
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured directory exists: {path}")
    return path


def save_json(data: Any, filepath: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to a JSON file.

    Args:
        data: Data to save (must be JSON-serializable)
        filepath: Output file path
        indent: Indentation for pretty printing

    Example:
        >>> save_json({"targets": results}, "output/targets_2026.json")
    """
    filepath = Path(filepath)
    ensure_directory(filepath.parent)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=indent, default=str)

    logger.info(f"Saved JSON to {filepath}")


def load_json(filepath: Union[str, Path]) -> Any:
    """
    Load data from a JSON file.

    Args:
        filepath: Input file path

    Returns:
        Loaded data

    Example:
        >>> data = load_json("output/targets_2026.json")
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    with open(filepath, "r") as f:
        data = json.load(f)

    logger.debug(f"Loaded JSON from {filepath}")
    return data


# ============================================================================
# FORMATTING UTILITIES
# ============================================================================

def format_currency(amount: float, currency_symbol: str = "$") -> str:
    """
    Format a number as currency.

    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use

    Returns:
        Formatted currency string

    Example:
        >>> format_currency(1234567.89)
        "$1,234,567.89"
    """
    return f"{currency_symbol}{amount:,.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format a decimal as a percentage.

    Args:
        value: Decimal value (e.g., 0.165 for 16.5%)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string

    Example:
        >>> format_percentage(0.165)
        "16.5%"
    """
    return f"{value * 100:.{decimals}f}%"


def format_large_number(number: float, precision: int = 1) -> str:
    """
    Format large numbers with K, M, B suffixes.

    Args:
        number: Number to format
        precision: Decimal precision

    Returns:
        Formatted string

    Example:
        >>> format_large_number(1500000)
        "1.5M"
    """
    abs_number = abs(number)
    sign = "-" if number < 0 else ""

    if abs_number >= 1_000_000_000:
        return f"{sign}{abs_number / 1_000_000_000:.{precision}f}B"
    elif abs_number >= 1_000_000:
        return f"{sign}{abs_number / 1_000_000:.{precision}f}M"
    elif abs_number >= 1_000:
        return f"{sign}{abs_number / 1_000:.{precision}f}K"
    else:
        return f"{sign}{abs_number:.{precision}f}"


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Configuration
    "load_config",

    # Date/Time
    "get_date_range",
    "get_fiscal_year",
    "is_business_day",
    "add_business_days",

    # Validation
    "validate_dataframe",
    "check_data_completeness",
    "detect_outliers",

    # Metrics
    "calculate_growth_rate",
    "calculate_cagr",
    "calculate_variance",

    # Transformations
    "aggregate_to_period",
    "pivot_by_dimensions",

    # File Operations
    "ensure_directory",
    "save_json",
    "load_json",

    # Formatting
    "format_currency",
    "format_percentage",
    "format_large_number",
]
