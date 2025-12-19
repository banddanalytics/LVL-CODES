# LVL-STMS Scripts

Utility scripts for the Sales Target Management System.

## Available Scripts

### `generate_sample_data.py`
Generates realistic pet food sales data for testing and development.

**Usage:**
```bash
python scripts/generate_sample_data.py
```

**Output:** CSV files in `data/sample/` that can be opened in Excel:
- `sales_daily_transactions.csv` - Full detail daily data
- `sales_monthly_aggregated.csv` - Monthly summaries
- `sales_by_category.csv` - Category breakdown
- `sales_by_region.csv` - Regional breakdown
- `sales_by_channel.csv` - Channel breakdown
- `sales_timeseries.csv` - Simple time series (for quick forecasting)

### `demo_forecast_with_excel.py` ⭐
**Complete end-to-end demo with Excel integration**

Interactive demo that:
1. Generates sample sales data (2022-2025)
2. Trains SARIMA forecasting model
3. Generates 2026 forecasts
4. Saves everything to Excel-compatible CSV files
5. Shows live progress you can monitor

**Usage:**
```bash
python scripts/demo_forecast_with_excel.py
```

**Output:** Forecast files in `data/forecasts/`:
- `forecast_2026_sarima.csv` - Forecast with confidence intervals
- `forecast_with_history.csv` - Combined historical + forecast
- `forecast_summary.csv` - Summary statistics

**Excel Integration:**
- Open CSV files in Excel while script runs
- Refresh to see updates
- Create charts and pivot tables
- Analyze results interactively

## Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the demo:
   ```bash
   python scripts/demo_forecast_with_excel.py
   ```

3. Open the generated CSV files in Excel:
   - `data/sample/sales_timeseries.csv`
   - `data/forecasts/forecast_2026_sarima.csv`
   - `data/forecasts/forecast_with_history.csv`

4. Create charts in Excel:
   - Select date and forecast columns
   - Insert → Line Chart
   - Add lower_95 and upper_95 for confidence bands

## Excel Tips

### Create a Forecast Chart
1. Open `forecast_with_history.csv` in Excel
2. Select columns: date, actual, forecast
3. Insert → Recommended Charts → Line Chart
4. Add error bars using lower_95 and upper_95 columns

### Create a Pivot Table
1. Open `sales_monthly_aggregated.csv` in Excel
2. Insert → PivotTable
3. Rows: date, category
4. Values: net_sales_amount (sum)
5. Analyze sales by category over time

### Auto-Refresh Data
1. Data → Get Data → From Text/CSV
2. Select your CSV file
3. Load
4. Right-click table → Refresh to update with latest data

## Notes

- All CSV files are Excel-compatible
- Scripts are heavily commented for learning
- Sample data is realistic with seasonality and trends
- Safe to run multiple times (overwrites previous output)

---

**Author:** LVL-CODES Analytics Team
**Version:** 1.0.0
