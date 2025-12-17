"""
LVL-CODES: Sales Data ETL Pipeline
================================================================================
This module handles the Extract, Transform, Load (ETL) process for sales data
from the data warehouse. It prepares data for forecasting and analysis.

Features:
    - Extract historical sales data
    - Clean and validate data
    - Create derived features
    - Handle missing values and outliers
    - Aggregate to different time periods
    - Load processed data for modeling

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from src.data.connectors.database_connector import DatabaseConnector
from src.utils.logging import get_logger, log_step, ProgressLogger
from src.utils.helpers import (
    validate_dataframe,
    check_data_completeness,
    detect_outliers,
    aggregate_to_period
)
from src.utils.constants import (
    TableNames,
    ColumnNames,
    MIN_DATA_COMPLETENESS,
    OUTLIER_Z_SCORE_THRESHOLD
)

# Initialize logger
logger = get_logger(__name__)


class SalesDataETL:
    """
    ETL pipeline for sales data processing.

    This class handles the complete ETL workflow:
        1. Extract data from database
        2. Transform and clean data
        3. Load processed data for analysis

    Example:
        >>> db = DatabaseConnector()
        >>> etl = SalesDataETL(db)
        >>> df = etl.run_pipeline(
        >>>     start_date="2021-01-01",
        >>>     end_date="2025-12-31"
        >>> )
    """

    def __init__(self, db_connector: DatabaseConnector):
        """
        Initialize ETL pipeline.

        Args:
            db_connector: Database connector instance
        """
        self.db = db_connector
        logger.info("SalesDataETL initialized")

    @log_step("Extract Sales Data")
    def extract_sales_data(
        self,
        start_date: str,
        end_date: str,
        categories: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        channels: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Extract sales data from the data warehouse.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            categories: Optional list of categories to filter
            regions: Optional list of regions to filter
            channels: Optional list of channels to filter

        Returns:
            DataFrame with raw sales data

        Raises:
            ValueError: If date range is invalid
        """
        logger.info(f"Extracting sales data from {start_date} to {end_date}")

        # Build WHERE clause
        where_conditions = [f"date >= '{start_date}'", f"date <= '{end_date}'"]

        if categories:
            categories_str = "', '".join(categories)
            where_conditions.append(f"category IN ('{categories_str}')")

        if regions:
            regions_str = "', '".join(regions)
            where_conditions.append(f"region IN ('{regions_str}')")

        if channels:
            channels_str = "', '".join(channels)
            where_conditions.append(f"channel IN ('{channels_str}')")

        where_clause = " AND ".join(where_conditions)

        # Extract data
        query = f"""
            SELECT
                s.date,
                s.sku_id,
                p.category,
                p.subgroup,
                p.sku_name,
                g.region,
                g.territory,
                c.channel,
                s.sales_amount,
                s.sales_quantity,
                COALESCE(r.returns_amount, 0) as returns_amount,
                COALESCE(r.returns_quantity, 0) as returns_quantity,
                s.sales_amount - COALESCE(r.returns_amount, 0) as net_sales_amount,
                s.sales_quantity - COALESCE(r.returns_quantity, 0) as net_sales_quantity
            FROM {TableNames.SALES_TRANSACTIONS} s
            LEFT JOIN {TableNames.PRODUCTS} p ON s.sku_id = p.sku_id
            LEFT JOIN {TableNames.GEOGRAPHY} g ON s.region_id = g.region_id
            LEFT JOIN {TableNames.CHANNELS} c ON s.channel_id = c.channel_id
            LEFT JOIN {TableNames.RETURNS} r ON s.date = r.date AND s.sku_id = r.sku_id
            WHERE {where_clause}
        """

        df = self.db.query_to_dataframe(query, parse_dates=["date"])

        logger.info(f"Extracted {len(df):,} rows of sales data")
        return df

    @log_step("Transform Data")
    def transform_data(
        self,
        df: pd.DataFrame,
        handle_missing: bool = True,
        handle_outliers: bool = True,
        create_features: bool = True
    ) -> pd.DataFrame:
        """
        Transform and clean sales data.

        Performs:
            - Data validation
            - Missing value handling
            - Outlier treatment
            - Feature engineering

        Args:
            df: Raw sales DataFrame
            handle_missing: Whether to handle missing values
            handle_outliers: Whether to handle outliers
            create_features: Whether to create derived features

        Returns:
            Transformed DataFrame
        """
        logger.info("Transforming sales data")
        df = df.copy()

        # ====================================================================
        # 1. DATA VALIDATION
        # ====================================================================
        required_cols = [
            "date", "sku_id", "category", "region", "channel",
            "sales_amount", "net_sales_amount"
        ]

        is_valid, errors = validate_dataframe(
            df,
            required_columns=required_cols,
            date_columns=["date"],
            numeric_columns=["sales_amount", "net_sales_amount"]
        )

        if not is_valid:
            logger.error(f"Data validation failed: {errors}")
            raise ValueError(f"Data validation errors: {errors}")

        # ====================================================================
        # 2. HANDLE MISSING VALUES
        # ====================================================================
        if handle_missing:
            logger.info("Handling missing values")

            # Check completeness
            completeness = check_data_completeness(df, threshold=MIN_DATA_COMPLETENESS)

            # Fill missing categorical values
            categorical_cols = ["category", "subgroup", "region", "territory", "channel"]
            for col in categorical_cols:
                if col in df.columns:
                    df[col] = df[col].fillna("Unknown")

            # Fill missing numeric values with 0 (for returns, etc.)
            numeric_cols = ["returns_amount", "returns_quantity"]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].fillna(0)

        # ====================================================================
        # 3. HANDLE OUTLIERS
        # ====================================================================
        if handle_outliers:
            logger.info("Detecting and handling outliers")

            # Detect outliers in sales amount
            outliers = detect_outliers(
                df["sales_amount"],
                method="zscore",
                threshold=OUTLIER_Z_SCORE_THRESHOLD
            )

            outlier_count = outliers.sum()
            if outlier_count > 0:
                logger.warning(f"Found {outlier_count} outliers in sales_amount")

                # Cap outliers at 99th percentile (or remove them)
                upper_cap = df["sales_amount"].quantile(0.99)
                df.loc[outliers, "sales_amount"] = upper_cap

        # ====================================================================
        # 4. CREATE DERIVED FEATURES
        # ====================================================================
        if create_features:
            logger.info("Creating derived features")

            # Temporal features
            df["year"] = df["date"].dt.year
            df["month"] = df["date"].dt.month
            df["quarter"] = df["date"].dt.quarter
            df["day_of_week"] = df["date"].dt.dayofweek
            df["day_of_month"] = df["date"].dt.day
            df["day_of_year"] = df["date"].dt.dayofyear
            df["week_of_year"] = df["date"].dt.isocalendar().week
            df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
            df["is_month_start"] = df["date"].dt.is_month_start.astype(int)
            df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
            df["is_quarter_start"] = df["date"].dt.is_quarter_start.astype(int)
            df["is_quarter_end"] = df["date"].dt.is_quarter_end.astype(int)

            # Return rate
            df["return_rate"] = np.where(
                df["sales_amount"] > 0,
                df["returns_amount"] / df["sales_amount"],
                0
            )

            # Average unit price
            df["avg_unit_price"] = np.where(
                df["sales_quantity"] > 0,
                df["sales_amount"] / df["sales_quantity"],
                0
            )

        logger.info(f"Transformation complete. Final shape: {df.shape}")
        return df

    @log_step("Aggregate Data")
    def aggregate_data(
        self,
        df: pd.DataFrame,
        period: str = "D",
        group_by: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Aggregate sales data to a specific time period.

        Args:
            df: Transformed sales DataFrame
            period: Aggregation period ('D'=daily, 'W'=weekly, 'M'=monthly)
            group_by: Additional columns to group by (e.g., ['category', 'region'])

        Returns:
            Aggregated DataFrame

        Example:
            >>> # Aggregate to monthly by category and region
            >>> monthly = etl.aggregate_data(
            >>>     df,
            >>>     period="M",
            >>>     group_by=["category", "region"]
            >>> )
        """
        logger.info(f"Aggregating data to {period} period")

        # Define aggregation functions
        agg_dict = {
            "sales_amount": "sum",
            "sales_quantity": "sum",
            "returns_amount": "sum",
            "returns_quantity": "sum",
            "net_sales_amount": "sum",
            "net_sales_quantity": "sum",
            "sku_id": "nunique",  # Distinct SKUs
        }

        # Group by date period and additional dimensions
        if group_by:
            groupby_cols = ["date"] + group_by
        else:
            groupby_cols = ["date"]

        # Ensure date is datetime
        df["date"] = pd.to_datetime(df["date"])

        # Set date as index for resampling
        df_indexed = df.set_index("date")

        # Group by additional dimensions if specified
        if group_by:
            # Group and resample
            aggregated = (
                df_indexed
                .groupby(group_by)
                .resample(period)
                .agg(agg_dict)
                .reset_index()
            )
        else:
            # Just resample
            aggregated = (
                df_indexed
                .resample(period)
                .agg(agg_dict)
                .reset_index()
            )

        # Rename distinct SKU column
        aggregated = aggregated.rename(columns={"sku_id": "distinct_skus"})

        logger.info(f"Aggregation complete. Shape: {aggregated.shape}")
        return aggregated

    def run_pipeline(
        self,
        start_date: str,
        end_date: str,
        categories: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        channels: Optional[List[str]] = None,
        period: str = "D",
        group_by: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Run the complete ETL pipeline.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            categories: Optional category filter
            regions: Optional region filter
            channels: Optional channel filter
            period: Aggregation period
            group_by: Grouping dimensions

        Returns:
            Processed and aggregated DataFrame ready for modeling

        Example:
            >>> db = DatabaseConnector()
            >>> etl = SalesDataETL(db)
            >>> df = etl.run_pipeline(
            >>>     start_date="2021-01-01",
            >>>     end_date="2025-12-31",
            >>>     period="M",
            >>>     group_by=["category", "region"]
            >>> )
        """
        logger.info("="*80)
        logger.info("Starting ETL Pipeline")
        logger.info("="*80)

        # Extract
        df_raw = self.extract_sales_data(
            start_date=start_date,
            end_date=end_date,
            categories=categories,
            regions=regions,
            channels=channels
        )

        # Transform
        df_transformed = self.transform_data(df_raw)

        # Aggregate
        df_final = self.aggregate_data(
            df_transformed,
            period=period,
            group_by=group_by
        )

        logger.info("="*80)
        logger.info("ETL Pipeline Complete")
        logger.info("="*80)

        return df_final


# ============================================================================
# CONVENIENCE FUNCTION
# ============================================================================

def load_sales_data(
    start_date: str,
    end_date: str,
    period: str = "M",
    group_by: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Convenience function to load and process sales data.

    Args:
        start_date: Start date
        end_date: End date
        period: Aggregation period
        group_by: Grouping dimensions

    Returns:
        Processed DataFrame

    Example:
        >>> df = load_sales_data(
        >>>     start_date="2021-01-01",
        >>>     end_date="2025-12-31",
        >>>     period="M"
        >>> )
    """
    with DatabaseConnector() as db:
        etl = SalesDataETL(db)
        return etl.run_pipeline(
            start_date=start_date,
            end_date=end_date,
            period=period,
            group_by=group_by
        )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "SalesDataETL",
    "load_sales_data",
]
