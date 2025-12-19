"""
LVL-CODES: Sample Data Generator for Testing
================================================================================
This script generates realistic pet food sales data for testing and development
without requiring access to the actual data warehouse.

Generates:
    - 3-5 years of historical sales data
    - Multiple product categories and sub-groups
    - Regional distribution
    - Channel breakdown
    - Seasonal patterns
    - Growth trends
    - Returns data

Output:
    - CSV files that can be opened in Excel
    - Ready for immediate use in forecasting models

Usage:
    python scripts/generate_sample_data.py

    # Or import and use programmatically
    from scripts.generate_sample_data import generate_sales_data
    df = generate_sales_data(years=3)

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logging import get_logger, ProgressLogger

# Initialize logger
logger = get_logger(__name__)


def generate_sales_data(
    start_date: str = "2022-01-01",
    end_date: str = "2025-12-31",
    n_skus: int = 50,
    base_daily_sales: float = 100000,
    growth_rate: float = 0.12,
    seasonality_amplitude: float = 0.3,
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Generate realistic pet food sales data with seasonality and trends.

    This function creates synthetic sales data that mimics real pet food
    retail patterns including:
    - Seasonal variations (higher in winter/holidays)
    - Growth trends
    - Day-of-week effects
    - Category-specific patterns
    - Regional variations
    - Channel differences

    Args:
        start_date: Start date for data generation (YYYY-MM-DD)
        end_date: End date for data generation (YYYY-MM-DD)
        n_skus: Number of unique SKUs to generate
        base_daily_sales: Base daily sales amount (total across all SKUs)
        growth_rate: Annual growth rate (e.g., 0.12 for 12%)
        seasonality_amplitude: Strength of seasonal patterns (0-1)
        random_seed: Random seed for reproducibility

    Returns:
        DataFrame with columns:
            - date: Transaction date
            - sku_id: SKU identifier
            - category: Product category (Dog Food, Cat Food, etc.)
            - subgroup: Product sub-group (Dry, Wet, etc.)
            - region: Geographic region
            - channel: Sales channel
            - sales_amount: Gross sales amount
            - sales_quantity: Units sold
            - returns_amount: Returns amount
            - returns_quantity: Units returned
            - net_sales_amount: Sales minus returns
            - net_sales_quantity: Quantity minus returns

    Example:
        >>> df = generate_sales_data(years=3, n_skus=100)
        >>> df.to_csv("sample_sales.csv", index=False)
        >>> # Open sample_sales.csv in Excel to view
    """
    logger.info(f"Generating sample sales data from {start_date} to {end_date}")

    # Set random seed for reproducibility
    np.random.seed(random_seed)

    # ========================================================================
    # 1. DEFINE PRODUCT HIERARCHY
    # ========================================================================

    # Product categories with their market share
    categories = {
        "Dog Food": {
            "weight": 0.45,  # 45% of sales
            "subgroups": {
                "Dry Dog Food": 0.50,
                "Wet Dog Food": 0.30,
                "Grain-Free Dog": 0.15,
                "Organic Dog": 0.05
            },
            "seasonality": 1.2,  # Higher seasonality
            "growth": growth_rate * 1.1  # Slightly higher growth
        },
        "Cat Food": {
            "weight": 0.30,
            "subgroups": {
                "Dry Cat Food": 0.55,
                "Wet Cat Food": 0.35,
                "Grain-Free Cat": 0.08,
                "Organic Cat": 0.02
            },
            "seasonality": 1.0,
            "growth": growth_rate * 0.9
        },
        "Treats": {
            "weight": 0.15,
            "subgroups": {
                "Dog Treats": 0.60,
                "Cat Treats": 0.30,
                "Dental Chews": 0.10
            },
            "seasonality": 1.5,  # Very seasonal (holidays)
            "growth": growth_rate * 1.3
        },
        "Supplements": {
            "weight": 0.10,
            "subgroups": {
                "Vitamins": 0.40,
                "Joint Support": 0.35,
                "Digestive Health": 0.25
            },
            "seasonality": 0.8,
            "growth": growth_rate * 1.5  # Fast growing category
        }
    }

    # ========================================================================
    # 2. DEFINE GEOGRAPHIC REGIONS
    # ========================================================================

    regions = {
        "Northeast": 0.25,
        "Southeast": 0.30,
        "Midwest": 0.20,
        "West": 0.25
    }

    # ========================================================================
    # 3. DEFINE SALES CHANNELS
    # ========================================================================

    channels = {
        "Retail": 0.50,      # Traditional retail stores
        "E-commerce": 0.30,  # Online sales (growing fast)
        "Wholesale": 0.15,   # Wholesale/bulk
        "Distribution": 0.05 # Other distribution
    }

    # Channel growth rates (e-commerce growing faster)
    channel_growth = {
        "Retail": growth_rate * 0.8,
        "E-commerce": growth_rate * 2.0,  # Double growth rate
        "Wholesale": growth_rate * 0.6,
        "Distribution": growth_rate * 1.0
    }

    # ========================================================================
    # 4. GENERATE DATE RANGE
    # ========================================================================

    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    n_days = len(date_range)

    logger.info(f"Generating {n_days} days of data")

    # ========================================================================
    # 5. CREATE BASE SKU CATALOG
    # ========================================================================

    skus = []
    sku_id = 1

    for category, cat_info in categories.items():
        for subgroup, sub_weight in cat_info["subgroups"].items():
            # Number of SKUs for this subgroup
            n_skus_subgroup = max(1, int(n_skus * cat_info["weight"] * sub_weight))

            for i in range(n_skus_subgroup):
                skus.append({
                    "sku_id": f"SKU{sku_id:05d}",
                    "category": category,
                    "subgroup": subgroup,
                    "sku_name": f"{subgroup} Product {i+1}",
                    "category_weight": cat_info["weight"],
                    "subgroup_weight": sub_weight,
                    "seasonality_factor": cat_info["seasonality"],
                    "growth_rate": cat_info["growth"]
                })
                sku_id += 1

    skus_df = pd.DataFrame(skus)
    logger.info(f"Created {len(skus_df)} SKUs across {len(categories)} categories")

    # ========================================================================
    # 6. GENERATE SALES TRANSACTIONS
    # ========================================================================

    logger.info("Generating daily sales transactions...")
    progress = ProgressLogger("Generating sales data", total=n_days, log_every=20)

    all_transactions = []

    for day_idx, current_date in enumerate(date_range):
        # ====================================================================
        # CALCULATE TIME-BASED FACTORS
        # ====================================================================

        # Days since start (for trend)
        days_elapsed = (current_date - pd.to_datetime(start_date)).days
        years_elapsed = days_elapsed / 365.25

        # Trend growth factor
        trend_factor = (1 + growth_rate) ** years_elapsed

        # Seasonal factors
        month = current_date.month
        day_of_year = current_date.dayofyear

        # Annual seasonality (higher in Nov-Dec for holidays)
        annual_seasonal = 1 + seasonality_amplitude * np.sin(
            2 * np.pi * (day_of_year - 60) / 365  # Peak around Dec
        )

        # Weekly seasonality (higher on weekends)
        day_of_week = current_date.dayofweek
        weekly_seasonal = 1.0 + 0.15 * (day_of_week >= 5)  # +15% on Sat/Sun

        # Special events (Black Friday, Christmas, etc.)
        event_boost = 1.0
        if month == 11 and current_date.day >= 24:  # Black Friday week
            event_boost = 1.5
        elif month == 12 and current_date.day <= 25:  # Christmas shopping
            event_boost = 1.3

        # ====================================================================
        # GENERATE TRANSACTIONS FOR EACH DIMENSION COMBINATION
        # ====================================================================

        # Calculate total daily sales for this date
        daily_total = base_daily_sales * trend_factor * annual_seasonal * weekly_seasonal * event_boost

        # Distribute across SKUs, regions, and channels
        for _, sku in skus_df.iterrows():
            for region, region_weight in regions.items():
                for channel, channel_weight in channels.items():

                    # Calculate sales for this combination
                    sku_category_sales = daily_total * sku["category_weight"] * sku["subgroup_weight"]

                    # Apply channel growth
                    channel_trend = (1 + channel_growth[channel]) ** years_elapsed

                    # Apply SKU-specific seasonality
                    sku_seasonal = 1 + (sku["seasonality_factor"] - 1) * seasonality_amplitude * np.sin(
                        2 * np.pi * (day_of_year - 60) / 365
                    )

                    # Final sales amount
                    sales_amount = (
                        sku_category_sales
                        * region_weight
                        * channel_weight
                        * channel_trend
                        * sku_seasonal
                        * np.random.uniform(0.8, 1.2)  # Random variation ±20%
                    )

                    # Calculate quantity (assume average price per unit)
                    avg_price = np.random.uniform(10, 50)  # $10-$50 per unit
                    sales_quantity = max(1, int(sales_amount / avg_price))

                    # Calculate returns (2-5% return rate)
                    return_rate = np.random.uniform(0.02, 0.05)
                    returns_amount = sales_amount * return_rate
                    returns_quantity = max(0, int(sales_quantity * return_rate))

                    # Net sales
                    net_sales_amount = sales_amount - returns_amount
                    net_sales_quantity = sales_quantity - returns_quantity

                    # Create transaction record
                    all_transactions.append({
                        "date": current_date,
                        "sku_id": sku["sku_id"],
                        "category": sku["category"],
                        "subgroup": sku["subgroup"],
                        "sku_name": sku["sku_name"],
                        "region": region,
                        "channel": channel,
                        "sales_amount": round(sales_amount, 2),
                        "sales_quantity": sales_quantity,
                        "returns_amount": round(returns_amount, 2),
                        "returns_quantity": returns_quantity,
                        "net_sales_amount": round(net_sales_amount, 2),
                        "net_sales_quantity": net_sales_quantity
                    })

        # Update progress
        progress.update(day_idx + 1)

    progress.complete()

    # ========================================================================
    # 7. CREATE FINAL DATAFRAME
    # ========================================================================

    df = pd.DataFrame(all_transactions)

    # Add calculated fields
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["day_of_week"] = df["date"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    logger.info(f"Generated {len(df):,} transaction records")
    logger.info(f"Date range: {df['date'].min()} to {df['date'].max()}")
    logger.info(f"Total sales: ${df['sales_amount'].sum():,.2f}")
    logger.info(f"Total net sales: ${df['net_sales_amount'].sum():,.2f}")

    return df


def save_sample_data(df: pd.DataFrame, output_dir: str = "./data/sample") -> dict:
    """
    Save generated sample data to Excel-compatible CSV files.

    Creates multiple files for different aggregation levels that can be
    opened and analyzed in Excel.

    Args:
        df: Generated sales DataFrame
        output_dir: Directory to save files

    Returns:
        Dictionary with paths to saved files

    Example:
        >>> df = generate_sales_data()
        >>> files = save_sample_data(df)
        >>> # Open files["daily"] in Excel
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Saving sample data to {output_path}")

    saved_files = {}

    # ========================================================================
    # 1. DAILY TRANSACTION DATA (Full Detail)
    # ========================================================================

    daily_file = output_path / "sales_daily_transactions.csv"
    df.to_csv(daily_file, index=False)
    saved_files["daily"] = str(daily_file)
    logger.info(f"✓ Saved daily transactions: {daily_file}")

    # ========================================================================
    # 2. MONTHLY AGGREGATED DATA
    # ========================================================================

    monthly = df.groupby([
        pd.Grouper(key="date", freq="M"),
        "category", "subgroup", "region", "channel"
    ]).agg({
        "sales_amount": "sum",
        "sales_quantity": "sum",
        "returns_amount": "sum",
        "returns_quantity": "sum",
        "net_sales_amount": "sum",
        "net_sales_quantity": "sum",
        "sku_id": "nunique"
    }).reset_index()

    monthly = monthly.rename(columns={"sku_id": "distinct_skus"})

    monthly_file = output_path / "sales_monthly_aggregated.csv"
    monthly.to_csv(monthly_file, index=False)
    saved_files["monthly"] = str(monthly_file)
    logger.info(f"✓ Saved monthly aggregated: {monthly_file}")

    # ========================================================================
    # 3. CATEGORY SUMMARY
    # ========================================================================

    category_summary = df.groupby(["date", "category"]).agg({
        "net_sales_amount": "sum",
        "net_sales_quantity": "sum"
    }).reset_index()

    category_file = output_path / "sales_by_category.csv"
    category_summary.to_csv(category_file, index=False)
    saved_files["category"] = str(category_file)
    logger.info(f"✓ Saved category summary: {category_file}")

    # ========================================================================
    # 4. REGIONAL SUMMARY
    # ========================================================================

    regional_summary = df.groupby(["date", "region"]).agg({
        "net_sales_amount": "sum",
        "net_sales_quantity": "sum"
    }).reset_index()

    regional_file = output_path / "sales_by_region.csv"
    regional_summary.to_csv(regional_file, index=False)
    saved_files["regional"] = str(regional_file)
    logger.info(f"✓ Saved regional summary: {regional_file}")

    # ========================================================================
    # 5. CHANNEL SUMMARY
    # ========================================================================

    channel_summary = df.groupby(["date", "channel"]).agg({
        "net_sales_amount": "sum",
        "net_sales_quantity": "sum"
    }).reset_index()

    channel_file = output_path / "sales_by_channel.csv"
    channel_summary.to_csv(channel_file, index=False)
    saved_files["channel"] = str(channel_file)
    logger.info(f"✓ Saved channel summary: {channel_file}")

    # ========================================================================
    # 6. TIME SERIES (for quick forecasting)
    # ========================================================================

    timeseries = df.groupby("date").agg({
        "net_sales_amount": "sum"
    }).reset_index()
    timeseries.columns = ["date", "sales"]

    timeseries_file = output_path / "sales_timeseries.csv"
    timeseries.to_csv(timeseries_file, index=False)
    saved_files["timeseries"] = str(timeseries_file)
    logger.info(f"✓ Saved time series: {timeseries_file}")

    return saved_files


def main():
    """
    Main function to generate and save sample data.

    Run this script directly to generate sample data files.
    """
    print("="*80)
    print("LVL-CODES Sample Data Generator")
    print("="*80)
    print()

    # Generate sample data
    df = generate_sales_data(
        start_date="2022-01-01",
        end_date="2025-12-31",
        n_skus=50,
        base_daily_sales=100000,
        growth_rate=0.12,  # 12% annual growth
        seasonality_amplitude=0.3,
        random_seed=42
    )

    # Save to files
    files = save_sample_data(df)

    print()
    print("="*80)
    print("✓ Sample Data Generation Complete!")
    print("="*80)
    print()
    print("Generated Files (Open in Excel):")
    for name, path in files.items():
        print(f"  • {name:12s}: {path}")

    print()
    print("Quick Stats:")
    print(f"  • Total Records: {len(df):,}")
    print(f"  • Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"  • Total Sales: ${df['sales_amount'].sum():,.2f}")
    print(f"  • Net Sales: ${df['net_sales_amount'].sum():,.2f}")
    print(f"  • Categories: {df['category'].nunique()}")
    print(f"  • SKUs: {df['sku_id'].nunique()}")
    print(f"  • Regions: {df['region'].nunique()}")
    print(f"  • Channels: {df['channel'].nunique()}")
    print()
    print("📊 You can now open these CSV files in Excel to explore the data!")
    print()


if __name__ == "__main__":
    main()
