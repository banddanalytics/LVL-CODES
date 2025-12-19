"""
LVL-CODES: Demo Script - SARIMA Forecasting with Excel Integration
================================================================================
This demo script showcases the complete forecasting workflow and saves all
results to Excel-compatible CSV files that you can monitor in real-time.

What this script does:
    1. Generates realistic sample sales data (2022-2025)
    2. Trains SARIMA forecasting model
    3. Generates 2026 forecasts
    4. Saves everything to CSV files (open in Excel!)
    5. Creates visualization-ready data

You can:
    - Open the CSV files in Excel while the script runs
    - Refresh Excel to see updates
    - Create pivot tables and charts
    - Analyze results interactively

Usage:
    python scripts/demo_forecast_with_excel.py

Then open the generated CSV files in Excel:
    - data/sample/sales_timeseries.csv (historical data)
    - data/forecasts/forecast_2026_sarima.csv (forecast)
    - data/forecasts/forecast_with_history.csv (combined view)

Author: LVL-CODES Analytics Team
Version: 1.0.0
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_sample_data import generate_sales_data, save_sample_data
from src.models.sarima import SARIMAForecaster
from src.utils.logging import get_logger

# Initialize logger
logger = get_logger(__name__)


def print_header(title: str):
    """Print a formatted header."""
    print()
    print("="*80)
    print(title.center(80))
    print("="*80)
    print()


def print_section(title: str):
    """Print a section header."""
    print()
    print(f"{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}")


def main():
    """
    Run complete forecasting demo with Excel integration.
    """
    print_header("LVL-CODES: SARIMA Forecasting Demo with Excel Integration")

    print("This demo will:")
    print("  1. Generate 4 years of sample pet food sales data (2022-2025)")
    print("  2. Train SARIMA forecasting model")
    print("  3. Generate 12-month forecast for 2026")
    print("  4. Save all results to CSV files you can open in Excel")
    print()
    print("📊 You can open Excel now and load the CSV files as they're created!")
    print()
    input("Press Enter to continue...")

    # ========================================================================
    # STEP 1: GENERATE SAMPLE DATA
    # ========================================================================

    print_section("Step 1: Generating Sample Sales Data")

    print("Generating realistic pet food sales data...")
    print("  • Date Range: 2022-01-01 to 2025-12-31 (4 years)")
    print("  • Categories: Dog Food, Cat Food, Treats, Supplements")
    print("  • Regions: Northeast, Southeast, Midwest, West")
    print("  • Channels: Retail, E-commerce, Wholesale, Distribution")
    print("  • Features: Seasonality, growth trends, day-of-week effects")
    print()

    # Generate data
    df_all = generate_sales_data(
        start_date="2022-01-01",
        end_date="2025-12-31",
        n_skus=50,
        base_daily_sales=100000,
        growth_rate=0.12,  # 12% historical growth
        seasonality_amplitude=0.3,
        random_seed=42
    )

    # Save to files
    print("\nSaving data to CSV files...")
    files = save_sample_data(df_all, output_dir="./data/sample")

    print("\n✓ Sample data generated and saved!")
    print("\n📁 Files you can open in Excel:")
    for name, path in files.items():
        print(f"   • {path}")

    print("\n💡 TIP: Open 'sales_timeseries.csv' in Excel to see the data!")
    print()
    input("Press Enter to continue to forecasting...")

    # ========================================================================
    # STEP 2: PREPARE DATA FOR FORECASTING
    # ========================================================================

    print_section("Step 2: Preparing Data for Forecasting")

    # Load time series data
    timeseries_path = files["timeseries"]
    df_ts = pd.read_csv(timeseries_path, parse_dates=["date"])
    df_ts = df_ts.set_index("date")

    print(f"Loaded time series data:")
    print(f"  • Observations: {len(df_ts):,}")
    print(f"  • Date Range: {df_ts.index.min().date()} to {df_ts.index.max().date()}")
    print(f"  • Total Sales: ${df_ts['sales'].sum():,.2f}")
    print(f"  • Average Daily Sales: ${df_ts['sales'].mean():,.2f}")
    print(f"  • Min Daily Sales: ${df_ts['sales'].min():,.2f}")
    print(f"  • Max Daily Sales: ${df_ts['sales'].max():,.2f}")

    # Aggregate to monthly (better for SARIMA with limited data)
    print("\nAggregating to monthly frequency for better forecasting...")
    df_monthly = df_ts.resample('M').sum()

    print(f"\nMonthly data:")
    print(f"  • Observations: {len(df_monthly)}")
    print(f"  • Average Monthly Sales: ${df_monthly['sales'].mean():,.2f}")

    print()
    input("Press Enter to start model training...")

    # ========================================================================
    # STEP 3: TRAIN SARIMA MODEL
    # ========================================================================

    print_section("Step 3: Training SARIMA Forecasting Model")

    print("Initializing SARIMA forecaster...")
    print("  • Auto-ARIMA will find optimal parameters")
    print("  • Seasonal period: m=12 (monthly data, yearly seasonality)")
    print("  • This may take 30-60 seconds...")
    print()

    # Create and train model
    forecaster = SARIMAForecaster()

    print("Training model (Auto-ARIMA searching for best parameters)...")
    forecaster.fit(df_monthly, target_col="sales", seasonal_period=12)

    # Show model summary
    print("\n" + forecaster.get_model_summary())

    print()
    input("Press Enter to generate 2026 forecast...")

    # ========================================================================
    # STEP 4: GENERATE 2026 FORECAST
    # ========================================================================

    print_section("Step 4: Generating 2026 Forecast")

    print("Generating 12-month forecast for 2026...")
    print("  • Forecast horizon: 12 months (Jan 2026 - Dec 2026)")
    print("  • Includes 95% confidence intervals")
    print()

    # Generate forecast with confidence intervals
    forecast, conf_int = forecaster.predict(
        horizon=12,
        frequency="M",
        return_conf_int=True
    )

    # Display forecast
    print("✓ Forecast generated!\n")
    print("2026 Monthly Forecast:")
    print("─" * 70)
    print(f"{'Month':<15} {'Forecast':<15} {'Lower 95%':<15} {'Upper 95%':<15}")
    print("─" * 70)

    for date, value in forecast.items():
        lower = conf_int.loc[date, "lower"]
        upper = conf_int.loc[date, "upper"]
        print(f"{date.strftime('%Y-%m'):<15} ${value:>12,.0f} ${lower:>12,.0f} ${upper:>12,.0f}")

    print("─" * 70)
    print(f"{'Total 2026':<15} ${forecast.sum():>12,.0f}")
    print("─" * 70)

    # Calculate growth vs 2025
    sales_2025 = df_monthly.loc["2025", "sales"].sum()
    forecast_2026 = forecast.sum()
    growth = (forecast_2026 - sales_2025) / sales_2025

    print(f"\n2025 Actual Sales: ${sales_2025:,.0f}")
    print(f"2026 Forecast Sales: ${forecast_2026:,.0f}")
    print(f"Projected Growth: {growth:.1%}")

    print()
    input("Press Enter to save forecast to Excel files...")

    # ========================================================================
    # STEP 5: SAVE FORECAST TO EXCEL-COMPATIBLE FILES
    # ========================================================================

    print_section("Step 5: Saving Forecast to Excel Files")

    # Create forecasts directory
    forecast_dir = Path("./data/forecasts")
    forecast_dir.mkdir(parents=True, exist_ok=True)

    # ────────────────────────────────────────────────────────────────────────
    # File 1: Forecast only
    # ────────────────────────────────────────────────────────────────────────

    forecast_file = forecast_dir / "forecast_2026_sarima.csv"

    forecast_df = pd.DataFrame({
        "date": forecast.index,
        "forecast": forecast.values,
        "lower_95": conf_int["lower"].values,
        "upper_95": conf_int["upper"].values
    })

    forecast_df.to_csv(forecast_file, index=False)
    print(f"✓ Saved forecast: {forecast_file}")

    # ────────────────────────────────────────────────────────────────────────
    # File 2: Historical + Forecast combined
    # ────────────────────────────────────────────────────────────────────────

    combined_file = forecast_dir / "forecast_with_history.csv"

    # Historical data
    historical = df_monthly.reset_index()
    historical.columns = ["date", "actual"]
    historical["forecast"] = np.nan
    historical["lower_95"] = np.nan
    historical["upper_95"] = np.nan
    historical["type"] = "historical"

    # Forecast data
    forecast_data = pd.DataFrame({
        "date": forecast.index,
        "actual": np.nan,
        "forecast": forecast.values,
        "lower_95": conf_int["lower"].values,
        "upper_95": conf_int["upper"].values,
        "type": "forecast"
    })

    # Combine
    combined = pd.concat([historical, forecast_data], ignore_index=True)
    combined = combined.sort_values("date")

    combined.to_csv(combined_file, index=False)
    print(f"✓ Saved combined view: {combined_file}")

    # ────────────────────────────────────────────────────────────────────────
    # File 3: Summary statistics
    # ────────────────────────────────────────────────────────────────────────

    summary_file = forecast_dir / "forecast_summary.csv"

    summary_data = {
        "Metric": [
            "Historical Period Start",
            "Historical Period End",
            "Forecast Period Start",
            "Forecast Period End",
            "Total 2025 Sales",
            "Total 2026 Forecast",
            "Growth Amount",
            "Growth Percentage",
            "Average Monthly (2025)",
            "Average Monthly (2026)",
            "Model Type",
            "Model Parameters",
            "AIC",
            "BIC"
        ],
        "Value": [
            df_monthly.index.min().strftime("%Y-%m"),
            df_monthly.index.max().strftime("%Y-%m"),
            forecast.index.min().strftime("%Y-%m"),
            forecast.index.max().strftime("%Y-%m"),
            f"${sales_2025:,.0f}",
            f"${forecast_2026:,.0f}",
            f"${forecast_2026 - sales_2025:,.0f}",
            f"{growth:.1%}",
            f"${sales_2025/12:,.0f}",
            f"${forecast_2026/12:,.0f}",
            "SARIMA",
            str(forecaster.model_params),
            f"{forecaster.aic:.2f}",
            f"{forecaster.bic:.2f}"
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(summary_file, index=False)
    print(f"✓ Saved summary: {summary_file}")

    # ========================================================================
    # STEP 6: FINAL INSTRUCTIONS
    # ========================================================================

    print_header("✓ Demo Complete!")

    print("📊 OPEN THESE FILES IN EXCEL:\n")
    print("1. Historical Data:")
    print(f"   {files['timeseries']}")
    print(f"   {files['monthly']}")
    print()
    print("2. 2026 Forecast:")
    print(f"   {forecast_file}")
    print()
    print("3. Combined View (History + Forecast):")
    print(f"   {combined_file}")
    print()
    print("4. Summary Statistics:")
    print(f"   {summary_file}")
    print()

    print("💡 EXCEL TIPS:\n")
    print("  • Create a line chart with 'date' on X-axis and 'forecast' on Y-axis")
    print("  • Add 'lower_95' and 'upper_95' as error bars or separate lines")
    print("  • Use pivot tables to analyze by category/region/channel")
    print("  • Create dashboard with slicers for interactive filtering")
    print()

    print("🎯 NEXT STEPS:\n")
    print("  • Analyze forecast accuracy")
    print("  • Adjust targets to hit 16% net growth")
    print("  • Run different scenarios (best/base/worst case)")
    print("  • Connect to your actual database")
    print("  • Implement other forecasting models (Prophet, XGBoost)")
    print()

    print("="*80)
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
