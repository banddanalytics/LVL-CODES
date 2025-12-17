# LVL-CODES: 2026 Sales Target Management System

## Overview
Comprehensive sales target management system for pet food retail & distribution with multi-dimensional forecasting, inventory management, and dynamic target adjustment capabilities.

## Key Features

### 📊 Multi-Dimensional Analytics
- **Product Hierarchy**: Category → Sub-Group → SKU level targeting
- **Geographic**: Regional and territory-based targets
- **Channel**: Retail, E-commerce, Wholesale, Distribution
- **Time Series**: Monthly, Quarterly, Annual forecasting

### 🤖 Advanced Forecasting Models
- **SARIMA**: Seasonal patterns and trends
- **Prophet**: Facebook's forecasting with holidays/events
- **Machine Learning**: XGBoost, LightGBM, Random Forest ensemble
- **Growth Decomposition**: Baseline, promotional, new products
- **Scenario Planning**: Best/Base/Worst case modeling

### 📦 Inventory & Stockout Management
- Real-time stock holding analysis
- Predictive stockout modeling
- Impact assessment on sales targets
- Reorder point optimization

### 🎯 Target Management
- 16% minimum net growth target (adjustable)
- Returns and adjustments tracking
- Rolling forecast updates
- Constraint-based optimization
- Automatic variance-triggered adjustments

### 📈 Reporting & Dashboards
- Real-time KPI monitoring
- Drill-down capabilities across all dimensions
- Automated alerts and recommendations
- Executive dashboards
- Variance analysis reports

## Project Structure

```
LVL-CODES/
├── config/                      # Configuration files
│   ├── database.yaml           # Database connection configs
│   ├── models.yaml             # Model hyperparameters
│   └── targets.yaml            # Target settings and constraints
├── src/
│   ├── data/                   # Data layer
│   │   ├── connectors/        # Database connectors
│   │   ├── etl/               # ETL pipelines
│   │   ├── schemas/           # Data warehouse schemas
│   │   └── validation/        # Data quality checks
│   ├── models/                 # Forecasting models
│   │   ├── sarima/            # SARIMA implementation
│   │   ├── prophet/           # Prophet implementation
│   │   ├── ml/                # Machine learning models
│   │   ├── ensemble/          # Ensemble methods
│   │   └── decomposition/     # Growth decomposition
│   ├── targets/                # Target management
│   │   ├── allocation/        # Target allocation logic
│   │   ├── optimization/      # Constraint optimization
│   │   ├── adjustment/        # Dynamic adjustments
│   │   └── scenarios/         # Scenario planning
│   ├── inventory/              # Inventory management
│   │   ├── stock_holding/     # Stock analysis
│   │   ├── stockout/          # Stockout prediction
│   │   └── impact/            # Sales impact assessment
│   ├── reporting/              # Reporting engine
│   │   ├── kpi/               # KPI calculations
│   │   ├── alerts/            # Alert system
│   │   └── exports/           # Report generation
│   ├── dashboard/              # Dashboard application
│   │   ├── app.py             # Main Dash application
│   │   ├── components/        # UI components
│   │   └── callbacks/         # Interactive callbacks
│   └── utils/                  # Utilities
│       ├── logging.py         # Logging configuration
│       ├── helpers.py         # Helper functions
│       └── constants.py       # Constants and enums
├── notebooks/                  # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_training.ipynb
│   ├── 03_target_setting.ipynb
│   └── 04_scenario_analysis.ipynb
├── tests/                      # Unit and integration tests
├── docs/                       # Documentation
│   ├── user_guide.md
│   ├── api_reference.md
│   └── deployment.md
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL/SQL Server (for data warehouse)
- 8GB+ RAM recommended
- Cursor IDE (recommended)

### Setup Steps

1. **Clone and Navigate**
```bash
cd LVL-CODES
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Database**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Initialize Database Schema**
```bash
python src/data/schemas/init_database.py
```

