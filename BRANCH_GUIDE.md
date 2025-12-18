# LVL-CODES Branch Navigation Guide

This guide helps you navigate between different branches in the LVL-CODES repository and understand what each branch contains.

---

## 🌿 Branch Overview

### Active Branches

| Branch Name | Purpose | Status | Contains |
|-------------|---------|--------|----------|
| `claude/LVL-CODES-MAIN-UgMj2` | Documentation Hub | ✅ Active | Repository docs, branch guides |
| `claude/LVL-STMS-UgMj2` | Sales Target Mgmt System | 🚧 Development | Full STMS project |

### Deprecated Branches

| Branch Name | Status | Notes |
|-------------|--------|-------|
| `claude/2026-sales-targets-UgMj2` | 🗑️ Deprecated | Renamed to `claude/LVL-CODES-MAIN-UgMj2` |

---

## 📍 Current Branch

You are currently on: **`claude/LVL-CODES-MAIN-UgMj2`** (Documentation Branch)

---

## 🗺️ Branch Navigation Commands

### Switching to Development Branch

```bash
# Switch to LVL-STMS development branch
git checkout claude/LVL-STMS-UgMj2
cd LVL-STMS/

# Now you're in the project directory
ls -la                     # See all files
cat README.md              # View project documentation
cat DEPLOYMENT_GUIDE.md    # View setup instructions
```

### Switching Back to Documentation Branch

```bash
# From any branch, switch to documentation hub
git checkout claude/LVL-CODES-MAIN-UgMj2
cd /home/user/LVL-CODES/  # Go to root

# View main documentation
cat README.md
cat BRANCH_GUIDE.md
```

### Creating Feature Branches

When working on new features:

```bash
# Start from the project branch
git checkout claude/LVL-STMS-UgMj2

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ... edit files ...

# Commit your work
git add .
git commit -m "Add: Description of your feature"

# Push to remote
git push origin feature/your-feature-name
```

---

## 📦 What Each Branch Contains

### `claude/LVL-CODES-MAIN-UgMj2` (Documentation Hub)

**Location**: `/home/user/LVL-CODES/`

**Structure**:
```
LVL-CODES/
├── README.md              # Main repository documentation
├── BRANCH_GUIDE.md        # This file - branch navigation
├── LVL-STMS/              # (Empty placeholder, project on other branch)
└── .git/                  # Git repository
```

**Purpose**:
- Central documentation hub for entire repository
- Branch navigation and switching guides
- Repository-wide standards and guidelines
- Project summaries and status overviews

**When to use this branch**:
- Reading repository-wide documentation
- Understanding project organization
- Learning how to navigate between projects
- Checking overall repository status

**Commands**:
```bash
git checkout claude/LVL-CODES-MAIN-UgMj2
cat README.md              # Repository overview
cat BRANCH_GUIDE.md        # Branch navigation (this file)
```

---

### `claude/LVL-STMS-UgMj2` (Sales Target Management System)

**Location**: `/home/user/LVL-CODES/LVL-STMS/`

**Structure**:
```
LVL-CODES/
├── README.md                    # Repository-level README
└── LVL-STMS/                    # Project directory
    ├── README.md                # Project documentation
    ├── DEPLOYMENT_GUIDE.md      # Complete setup guide
    ├── PROJECT_STATUS.md        # Current status & roadmap
    ├── requirements.txt         # Python dependencies
    ├── setup.py                 # Package installation
    ├── .env.example             # Environment template
    ├── .gitignore               # Git ignore rules
    ├── src/                     # Source code
    │   ├── data/                # Data processing
    │   │   ├── connectors/      # Database connections
    │   │   ├── etl/             # ETL pipelines
    │   │   ├── schemas/         # Data schemas
    │   │   └── validation/      # Data quality
    │   ├── models/              # Forecasting models
    │   │   ├── sarima/          # SARIMA implementation
    │   │   ├── prophet/         # Prophet implementation
    │   │   ├── ml/              # ML models (XGBoost, etc.)
    │   │   ├── ensemble/        # Ensemble forecaster
    │   │   └── decomposition/   # Growth decomposition
    │   ├── targets/             # Target management
    │   │   ├── allocation/      # Target allocation
    │   │   ├── optimization/    # Constraint optimization
    │   │   ├── adjustment/      # Dynamic adjustments
    │   │   └── scenarios/       # Scenario planning
    │   ├── inventory/           # Inventory management
    │   │   ├── stock_holding/   # Stock analysis
    │   │   ├── stockout/        # Stockout prediction
    │   │   └── impact/          # Sales impact
    │   ├── reporting/           # Reporting system
    │   │   ├── kpi/             # KPI calculations
    │   │   ├── alerts/          # Alert system
    │   │   └── exports/         # Report generation
    │   ├── dashboard/           # Dashboard app
    │   │   ├── app.py           # Main Dash app
    │   │   ├── components/      # UI components
    │   │   └── callbacks/       # Interactive callbacks
    │   └── utils/               # Utilities
    │       ├── constants.py     # Application constants
    │       ├── logging.py       # Logging configuration
    │       └── helpers.py       # Helper functions
    ├── config/                  # Configuration files
    │   ├── database.yaml        # Database settings
    │   ├── models.yaml          # Model configurations
    │   └── targets.yaml         # Target settings
    ├── notebooks/               # Jupyter notebooks
    ├── tests/                   # Test suites
    ├── docs/                    # Additional docs
    ├── data/                    # Data directories (gitignored)
    ├── logs/                    # Log files (gitignored)
    ├── models/saved_models/     # Trained models (gitignored)
    └── reports/                 # Generated reports (gitignored)
```

