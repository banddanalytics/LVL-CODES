# LVL-CODES: 2026 Sales Targets - Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Database Setup](#database-setup)
5. [Configuration](#configuration)
6. [Running the System](#running-the-system)
7. [Usage Examples](#usage-examples)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## Overview

This guide walks you through deploying the LVL-CODES 2026 Sales Target Management System. The system provides:

- **Multi-model forecasting** (SARIMA, Prophet, XGBoost, LightGBM, Random Forest, Ensemble)
- **Target allocation** with 16% minimum net growth
- **Inventory & stockout prediction**
- **Dynamic target adjustments**
- **Interactive dashboards**
- **Automated reporting**

---

## Prerequisites

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.9 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Disk Space**: 5GB for application + database
- **Database**: PostgreSQL 12+ (or SQL Server, MySQL)

### Skills Required
- Basic command line usage
- SQL knowledge (for database queries)
- Python basics (for customization)

---

## Installation

### 1. Navigate to Project Directory

```bash
cd /home/user/LVL-CODES
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Install project in development mode
pip install -e .
```

**Note**: Installation may take 10-15 minutes due to large packages (TensorFlow, XGBoost, etc.)

### 4. Verify Installation

```bash
# Test imports
python -c "import pandas, numpy, sklearn, prophet, xgboost, lightgbm; print('✓ All packages installed successfully')"
```

---

## Database Setup

### Option 1: Connect to Existing Data Warehouse

If you have an existing data warehouse with sales data:

1. **Verify Database Accessibility**

```bash
# Test PostgreSQL connection (adjust for your database)
psql -h your_host -p 5432 -U your_user -d your_database -c "SELECT version();"
```

2. **Verify Required Tables Exist**

Your database should contain these tables (or similar):
- `fact_sales` - Sales transactions
- `dim_products` - Product master data
- `dim_geography` - Geographic dimensions
- `dim_channels` - Sales channels
- `fact_inventory` - Stock levels
- `fact_returns` - Return data

3. **Map Your Schema**

Edit `config/database.yaml` to match your actual table names:

```yaml
tables:
  sales_transactions:
    name: your_actual_sales_table_name  # Change this
    schema: your_schema_name
```

### Option 2: Generate Sample Data (For Testing)

If you don't have data yet, create sample data:

```python
# Run in Python
from scripts import generate_sample_data

# Generate 3 years of sample pet food sales data
generate_sample_data.create_dataset(
    start_date="2022-01-01",
    end_date="2025-12-31",
    n_skus=100,
    n_stores=50,
    output_path="./data/sample/"
)
```

---

## Configuration

### 1. Create Environment File

```bash
# Copy example environment file
cp .env.example .env

# Edit with your actual values
nano .env  # or use your preferred editor
```

### 2. Configure Database Connection

Edit `.env` file:

```bash
# Database Configuration
DB_TYPE=postgresql
DB_HOST=your_database_host
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_secure_password

# IMPORTANT: Never commit .env to version control!
```

### 3. Test Database Connection

```python
# Test connection
from src.data.connectors import DatabaseConnector

db = DatabaseConnector()
print("✓ Database connection successful!")

# Verify tables
info = db.get_table_info("fact_sales")
print(f"Sales table has {info['row_count']:,} rows")

db.close()
```

### 4. Configure Model Parameters

Review and adjust `config/models.yaml`:

```yaml
# Example: Adjust ensemble weights based on your validation results
ensemble:
  weights:
    sarima: 0.20      # Adjust these based on model performance
    prophet: 0.25
    xgboost: 0.25
    lightgbm: 0.20
    random_forest: 0.10
```

### 5. Configure Target Settings

Review and adjust `config/targets.yaml`:

```yaml
growth_targets:
  minimum_net_growth: 0.16  # Your 16% target
  base_year: 2025
  forecast_year: 2026

# Adjust dimensional targets for your categories
dimensions:
  product:
    categories:
      dog_food:
        min_growth: 0.15
        max_growth: 0.20
        weight: 0.45  # 45% of total sales
```

---

## Running the System

### Step 1: Extract and Process Historical Data

```python
from src.data.etl import SalesDataETL
from src.data.connectors import DatabaseConnector

# Connect to database
db = DatabaseConnector()

# Initialize ETL
etl = SalesDataETL(db)

# Extract and process sales data
df_sales = etl.run_pipeline(
    start_date="2021-01-01",
    end_date="2025-12-31",
    period="M",  # Monthly aggregation
    group_by=["category", "region", "channel"]
)

print(f"Loaded {len(df_sales):,} rows of sales data")
df_sales.to_csv("./data/processed/sales_monthly.csv", index=False)
```

### Step 2: Train Forecasting Models

```python
from src.models.ensemble import EnsembleForecaster

# Initialize ensemble with all models
forecaster = EnsembleForecaster(
    models=['sarima', 'prophet', 'xgboost', 'lightgbm', 'random_forest']
)

# Train on historical data
forecaster.fit(
    data=df_sales,
    target_col="net_sales_amount"
)

# Generate 2026 forecast (12 months)
forecast_2026 = forecaster.predict(horizon=12, frequency="M")

print("2026 Forecast:")
print(forecast_2026.head())

# Save forecast
forecast_2026.to_csv("./data/forecasts/forecast_2026.csv")
```

### Step 3: Allocate Targets with 16% Growth

```python
from src.targets.allocation import TargetAllocator

# Initialize allocator
allocator = TargetAllocator(
    base_forecast=forecast_2026,
    target_growth=0.16,  # 16% minimum net growth
    dimensions=['category', 'region', 'channel']
)

# Allocate targets
targets_2026 = allocator.allocate()

print("2026 Targets by Category:")
print(targets_2026.groupby("category")["target"].sum())

# Save targets
targets_2026.to_csv("./data/targets/targets_2026.csv", index=False)
```

### Step 4: Run Stockout Analysis

```python
from src.inventory.stockout import StockoutPredictor

# Load current inventory
inventory = etl.extract_inventory_data()

# Predict stockout risk
predictor = StockoutPredictor()
stockout_risk = predictor.predict(
    current_stock=inventory,
    forecast=forecast_2026
)

# Adjust targets for stockout risk
from src.inventory.impact import SalesImpactAnalyzer

impact_analyzer = SalesImpactAnalyzer()
adjusted_targets = impact_analyzer.adjust_for_stockouts(
    targets=targets_2026,
    stockout_risk=stockout_risk
)

print("Targets adjusted for stockout risk")
```

### Step 5: Launch Dashboard

```bash
# Start the dashboard
python src/dashboard/app.py

# Access at: http://localhost:8050
```

Or run as background service:

```bash
# Run in background
nohup python src/dashboard/app.py > dashboard.log 2>&1 &

# Check if running
ps aux | grep dashboard

# Stop dashboard
pkill -f "dashboard/app.py"
```

---

## Usage Examples

### Example 1: Quick Forecast for Single Category

```python
from src.data.etl import load_sales_data
from src.models.prophet import ProphetForecaster

# Load dog food sales
df = load_sales_data(
    start_date="2022-01-01",
    end_date="2025-12-31",
    period="M"
)

df_dog_food = df[df["category"] == "Dog Food"]

# Forecast with Prophet
model = ProphetForecaster()
model.fit(df_dog_food, target_col="net_sales_amount")

# Predict 2026
forecast = model.predict(horizon=12)

print(forecast)
```

### Example 2: Scenario Analysis

```python
from src.targets.scenarios import ScenarioPlanner

planner = ScenarioPlanner(base_forecast=forecast_2026)

# Run best/base/worst case scenarios
scenarios = planner.run_scenarios(
    best_case_growth=0.22,   # 22%
    base_case_growth=0.16,   # 16%
    worst_case_growth=0.10   # 10%
)

print("Scenario Analysis:")
for scenario_name, result in scenarios.items():
    print(f"{scenario_name}: ${result['total_sales']:,.0f}")
```

### Example 3: Regional Target Allocation

```python
from src.targets.allocation import TargetAllocator

# Allocate by region only
allocator = TargetAllocator(
    base_forecast=forecast_2026,
    target_growth=0.16,
    dimensions=['region']
)

regional_targets = allocator.allocate()

print("\n2026 Regional Targets:")
print(regional_targets.groupby("region")["target"].sum().sort_values(ascending=False))
```

### Example 4: Generate Executive Report

```python
from src.reporting.generate_reports import ExecutiveReport

report = ExecutiveReport(
    targets=targets_2026,
    actuals=df_sales,
    forecast=forecast_2026
)

# Generate PDF report
report.generate(
    output_path="./reports/2026_targets_executive_summary.pdf",
    format="pdf"
)

print("✓ Executive report generated")
```

---

## Troubleshooting

### Issue 1: Database Connection Fails

**Error**: `Failed to connect to database`

**Solutions**:
1. Verify credentials in `.env`:
   ```bash
   # Test connection manually
   psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME
   ```

2. Check firewall/network:
   ```bash
   # Test connectivity
   telnet your_db_host 5432
   ```

3. Verify database is running:
   ```bash
   # PostgreSQL
   sudo systemctl status postgresql

   # Or check logs
   tail -f /var/log/postgresql/postgresql-12-main.log
   ```

### Issue 2: Model Training Fails

**Error**: `Insufficient historical data for modeling`

**Solutions**:
1. Verify you have at least 24 months of data:
   ```python
   df = load_sales_data("2021-01-01", "2025-12-31")
   print(f"Data range: {df['date'].min()} to {df['date'].max()}")
   print(f"Total months: {len(df['date'].unique())}")
   ```

2. Check for data gaps:
   ```python
   # Find missing dates
   date_range = pd.date_range(df['date'].min(), df['date'].max(), freq='D')
   missing_dates = set(date_range) - set(df['date'])
   print(f"Missing {len(missing_dates)} dates")
   ```

3. Reduce model complexity for small datasets:
   ```yaml
   # In config/models.yaml
   sarima:
     auto_arima:
       max_p: 3  # Reduce from 5
       max_q: 3  # Reduce from 5
   ```

### Issue 3: Dashboard Won't Start

**Error**: `Address already in use`

**Solutions**:
1. Check if port 8050 is in use:
   ```bash
   lsof -i :8050
   # Kill existing process
   kill -9 <PID>
   ```

2. Use different port:
   ```bash
   # In .env
   DASH_PORT=8051
   ```

3. Check logs:
   ```bash
   tail -f logs/lvl_codes.log
   ```

### Issue 4: Out of Memory

**Error**: `MemoryError` or system slowdown

**Solutions**:
1. Process data in chunks:
   ```python
   # Load data in chunks
   for chunk in pd.read_sql(query, db.engine, chunksize=10000):
       process_chunk(chunk)
   ```

2. Reduce model complexity:
   ```yaml
   # Use fewer ensemble models
   ensemble:
     enabled_models: ['prophet', 'xgboost']  # Only 2 instead of 5
   ```

3. Increase system swap:
   ```bash
   # Linux: Add swap space
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

---

## Next Steps

### Phase 1: Complete Core Models (Estimated: 1-2 weeks)

The framework is in place. Now complete these model implementations:

1. **SARIMA Model** (`src/models/sarima/sarima_forecaster.py`)
   - Implement auto-ARIMA with pmdarima
   - Add seasonal decomposition
   - Test with monthly sales data

2. **Prophet Model** (`src/models/prophet/prophet_forecaster.py`)
   - Implement Facebook Prophet
   - Add custom holidays (pet industry events)
   - Test with daily/weekly data

3. **XGBoost Model** (`src/models/ml/xgboost_forecaster.py`)
   - Feature engineering (lags, rolling stats)
   - Hyperparameter tuning
   - Test and validate

4. **LightGBM & Random Forest** (similar to XGBoost)
   - Implement in `src/models/ml/`

5. **Ensemble Forecaster** (`src/models/ensemble/ensemble_forecaster.py`)
   - Combine all models
   - Weighted averaging
   - Performance comparison

### Phase 2: Target Optimization (Estimated: 1 week)

1. **Constraint Optimization** (`src/targets/optimization/`)
   - Implement linear programming (PuLP)
   - Add inventory constraints
   - Add budget constraints

2. **Dynamic Adjustment** (`src/targets/adjustment/`)
   - Rolling forecast updates
   - Variance-triggered reallocation
   - Performance-based adjustments

### Phase 3: Inventory Management (Estimated: 1 week)

1. **Stock Holding Analysis** (`src/inventory/stock_holding/`)
   - Days of supply calculation
   - Reorder point optimization
   - ABC analysis

2. **Stockout Prediction** (`src/inventory/stockout/`)
   - Probability modeling
   - Safety stock calculation
   - Impact on targets

### Phase 4: Dashboard & Reporting (Estimated: 1-2 weeks)

1. **Interactive Dashboard** (`src/dashboard/`)
   - Build with Plotly Dash
   - KPI cards
   - Interactive charts
   - Drill-down capabilities

2. **Automated Reports** (`src/reporting/`)
   - PDF generation
   - Email alerts
   - Scheduled reports

### Phase 5: Testing & Documentation (Ongoing)

1. **Unit Tests** (`tests/`)
   - Test each module
   - Achieve >80% coverage

2. **Integration Tests**
   - End-to-end workflows
   - Performance benchmarks

3. **User Documentation**
   - Update README with examples
   - Create video tutorials
   - Write API reference

---

## Getting Help

### Resources

- **Project README**: `README.md`
- **API Reference**: `docs/api_reference.md` (coming soon)
- **Configuration Guide**: See `config/` directory YAML files
- **Example Notebooks**: `notebooks/` (coming soon)

### Support Channels

1. **GitHub Issues**: Create an issue for bugs or features
2. **Internal Team**: Contact LVL-CODES Analytics Team
3. **Documentation**: Check inline code comments (extensively documented)

### Contributing

When developing new features:

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Follow the existing code style (heavily commented)

3. Add tests for new functionality

4. Update documentation

5. Submit for review

---

## Security Notes

### Protect Sensitive Data

- **Never commit `.env` file** (contains passwords)
- **Never commit actual sales data** to version control
- Use `.gitignore` (already configured)

### Database Access

- Use read-only database user for forecasting (if possible)
- Restrict write access to target tables
- Use VPN for remote database access

### API Keys

If using external services (weather data, etc.):
- Store API keys in `.env`
- Rotate keys regularly
- Monitor usage

---

## Performance Tips

### For Large Datasets (> 1M rows)

1. **Use sampling for development**:
   ```python
   # Sample 10% of data for testing
   df_sample = df.sample(frac=0.1, random_state=42)
   ```

2. **Aggregate before modeling**:
   ```python
   # Model monthly instead of daily
   df_monthly = aggregate_to_period(df, period="M")
   ```

3. **Use parallel processing**:
   ```python
   # In config/models.yaml
   general:
     n_jobs: -1  # Use all CPU cores
   ```

### For Faster Model Training

1. **Reduce hyperparameter search space**
2. **Use early stopping**
3. **Cache intermediate results**
4. **Train only changed models**

---

## Maintenance

### Regular Tasks

**Daily**:
- Monitor dashboard for alerts
- Check log files for errors

**Weekly**:
- Review forecast accuracy
- Update actuals vs. targets

**Monthly**:
- Retrain models with new data
- Review and adjust targets
- Generate executive reports

**Quarterly**:
- Major model retraining
- Configuration review
- Performance optimization

### Backup Strategy

```bash
# Backup database
pg_dump your_database > backup_$(date +%Y%m%d).sql

# Backup models
cp -r ./models/saved_models/ ./backups/models_$(date +%Y%m%d)/

# Backup configuration
cp -r ./config/ ./backups/config_$(date +%Y%m%d)/
```

---

## Conclusion

You now have a comprehensive framework for 2026 sales target management. The foundation is built with:

✅ Database connectivity
✅ ETL pipelines
✅ Configuration management
✅ Base forecasting framework
✅ Utilities and helpers
✅ Logging and monitoring

**Next**: Complete the specific forecasting models and connect to your actual data warehouse.

For questions or issues, refer to the troubleshooting section or contact the development team.

**Good luck with your 2026 sales targets!** 🎯
