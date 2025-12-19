# Excel Integration Guide - Real-Time Monitoring

## Quick Start (5 Minutes)

### Step 1: Run the Demo

```bash
cd /home/user/LVL-CODES/LVL-STMS

# Make sure you're in the LVL-STMS directory
python scripts/demo_forecast_with_excel.py
```

The script will:
1. Generate 4 years of sample sales data (2022-2025)
2. Train SARIMA forecasting model
3. Generate 12-month forecast for 2026
4. Save everything to CSV files

**Total runtime**: ~60-90 seconds

---

### Step 2: Open Files in Excel

While the script runs (or after), open these CSV files in Excel:

#### Historical Data
```
LVL-STMS/data/sample/sales_timeseries.csv
```
- Simple time series: date + sales
- 1,461 rows (4 years of daily data)
- Ready for charting

#### 2026 Forecast
```
LVL-STMS/data/forecasts/forecast_2026_sarima.csv
```
- 12 months of forecast
- Includes 95% confidence intervals
- Columns: date, forecast, lower_95, upper_95

#### Combined View
```
LVL-STMS/data/forecasts/forecast_with_history.csv
```
- Historical + Forecast in one file
- Perfect for charts
- Type column shows "historical" vs "forecast"

---

### Step 3: Create a Forecast Chart in Excel

**Option A: Quick Chart**
1. Open `forecast_with_history.csv`
2. Select columns A (date), B (actual), and C (forecast)
3. Insert → Recommended Charts → Line Chart
4. Done! You now see historical vs forecast

**Option B: Chart with Confidence Bands**
1. Open `forecast_2026_sarima.csv`
2. Select all columns
3. Insert → Line Chart
4. Right-click forecast series → Add Error Bars
5. Custom → Specify lower_95 and upper_95

**Option C: Professional Dashboard**
1. Open `forecast_with_history.csv`
2. Insert → PivotChart
3. Axis: date
4. Values: actual, forecast
5. Add slicers for interactivity

---

## Real-Time Monitoring

### Watch Data Generate Live

1. **Open Excel FIRST** (before running script)

2. In Excel:
   - Data → Get Data → From Text/CSV
   - Navigate to: `LVL-STMS/data/sample/sales_timeseries.csv`
   - Click "Load"

3. **Run the script**:
   ```bash
   python scripts/demo_forecast_with_excel.py
   ```

4. **In Excel**: Right-click the table → Refresh
   - Watch the data populate row by row!

---

## Excel Analysis Examples

### Example 1: Monthly Sales Pivot Table

**File**: `data/sample/sales_monthly_aggregated.csv`

1. Open in Excel
2. Insert → PivotTable
3. Setup:
   - Rows: date, category
   - Values: net_sales_amount (Sum)
4. Result: Sales by month and category

### Example 2: Regional Comparison

**File**: `data/sample/sales_by_region.csv`

1. Open in Excel
2. Select data
3. Insert → Recommended Charts → Column Chart
4. Compare regions over time

### Example 3: Growth Analysis

**File**: `data/forecasts/forecast_summary.csv`

1. Open in Excel
2. Contains key metrics:
   - 2025 actual sales
   - 2026 forecast
   - Growth percentage
   - Model parameters

---

## Advanced Excel Features

### Auto-Refresh Data Connection

1. Data → Queries & Connections
2. Right-click your query → Properties
3. Check "Refresh every" → Set to 5 minutes
4. Excel will auto-update as files change!

### Create Dashboard

1. Create new workbook
2. Data → Get Data → From CSV
3. Load all forecast CSVs
4. Create relationships between tables
5. Build dashboard with:
   - KPI cards (total sales, growth %)
   - Line charts (forecast trend)
   - Bar charts (category comparison)
   - Slicers (filter by region, channel)

### Conditional Formatting

Highlight forecast values:
```
Home → Conditional Formatting → Color Scales
```

Show confidence intervals with error bars:
```
Chart → Add Chart Element → Error Bars → Custom
```

---

## File Reference

### Sample Data Files (`data/sample/`)