**Purpose**:
- Complete 2026 sales target management system
- Multi-model forecasting (SARIMA, Prophet, XGBoost, LightGBM, Random Forest)
- Target allocation with 16% minimum net growth
- Inventory management & stockout prediction
- Interactive dashboards & automated reporting

**Current Status**: ~35% Complete
- ✅ Infrastructure (100%)
- ✅ Database layer (100%)
- ✅ ETL pipeline (100%)
- ✅ Base framework (80%)
- ⏳ Forecasting models (30%)
- ⏳ Other components (0-30%)

**When to use this branch**:
- Developing forecasting models
- Building target allocation logic
- Implementing dashboards
- Writing tests
- Running the application

**Commands**:
```bash
# Switch to development branch
git checkout claude/LVL-STMS-UgMj2
cd LVL-STMS/

# View project documentation
cat README.md                # Project overview
cat DEPLOYMENT_GUIDE.md      # Detailed setup guide
cat PROJECT_STATUS.md        # Current status

# Set up environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Configure database
cp .env.example .env
nano .env                    # Edit with your credentials

# Start development
python src/dashboard/app.py  # Run dashboard
pytest tests/                # Run tests
```

---

## 🔄 Common Workflows

### Workflow 1: Starting New Development

```bash
# 1. Switch to project branch and pull latest
git checkout claude/LVL-STMS-UgMj2
git pull origin claude/LVL-STMS-UgMj2

# 2. Navigate to project
cd LVL-STMS/

# 3. Activate environment
source venv/bin/activate

# 4. Start coding!
```

### Workflow 2: Checking Documentation

```bash
# 1. Switch to documentation branch
git checkout claude/LVL-CODES-MAIN-UgMj2

# 2. View documentation
cat README.md
cat BRANCH_GUIDE.md

# 3. Return to development
git checkout claude/LVL-STMS-UgMj2
```

### Workflow 3: Creating a Pull Request

```bash
# 1. Create feature branch from project branch
git checkout claude/LVL-STMS-UgMj2
git checkout -b feature/implement-sarima-model

# 2. Make changes and test
# ... development work ...
pytest tests/

# 3. Commit changes
git add .
git commit -m "Add: SARIMA forecasting model implementation"

# 4. Push to remote
git push origin feature/implement-sarima-model

# 5. Create PR on GitHub
# Go to: https://github.com/banddanalytics/LVL-CODES/pulls
```

### Workflow 4: Syncing Multiple Branches

```bash
# Update documentation branch
git checkout claude/LVL-CODES-MAIN-UgMj2
git pull origin claude/LVL-CODES-MAIN-UgMj2

# Update development branch
git checkout claude/LVL-STMS-UgMj2
git pull origin claude/LVL-STMS-UgMj2

# View status of all branches
git branch -a
```

---

## 📋 Branch Status Reference

### Check Current Branch

```bash
# Show current branch
git branch

# Show with more detail
git status
```

### View All Branches

```bash
# Local branches only
git branch

# Local and remote branches
git branch -a

# Remote branches only
git branch -r
```

### Branch Information

```bash
# Show last commit on each branch
git branch -v

# Show tracked remote branches
git branch -vv

# Show merged branches
git branch --merged

# Show unmerged branches
git branch --no-merged
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "Not on a branch"

**Problem**: Detached HEAD state

**Solution**:
```bash
# Return to a named branch
git checkout claude/LVL-STMS-UgMj2
```

### Issue 2: "Uncommitted changes"

**Problem**: Can't switch branches with uncommitted changes

**Solution Option A** (Save changes):
```bash
git stash                    # Save changes temporarily
git checkout target-branch   # Switch branch
git stash pop                # Restore changes (if needed)
```

**Solution Option B** (Commit changes):
```bash
git add .
git commit -m "WIP: Description"
git checkout target-branch
```

### Issue 3: "Branch already exists"

**Problem**: Trying to create existing branch

**Solution**:
```bash
# Just checkout existing branch
git checkout existing-branch

# Or delete and recreate (be careful!)
git branch -D old-branch
git checkout -b old-branch
```

### Issue 4: "Diverged branches"

**Problem**: Local and remote branches have different commits

**Solution**:
```bash
# Pull and merge
git pull origin branch-name

# Or pull with rebase
git pull --rebase origin branch-name
```

---

## 🎯 Quick Reference

### Documentation Branch Commands

```bash
git checkout claude/LVL-CODES-MAIN-UgMj2
cat README.md
cat BRANCH_GUIDE.md
```

### Development Branch Commands

```bash
git checkout claude/LVL-STMS-UgMj2
cd LVL-STMS/
cat README.md
cat DEPLOYMENT_GUIDE.md
```

### Branch Management

```bash
# List branches
git branch -a

# Create branch
git checkout -b new-branch

# Delete branch
git branch -d branch-name

# Rename current branch
git branch -m new-name

# Update from remote
git pull origin branch-name
```

---

## 📞 Need Help?

- **Git Issues**: Check Git documentation or create GitHub issue
- **Project Questions**: See project-specific README files
- **Repository Structure**: Read main README.md
- **Setup Help**: Check DEPLOYMENT_GUIDE.md in project directory

---

## 🔗 Useful Links

- **Repository**: https://github.com/banddanalytics/LVL-CODES
- **LVL-STMS Branch**: https://github.com/banddanalytics/LVL-CODES/tree/claude/LVL-STMS-UgMj2
- **Documentation Branch**: https://github.com/banddanalytics/LVL-CODES/tree/claude/LVL-CODES-MAIN-UgMj2

---

**Last Updated**: 2025-12-17
**Maintained By**: LVL-CODES Analytics Team
