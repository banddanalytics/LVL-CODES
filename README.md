# LVL-CODES Repository - Main Documentation Hub

**Welcome to LVL-CODES!** This repository hosts multiple data analytics and business intelligence projects for pet food retail & distribution.

---

## 📚 Repository Structure

This is a **multi-project repository** organized by branches and subdirectories:

```
LVL-CODES/
├── README.md (This file - Documentation hub)
├── BRANCH_GUIDE.md (Branch information and navigation)
└── [Project Subdirectories in respective branches]
```

---

## 🌿 Active Branches & Projects

### `claude/LVL-STMS-UgMj2` ⭐ **Main Development Branch**
**Project**: LVL-STMS (Sales Target Management System)
**Location**: `LVL-STMS/`
**Status**: 🚧 In Development (~35% Complete)

**Description**:
Comprehensive 2026 sales target management system for pet food retail & distribution with advanced forecasting, optimization, and inventory management.

**Key Features**:
- ✅ Multi-model forecasting (SARIMA, Prophet, XGBoost, LightGBM, Random Forest, Ensemble)
- ✅ 16% minimum net growth targeting with dynamic adjustments
- ✅ Multi-dimensional analytics (product hierarchy, geography, channels)
- ✅ Inventory management & stockout prediction
- ✅ Constraint-based optimization (budget, capacity, distribution)
- ✅ Scenario planning (best/base/worst case, Monte Carlo simulation)
- ✅ Interactive dashboards & automated reporting

**What's Completed**:
- ✅ Complete project infrastructure & configuration
- ✅ Database connectivity layer (PostgreSQL, SQL Server, MySQL)
- ✅ ETL pipeline with data validation & feature engineering
- ✅ Base forecasting framework
- ✅ Utilities, logging, and helper functions
- ✅ Comprehensive documentation

**What's Next** (Priority Order):
1. ⏳ Implement individual forecasting models (SARIMA, Prophet, ML)
2. ⏳ Build target allocation & optimization system
3. ⏳ Develop inventory & stockout prediction
4. ⏳ Create interactive dashboards
5. ⏳ Build automated reporting & alerts

**Quick Start**:
```bash
git checkout claude/LVL-STMS-UgMj2
cd LVL-STMS/
cat README.md           # Project documentation
cat DEPLOYMENT_GUIDE.md # Setup instructions
```

**Documentation Files**:
- `LVL-STMS/README.md` - Project overview & features
- `LVL-STMS/DEPLOYMENT_GUIDE.md` - Complete setup & usage guide
- `LVL-STMS/PROJECT_STATUS.md` - Current status & roadmap

---

### `claude/LVL-CODES-MAIN-UgMj2` 📖 **Documentation Branch**
**Current Branch** - You are here!

**Purpose**: Central documentation hub for the entire LVL-CODES repository

**Contents**:
- Repository overview
- Branch navigation guide
- Project summaries
- Development guidelines

---

## 🎯 Project Goals & Use Cases

### LVL-STMS (Sales Target Management System)

**Business Objective**:
Set and manage 2026 sales targets for pet food market with 16% minimum net growth after returns.

**Target Audience**:
- Sales Directors & VPs
- Regional Sales Managers
- Category Managers
- Demand Planners
- Business Analysts

**Key Use Cases**:

1. **Annual Target Setting**
   - Generate baseline forecasts for 2026
   - Allocate 16% growth across dimensions
   - Apply constraints (inventory, budget, capacity)
   - Review and approve targets

2. **Monthly Performance Tracking**
   - Compare actuals vs. targets
   - Identify variance triggers (±10%)
   - Automatically reallocate underperforming targets
   - Generate executive dashboards

3. **Scenario Planning**
   - Model best/base/worst case scenarios
   - Run Monte Carlo simulations
   - Assess risk and opportunity
   - Support strategic decision-making

4. **Inventory Optimization**
   - Predict stockout risks
   - Calculate safety stock requirements
   - Adjust targets for inventory constraints
   - Optimize reorder points

5. **Channel & Category Analysis**
   - Compare performance across channels (retail, e-commerce, wholesale)
   - Analyze category growth trends
   - Optimize product mix
   - Support promotional planning

---

## 💻 Technology Stack

### LVL-STMS Stack:

**Languages & Core**:
- Python 3.9+
- SQL (PostgreSQL, SQL Server, MySQL)

**Data Processing**:
- pandas, numpy, scipy
- SQLAlchemy (database ORM)
- Great Expectations (data quality)

**Forecasting & ML**:
- statsmodels (SARIMA)
- Prophet (Facebook forecasting)
- scikit-learn (ML framework)
- XGBoost, LightGBM (gradient boosting)
- TensorFlow/Keras (deep learning - optional)

**Optimization**:
- PuLP (linear programming)
- CVXPY (convex optimization)
- Pyomo (optimization modeling)

**Visualization & Dashboards**:
- Plotly, Dash (interactive dashboards)
- Matplotlib, Seaborn (static plots)

**Reporting**:
- ReportLab (PDF generation)
- openpyxl, xlsxwriter (Excel)
- Jinja2 (templates)

**Configuration & Deployment**:
- YAML configuration files
- python-dotenv (environment variables)
- loguru (advanced logging)

---

## 📊 Development Status Overview

| Project | Branch | Status | Completion | Last Updated |
|---------|--------|--------|------------|--------------|
| **LVL-STMS** | claude/LVL-STMS-UgMj2 | 🚧 Active | ~35% | 2025-12-17 |

### LVL-STMS Detailed Status:

