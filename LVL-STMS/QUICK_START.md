# LVL-STMS Quick Start Guide

Get up and running with forecasting in 5 minutes!

---

## 🚀 Option 1: Demo with Sample Data (No Database Needed)

**Best for**: Testing, learning, immediate results

```bash
cd /home/user/LVL-CODES/LVL-STMS

# Run interactive demo
python scripts/demo_forecast_with_excel.py
```

**What happens**:
1. Generates 4 years of realistic pet food sales data
2. Trains SARIMA forecasting model
3. Creates 2026 forecast (12 months)
4. Saves to CSV files you can open in Excel

**Time**: 2-3 minutes

**Output files**:
- `data/sample/sales_timeseries.csv` - Historical data
- `data/forecasts/forecast_2026_sarima.csv` - 12-month forecast
- `data/forecasts/forecast_with_history.csv` - Combined view

**Then**: Open CSV files in Excel, create charts!

---

## 🔌 Option 2: Connect to SAP Business One

**Best for**: Real forecasts with your actual data

### Step 1: Configure Database Connection

Edit `.env` file:
```bash
cd /home/user/LVL-CODES/LVL-STMS
nano .env
```

Add:
```
SAP_B1_SERVER=your_sap_server
SAP_B1_DATABASE=your_company_db
SAP_B1_USER=your_username
SAP_B1_PASSWORD=your_password
```

### Step 2: Customize SQL Query

1. Open `sql/sap_b1_sales_extract.sql`
2. Find YOUR item group codes:
   ```sql
   SELECT * FROM OITG
   ```
3. Update category mapping (lines 50-56)
4. Update territory mapping (lines 75-81)
5. Update channel mapping (lines 86-95)

**See**: `sql/README.md` for detailed instructions

### Step 3: Extract Data

**Manual**:
1. Run `sql/sap_b1_sales_extract.sql` in SSMS
2. Export to CSV
3. Save as `data/raw/sap_sales.csv`

**Automated** (recommended):
```bash
python scripts/extract_from_sap_b1.py --start-date 2022-01-01 --end-date 2025-12-31
```

### Step 4: Generate Forecast

```python
import pandas as pd
from src.models.sarima import SARIMAForecaster

# Load your data
df = pd.read_csv('data/raw/sap_b1_timeseries.csv', parse_dates=['date'])
df = df.set_index('date')

# Train model
forecaster = SARIMAForecaster()
forecaster.fit(df, target_col='sales')

# Forecast 2026
forecast = forecaster.predict(horizon=12)

# Save
forecast.to_csv('data/forecasts/my_2026_forecast.csv')
```

---

## 📊 Excel Integration

### Quick Chart

1. Open `data/forecasts/forecast_with_history.csv` in Excel
2. Select columns: date, actual, forecast
3. Insert → Line Chart
4. Done!

### With Confidence Bands

1. Open `data/forecasts/forecast_2026_sarima.csv`
2. Select all columns
3. Insert → Line Chart
4. Right-click forecast → Add Error Bars
5. Custom → Use lower_95 and upper_95

**See**: `EXCEL_GUIDE.md` for complete Excel instructions

---

## 📁 Key Files Reference

| File | Purpose |
|------|---------|
| `scripts/demo_forecast_with_excel.py` | Run demo with sample data |
| `scripts/generate_sample_data.py` | Generate test data |
| `scripts/extract_from_sap_b1.py` | Extract from SAP B1 |
| `sql/sap_b1_sales_extract.sql` | SAP B1 SQL query (comprehensive) |
| `sql/sap_b1_simple_extract.sql` | SAP B1 SQL query (simplified) |
| `src/models/sarima/sarima_forecaster.py` | SARIMA forecasting model |

---

## 📚 Documentation

| Guide | Description |
|-------|-------------|
| `README.md` | Project overview |
| `DEPLOYMENT_GUIDE.md` | Complete setup guide |
| `EXCEL_GUIDE.md` | Excel integration guide |
| `PROJECT_STATUS.md` | Current status & roadmap |
| `sql/README.md` | SAP B1 customization guide |
| `scripts/README.md` | Scripts usage guide |

---

## 🎯 Common Tasks

### Generate Sample Data Only
```bash
python scripts/generate_sample_data.py
```

### Train Model on Custom Data
```python
from src.models.sarima import SARIMAForecaster
import pandas as pd

df = pd.read_csv('your_data.csv', parse_dates=['date'], index_col='date')
forecaster = SARIMAForecaster()
forecaster.fit(df, target_col='sales')
forecast = forecaster.predict(horizon=12)
```

### Extract from SAP B1 (One Month)
```bash
python scripts/extract_from_sap_b1.py \
    --start-date 2025-01-01 \
    --end-date 2025-01-31 \
    --output-dir data/test
```

---

## ❓ Troubleshooting

### "No module named 'src'"
```bash
cd /home/user/LVL-CODES/LVL-STMS
pip install -e .
```

### "Cannot connect to SAP B1"
- Check credentials in `.env`
- Verify server is accessible
- Test with SSMS first

### "Query returns no data"
- Check date range in SQL
- Verify tables exist: `SELECT * FROM OINV`
- Check permissions

### "Files not generating"
```bash
# Check you're in right directory
cd /home/user/LVL-CODES/LVL-STMS
pwd

# List generated files
ls -la data/sample/
ls -la data/forecasts/
```

---

## 🚦 Next Steps

**After running demo**:
1. ✅ Open CSV files in Excel
2. ✅ Create forecast charts
3. ✅ Analyze results
4. ✅ Connect to SAP B1
5. ✅ Generate real 2026 forecast
6. ✅ Apply 16% growth target

**Future enhancements**:
- Add Prophet forecasting model
- Add XGBoost forecasting model
- Build ensemble forecaster
- Create target allocation system
- Build interactive dashboard

---

## 📞 Need Help?

**Check these first**:
- `DEPLOYMENT_GUIDE.md` - Setup instructions
- `EXCEL_GUIDE.md` - Excel integration
- `sql/README.md` - SAP B1 customization

**Still stuck?**
- Check logs: `cat logs/lvl_codes.log`
- Review error messages
- Contact LVL-CODES Analytics Team

---

**Ready to get started?** Run the demo now:

```bash
cd /home/user/LVL-CODES/LVL-STMS
python scripts/demo_forecast_with_excel.py
```

Then open the CSV files in Excel! 📊📈

---

**Last Updated**: 2025-12-17
**Version**: 1.0.0