6. **Run ETL Pipeline**
```bash
python src/data/etl/run_etl.py
```

## Quick Start

### 1. Load Historical Data
```python
from src.data.connectors import DatabaseConnector
from src.data.etl import SalesDataETL

# Connect to your data warehouse
db = DatabaseConnector()
etl = SalesDataETL(db)

# Extract and load sales data
etl.extract_sales_history(start_date='2021-01-01', end_date='2025-12-31')
```

### 2. Train Forecasting Models
```python
from src.models.ensemble import EnsembleForecaster

# Initialize ensemble with all models
forecaster = EnsembleForecaster(
    models=['sarima', 'prophet', 'xgboost', 'lightgbm', 'random_forest']
)

# Train on historical data
forecaster.fit(train_data)

# Generate 2026 forecasts
forecasts_2026 = forecaster.predict(horizon=12)  # 12 months
```

### 3. Set Targets with Growth Constraint
```python
from src.targets.allocation import TargetAllocator
from src.targets.optimization import ConstraintOptimizer

# Allocate 16% growth target across dimensions
allocator = TargetAllocator(
    base_forecast=forecasts_2026,
    target_growth=0.16,  # 16% minimum net growth
    dimensions=['region', 'channel', 'category', 'subgroup']
)

# Optimize with constraints
optimizer = ConstraintOptimizer(
    inventory_capacity=True,
    distribution_limits=True,
    budget_constraints=True
)

targets_2026 = optimizer.optimize(allocator.allocate())
```

### 4. Run Stockout Impact Analysis
```python
from src.inventory.stockout import StockoutPredictor
from src.inventory.impact import SalesImpactAnalyzer

# Predict potential stockouts
stockout_predictor = StockoutPredictor()
stockout_risk = stockout_predictor.predict(
    current_stock=current_inventory,
    forecast=forecasts_2026
)

# Assess impact on targets
impact_analyzer = SalesImpactAnalyzer()
adjusted_targets = impact_analyzer.adjust_for_stockouts(
    targets=targets_2026,
    stockout_risk=stockout_risk
)
```

### 5. Launch Dashboard
```bash
python src/dashboard/app.py
```
Access at: http://localhost:8050

## Configuration

### Database Configuration (config/database.yaml)
```yaml
data_warehouse:
  host: your_host
  port: 5432
  database: sales_dw
  user: your_user
  password: ${DB_PASSWORD}  # From .env file
```

### Model Configuration (config/models.yaml)
```yaml
ensemble:
  weights:
    sarima: 0.20
    prophet: 0.25
    xgboost: 0.25
    lightgbm: 0.20
    random_forest: 0.10
```

### Target Configuration (config/targets.yaml)
```yaml
growth_targets:
  minimum_net_growth: 0.16  # 16%
  adjustment_trigger: 0.10   # ±10% variance triggers review
  rolling_forecast_window: 12  # months
```

## Usage Examples

See `notebooks/` directory for detailed examples:
- **01_data_exploration.ipynb**: Data analysis and visualization
- **02_model_training.ipynb**: Model training and evaluation
- **03_target_setting.ipynb**: Target allocation and optimization
- **04_scenario_analysis.ipynb**: What-if scenario planning

## Monitoring & Alerts

The system automatically:
- Tracks daily/weekly/monthly performance vs. targets
- Triggers alerts when variance exceeds ±10%
- Recommends corrective actions
- Updates rolling forecasts monthly
- Monitors inventory levels and stockout risks

## API Reference

See `docs/api_reference.md` for detailed API documentation.

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Contributing

This is an internal project for LVL-CODES sales analytics team.

## Support

For issues or questions:
- Create an issue in the repository
- Contact the analytics team
- See documentation in `docs/`

## License

Internal use only - LVL-CODES Analytics Team

---

**Version**: 1.0.0
**Last Updated**: 2025-12-17
**Maintained By**: LVL-CODES Analytics Team