| File | Description | Rows | Use For |
|------|-------------|------|---------|
| `sales_daily_transactions.csv` | Full detail | ~460k | Deep analysis |
| `sales_monthly_aggregated.csv` | Monthly summary | 48 | Trends |
| `sales_by_category.csv` | Category breakdown | 5,844 | Category analysis |
| `sales_by_region.csv` | Regional breakdown | 5,844 | Regional analysis |
| `sales_by_channel.csv` | Channel breakdown | 5,844 | Channel analysis |
| `sales_timeseries.csv` | Simple time series | 1,461 | Quick forecasting |

### Forecast Files (`data/forecasts/`)

| File | Description | Use For |
|------|-------------|---------|
| `forecast_2026_sarima.csv` | 12-month forecast | Primary forecast |
| `forecast_with_history.csv` | Combined view | Charts |
| `forecast_summary.csv` | Statistics | Reporting |

---

## Formulas & Calculations

### Calculate Growth in Excel

```excel
// Growth percentage
=(forecast_2026 - actual_2025) / actual_2025

// Year-over-year growth
=(B2 - B1) / B1
```

### Moving Average

```excel
=AVERAGE(B2:B13)  // 12-month average
```

### Forecast Accuracy (after actuals available)

```excel
// MAPE (Mean Absolute Percentage Error)
=AVERAGE(ABS((actual - forecast) / actual))

// RMSE (Root Mean Squared Error)
=SQRT(AVERAGE((actual - forecast)^2))
```

---

## Troubleshooting

### File Won't Open
- Make sure script has finished running
- Check file exists at path
- Try "Open" vs "Import Data"

### Chart Looks Wrong
- Ensure date column is formatted as Date
- Check column headers are correct
- Remove any blank rows

### Can't Refresh Data
- Close and reopen file
- Data → Refresh All
- Check file path hasn't changed

---

## Tips & Tricks

### 1. Format Dates
```
Select date column → Format Cells → Date → "MMM YYYY"
```

### 2. Format Currency
```
Select sales columns → Format Cells → Currency → $
```

### 3. Create Sparklines
```
Insert → Sparklines → Line
Select range → Mini charts in cells!
```

### 4. Freeze Panes
```
View → Freeze Panes → Freeze Top Row
Scroll while keeping headers visible
```

### 5. Quick Sum
```
Select range → Look at bottom-right status bar
Shows: Sum, Average, Count
```

---

## What to Look For

### In the Data
- ✅ Seasonal patterns (higher in Nov-Dec)
- ✅ Growth trend (upward slope)
- ✅ Weekend spikes (Sat-Sun higher)
- ✅ Channel differences (e-commerce growing faster)

### In the Forecast
- ✅ Follows historical pattern
- ✅ Confidence bands widen over time (normal!)
- ✅ Growth rate ~12-16%
- ✅ Seasonal peaks in summer/holidays

---

## Next Steps

After exploring in Excel:

1. **Adjust Parameters**
   - Edit `config/models.yaml`
   - Change growth rate, seasonality
   - Re-run demo

2. **Try Different Models**
   - Prophet (coming soon)
   - XGBoost (coming soon)
   - Compare results

3. **Connect Real Data**
   - Provide database credentials
   - Use actual sales data
   - Generate real 2026 forecast

4. **Build Dashboard**
   - Power BI import
   - Tableau connection
   - Excel dashboard with slicers

---

## Support

**Can't find a file?**
```bash
cd /home/user/LVL-CODES/LVL-STMS
ls -la data/sample/
ls -la data/forecasts/
```

**Script failed?**
```bash
# Check logs
cat logs/lvl_codes.log

# Re-run with verbose output
python scripts/demo_forecast_with_excel.py
```

**Need help with Excel?**
- Microsoft Excel Help: F1 key
- Excel formulas: https://support.microsoft.com/excel
- Chart tutorials: YouTube → "Excel forecast chart"

---

**Happy Forecasting!** 📊📈

*Last Updated: 2025-12-17*
*LVL-CODES Analytics Team*