| Component | Status | Completion |
|-----------|--------|------------|
| Infrastructure | ✅ Complete | 100% |
| Configuration | ✅ Complete | 100% |
| Database Layer | ✅ Complete | 100% |
| ETL Pipeline | ✅ Complete | 100% |
| Base Framework | ✅ Complete | 80% |
| Forecasting Models | ⏳ Pending | 30% |
| Target Allocation | ⏳ Pending | 0% |
| Optimization | ⏳ Pending | 0% |
| Inventory Mgmt | ⏳ Pending | 0% |
| Dashboards | ⏳ Pending | 0% |
| Reporting | ⏳ Pending | 0% |
| Testing | ⏳ Pending | 0% |

---

## 🚀 Getting Started

### For New Developers:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/banddanalytics/LVL-CODES.git
   cd LVL-CODES
   ```

2. **Choose your project branch**:
   ```bash
   # For Sales Target Management System
   git checkout claude/LVL-STMS-UgMj2
   cd LVL-STMS/
   ```

3. **Follow project-specific setup**:
   ```bash
   # Read the deployment guide
   cat DEPLOYMENT_GUIDE.md

   # Install dependencies
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   nano .env
   ```

---

## 📁 File Organization Standards

### Branch Structure:
```
LVL-CODES/
├── [Project-Name]/          # Project subdirectory
│   ├── README.md            # Project documentation
│   ├── DEPLOYMENT_GUIDE.md  # Setup instructions
│   ├── PROJECT_STATUS.md    # Current status
│   ├── requirements.txt     # Dependencies
│   ├── setup.py             # Package setup
│   ├── .env.example         # Environment template
│   ├── .gitignore           # Git ignore rules
│   ├── src/                 # Source code
│   ├── config/              # Configuration files
│   ├── tests/               # Test suites
│   ├── notebooks/           # Jupyter notebooks
│   ├── docs/                # Additional documentation
│   └── data/                # Data directories (gitignored)
└── README.md                # Repository overview
```

---

## 🔧 Development Guidelines

### Code Standards:
- **Style**: PEP 8 compliant
- **Type Hints**: Use throughout
- **Documentation**: Comprehensive docstrings
- **Comments**: Extensive inline comments (especially for Cursor IDE)
- **Testing**: Aim for >80% coverage

### Git Workflow:
1. Create feature branches from project branches
2. Use descriptive commit messages
3. Reference issues/tickets in commits
4. Submit PRs for review
5. Merge after approval

### Branch Naming:
- Main documentation: `claude/LVL-CODES-MAIN-*`
- Project branches: `claude/[PROJECT-NAME]-*`
- Feature branches: `feature/[feature-name]`
- Bugfix branches: `bugfix/[bug-name]`

---

## 📖 Documentation Links

### LVL-STMS Documentation:

**In Repository**:
- [LVL-STMS README](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/README.md)
- [Deployment Guide](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/DEPLOYMENT_GUIDE.md)
- [Project Status](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/PROJECT_STATUS.md)

**Configuration Reference**:
- [Database Config](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/config/database.yaml)
- [Models Config](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/config/models.yaml)
- [Targets Config](../../tree/claude/LVL-STMS-UgMj2/LVL-STMS/config/targets.yaml)

---

## 🤝 Contributing

### For Team Members:

1. **Pull latest changes**:
   ```bash
   git checkout claude/LVL-STMS-UgMj2
   git pull origin claude/LVL-STMS-UgMj2
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

4. **Push and create PR**:
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

---

## 🔒 Security & Compliance

### Sensitive Data:
- ❌ Never commit `.env` files
- ❌ Never commit actual sales data
- ❌ Never commit credentials or API keys
- ✅ Use `.gitignore` (already configured)
- ✅ Use environment variables
- ✅ Use parameterized SQL queries

### Data Access:
- Database credentials stored in `.env` files only
- Use read-only database users where possible
- VPN required for remote database access
- Regular credential rotation recommended

---

## 📞 Support & Contact

### For Questions:
- **GitHub Issues**: Create an issue for bugs or feature requests
- **Team Contact**: LVL-CODES Analytics Team
- **Documentation**: Check project-specific README files

### Resources:
- Project READMEs in respective branches
- Deployment guides
- Inline code documentation (heavily commented)

---

## 📅 Recent Updates

### 2025-12-17:
- ✅ Created LVL-STMS project structure
- ✅ Implemented database connectivity layer
- ✅ Built ETL pipeline framework
- ✅ Created base forecasting framework
- ✅ Reorganized repository structure
- ✅ Renamed branches for clarity
- ✅ Updated documentation hub

---

## 🗺️ Roadmap

### Q1 2026:
- [ ] Complete LVL-STMS forecasting models
- [ ] Implement target allocation & optimization
- [ ] Build inventory management module
- [ ] Launch interactive dashboards
- [ ] Deploy to production

### Future Projects:
- 🔜 Customer segmentation & analytics
- 🔜 Price optimization system
- 🔜 Marketing campaign ROI tracker
- 🔜 Competitor intelligence dashboard

---

## 📜 License

Internal use only - LVL-CODES Analytics Team

---

## 🎯 Quick Navigation

| I want to... | Go here |
|--------------|---------|
| Work on Sales Targets | `git checkout claude/LVL-STMS-UgMj2` |
| View project documentation | Check branch README files |
| Set up development environment | Follow project DEPLOYMENT_GUIDE.md |
| Understand current status | Check PROJECT_STATUS.md |
| Report a bug | Create a GitHub issue |

---

**Last Updated**: 2025-12-17
**Maintained By**: LVL-CODES Analytics Team
**Repository**: https://github.com/banddanalytics/LVL-CODES
